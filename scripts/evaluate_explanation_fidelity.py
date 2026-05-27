"""T113 - Offline fidelity evaluation for Capa 3 explanations.

The script uses the internal-validation sample as the evaluation base. It builds a
PriorityRecommendation from each row, obtains a Capa 3 explanation in degraded/static
mode and applies a deterministic judge rubric.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
CONTRACTS_ROOT = SRC_ROOT / "contracts"
sys.path.insert(0, str(CONTRACTS_ROOT))
sys.path.insert(0, str(SRC_ROOT))

import pandas as pd  # noqa: E402

from capa3_llm_mcp.degraded import degraded_explain  # noqa: E402
from contracts import (  # noqa: E402
    ActivatedRule,
    ConfidenceLevel,
    ModelUsed,
    NormaID,
    Priority,
    PriorityRecommendation,
)

DEFAULT_SAMPLE = PROJECT_ROOT / "resources" / "internal_validation" / "casos_revision_v0.1.0.csv"
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "artifacts" / "reports" / "explanation_fidelity_v0.1.0.json"
DEFAULT_OUTPUT_MD = PROJECT_ROOT / "artifacts" / "reports" / "explanation_fidelity_v0.1.0.md"
DEFAULT_CASES_CSV = PROJECT_ROOT / "artifacts" / "reports" / "explanation_fidelity_cases_v0.1.0.csv"
LABELS = ["P1", "P2", "P3", "P4"]
SIGNAL_KEYWORDS = {
    "signal_fallecido": ("fallecid", "muert"),
    "signal_herido_grave": ("herido", "grave", "inconsciente"),
    "signal_atrapado": ("atrapad",),
    "signal_intoxicacion": ("intoxic", "humo", "inhal"),
    "signal_varias_llamadas": ("varias", "llamadas", "alertantes"),
    "signal_incendio": ("incendio", "humo", "arder"),
    "signal_accidente_trafico": ("trafico", "colision", "vehiculo", "carretera"),
    "signal_rescate": ("rescate", "atrapad", "salvamento"),
    "signal_meteo_inundacion": ("inund", "meteo", "lluvia"),
    "riesgo_vital_textual": ("riesgo vital", "maxima urgencia", "p1"),
}


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _confidence_level(max_probability: float) -> ConfidenceLevel:
    if max_probability >= 0.80:
        return ConfidenceLevel.HIGH
    if max_probability >= 0.60:
        return ConfidenceLevel.MEDIUM
    if max_probability >= 0.40:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.UNKNOWN


def _split_rule_texts(raw: str) -> list[str]:
    marker = "reglas_top_prediccion:"
    if marker not in raw:
        return []
    tail = raw.split(marker, 1)[1]
    return [part.strip() for part in tail.split("|") if part.strip()]


def _anchors_for_row(row: dict[str, Any]) -> list[NormaID]:
    category = str(row.get("categoria_operativa_preliminar", "")).lower()
    anchors = [NormaID.LEY_17_2015, NormaID.PLANCAL_DEC_4_2019]
    if "incendio" in category:
        anchors.append(NormaID.INFOCAL_DEC_6_2025)
    if "meteor" in category or "inund" in category:
        anchors.append(NormaID.INUNCYL)
    if "sanitario" in category:
        anchors.append(NormaID.RGPD)
    return anchors


def _activated_rules(row: dict[str, Any]) -> list[ActivatedRule]:
    rules = []
    texts = _split_rule_texts(str(row.get("reglas_o_senales_mostradas", "")))
    anchors = _anchors_for_row(row)
    for idx, text in enumerate(texts[:5], start=1):
        rules.append(
            ActivatedRule(
                rule_id=f"RF-{row['case_id']}-{idx:02d}",
                human_text=text[:200],
                weight=1.0 / idx,
                normative_anchors=anchors,
            )
        )
    if not rules and row["recomendacion_sistema"] in ("P1", "P2"):
        rules.append(
            ActivatedRule(
                rule_id=f"RF-{row['case_id']}-FALLBACK",
                human_text=str(row.get("reglas_o_senales_mostradas", ""))[:200]
                or "Senales textuales predecisionales compatibles con prioridad alta",
                weight=0.1,
                normative_anchors=anchors,
            )
        )
    return rules


def _priority_recommendation(row: dict[str, Any]) -> PriorityRecommendation:
    probabilities = {
        Priority.P1: float(row["prob_p1"]),
        Priority.P2: float(row["prob_p2"]),
        Priority.P3: float(row["prob_p3"]),
        Priority.P4: float(row["prob_p4"]),
    }
    total = sum(probabilities.values())
    if abs(total - 1.0) > 1e-6:
        probabilities = {priority: value / total for priority, value in probabilities.items()}
    pmax = max(probabilities.values())
    recommended = Priority(str(row["recomendacion_sistema"]))
    return PriorityRecommendation(
        incident_id=str(row["incident_id"]),
        priority_recommended=recommended,
        probabilities=probabilities,
        activated_rules=_activated_rules(row),
        confidence_level=_confidence_level(pmax),
        model_used=ModelUsed.RULEFIT,
        model_version_capa2="0.1.0",
        requires_human_attention=recommended in (Priority.P1, Priority.P2)
        or str(row["sample_type"]) == "critical_p1_false_negative",
    )


def _mentioned_priority(explanation: str, priority: str) -> bool:
    text = explanation.lower()
    aliases = {
        "P1": ("p1", "maxima urgencia", "máxima urgencia"),
        "P2": ("p2", "urgencia alta"),
        "P3": ("p3", "urgencia media"),
        "P4": ("p4", "prioridad baja"),
    }
    return any(alias in text for alias in aliases[priority])


def _signal_coverage(row: dict[str, Any], explanation: str, rules_summary: list[str]) -> float:
    signals_blob = str(row.get("reglas_o_senales_mostradas", ""))
    active_signals = [signal for signal in SIGNAL_KEYWORDS if signal in signals_blob]
    if not active_signals:
        return 1.0
    text = (explanation + " " + " ".join(rules_summary)).lower()
    hits = 0
    for signal in active_signals:
        if any(keyword in text for keyword in SIGNAL_KEYWORDS[signal]):
            hits += 1
    return hits / len(active_signals)


def _has_priority_contradiction(explanation: str, expected: str) -> bool:
    text = explanation.lower()
    mentioned = {label for label in LABELS if _mentioned_priority(text, label)}
    return bool(mentioned - {expected})


def _judge(row: dict[str, Any], rec: Any) -> dict[str, Any]:
    expected_priority = str(row["recomendacion_sistema"])
    priority_ok = _mentioned_priority(rec.explanation_text, expected_priority)
    rules_ok = bool(rec.activated_rules_summary) or expected_priority in ("P3", "P4")
    signal_score = _signal_coverage(row, rec.explanation_text, rec.activated_rules_summary)
    citations_ok = expected_priority not in ("P1", "P2") or len(rec.legal_citations) >= 1
    no_contradiction = not _has_priority_contradiction(rec.explanation_text, expected_priority)
    disclaimer_ok = bool(rec.confidence_disclaimer)

    points = {
        "priority_alignment": 2.0 if priority_ok else 0.0,
        "rule_traceability": 2.0 if rules_ok else 0.0,
        "signal_coverage": 2.0 * signal_score,
        "legal_traceability": 2.0 if citations_ok else 0.0,
        "no_contradiction": 1.0 if no_contradiction else 0.0,
        "confidence_disclaimer": 1.0 if disclaimer_ok else 0.0,
    }
    score = round(sum(points.values()) / 10.0, 6)
    failed = [key for key, value in points.items() if value <= 0.0]
    return {
        "fidelity_score": score,
        "passed": score >= 0.80 and priority_ok and citations_ok and no_contradiction,
        "failed_checks": ";".join(failed),
        **{key: round(value, 6) for key, value in points.items()},
    }


def _write_cases(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [float(row["fidelity_score"]) for row in rows]
    passed = sum(bool(row["passed"]) for row in rows)
    by_type = {}
    for sample_type in sorted({str(row["sample_type"]) for row in rows}):
        subset = [row for row in rows if row["sample_type"] == sample_type]
        by_type[sample_type] = {
            "rows": len(subset),
            "pass_rate": round(sum(bool(row["passed"]) for row in subset) / len(subset), 6),
            "mean_fidelity": round(sum(float(row["fidelity_score"]) for row in subset) / len(subset), 6),
        }
    return {
        "rows": len(rows),
        "passed": passed,
        "pass_rate": round(passed / len(rows), 6),
        "mean_fidelity": round(sum(scores) / len(scores), 6),
        "min_fidelity": round(min(scores), 6),
        "by_sample_type": by_type,
        "failed_checks": dict(Counter(check for row in rows for check in str(row["failed_checks"]).split(";") if check)),
    }


def _write_markdown(summary: dict[str, Any], report: dict[str, Any], path: Path) -> None:
    lines = [
        "# T113 - Evaluacion de fidelidad de explicaciones",
        "",
        f"Generado: `{report['generated_at']}`",
        "",
        "## Resultado global",
        "",
        f"- Casos evaluados: {summary['rows']}",
        f"- Pass rate: {summary['pass_rate']}",
        f"- Fidelidad media: {summary['mean_fidelity']}",
        f"- Fidelidad minima: {summary['min_fidelity']}",
        "",
        "## Por tipo de muestra",
        "",
        "| Tipo | Casos | Pass rate | Fidelidad media |",
        "|---|---:|---:|---:|",
    ]
    for sample_type, values in summary["by_sample_type"].items():
        lines.append(
            f"| {sample_type} | {values['rows']} | {values['pass_rate']} | {values['mean_fidelity']} |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "- priority_alignment: la explicacion menciona la prioridad recomendada por Capa 2.",
            "- rule_traceability: incluye resumen de reglas cuando procede.",
            "- signal_coverage: cubre las senales textuales principales.",
            "- legal_traceability: P1/P2 incluyen citas legales.",
            "- no_contradiction: no menciona otra prioridad incompatible.",
            "- confidence_disclaimer: comunica cautela o modo degradado.",
            "",
            "## Artefactos",
            "",
        ]
    )
    for name, artifact_path in report["artifacts"].items():
        lines.append(f"- {name}: `{artifact_path}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-csv", type=Path, default=DEFAULT_SAMPLE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--cases-csv", type=Path, default=DEFAULT_CASES_CSV)
    args = parser.parse_args(argv)

    sample = pd.read_csv(args.sample_csv)
    rows = []
    for source_row in sample.to_dict(orient="records"):
        priority_rec = _priority_recommendation(source_row)
        operator_rec = degraded_explain(priority_rec)
        judge = _judge(source_row, operator_rec)
        rows.append(
            {
                "case_id": source_row["case_id"],
                "sample_type": source_row["sample_type"],
                "incident_id": source_row["incident_id"],
                "weak_label_p1p4": source_row["weak_label_p1p4"],
                "priority_recommended": source_row["recomendacion_sistema"],
                "llm_model": operator_rec.llm_metadata.llm_model,
                "legal_citations": len(operator_rec.legal_citations),
                "activated_rules_summary": len(operator_rec.activated_rules_summary),
                "explanation_text": operator_rec.explanation_text,
                **judge,
            }
        )

    summary = _summarize(rows)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "T113 offline explanation fidelity over internal validation sample",
        "judge_mode": "deterministic_offline_proxy",
        "model_evaluated": "degraded-static-v0.1.0",
        "sample_csv": _rel(args.sample_csv),
        "summary": summary,
        "artifacts": {
            "json": _rel(args.output_json),
            "markdown": _rel(args.output_md),
            "cases_csv": _rel(args.cases_csv),
        },
        "limitations": [
            "This is a deterministic proxy judge, not an external LLM-as-Judge run.",
            "It verifies fidelity to Capa 2 outputs and rule evidence, not linguistic quality.",
            "A future run can replace the judge with an independent local LLM over the same cases.",
        ],
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_cases(rows, args.cases_csv)
    _write_markdown(summary, report, args.output_md)
    print(
        "[OK] Explanation fidelity evaluated "
        f"rows={summary['rows']} pass_rate={summary['pass_rate']} "
        f"mean={summary['mean_fidelity']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
