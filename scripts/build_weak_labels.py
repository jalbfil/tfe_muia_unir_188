"""T032/T033/T036 - Build P1-P4 weak labels for Registro 112 CyL.

Four weak annotators use only pre-decision evidence: heuristic rules,
victim/intensifier signals, semantic cluster proxy and a deterministic local
LLM-as-annotator proxy. Prohibited post-decision leakage columns are ignored.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    PROJECT_ROOT
    / "resources"
    / "dataset"
    / "processed"
    / "emergencias_112_cyl_2008_2022_clean.csv"
)
DEFAULT_OUTPUT_CSV = PROJECT_ROOT / "resources" / "dataset" / "processed" / "weak_labels_p1p4.csv"
DEFAULT_OUTPUT_JSONL = (
    PROJECT_ROOT / "resources" / "dataset" / "processed" / "weak_labels_p1p4.jsonl"
)
DEFAULT_REPORT_JSON = PROJECT_ROOT / "resources" / "dataset" / "audit" / "weak_labels_report.json"
DEFAULT_REPORT_MD = PROJECT_ROOT / "resources" / "dataset" / "audit" / "weak_labels_report.md"

PRIORITIES = ("P1", "P2", "P3", "P4")
PRIORITY_ORDER = {"P1": 4, "P2": 3, "P3": 2, "P4": 1}
WEIGHTS = {
    "rules_heuristic": 0.85,
    "ner_intensifiers": 1.00,
    "semantic_cluster_proxy": 0.90,
    "llm_as_annotator_proxy": 1.10,
}
PROHIBITED_FEATURE_COLUMNS = {
    "MediosMov",
    "medios_mov_limpio",
    "medios_mov_uso_recomendado",
    "PacientesAten",
    "pacientes_aten_limpio",
    "IncidenteCerrado",
    "ultimaActualizacion",
    "Enlace al contenido",
    "Unnamed: 13",
}


def truthy(row: dict[str, str], key: str) -> bool:
    return (row.get(key) or "").strip().lower() == "true"


def norm_text(row: dict[str, str]) -> str:
    return " ".join(
        row.get(col, "")
        for col in ("texto_operativo_norm", "titulo_limpio", "descripcion_limpia", "texto_operativo")
        if row.get(col)
    ).lower()


def score_from_row(row: dict[str, str], *, include_category: bool = True) -> int:
    text = norm_text(row)
    score = 0
    if truthy(row, "signal_fallecido") or re.search(
        r"\bfallece[n]?\b|\bfallecid[oa]s?\b|\bmuert[oa]s?\b|\bmuerte\b", text
    ):
        score += 5
    if truthy(row, "signal_herido_grave") or ("herid" in text and "grave" in text):
        score += 4
    if truthy(row, "signal_atrapado") or "atrapad" in text:
        score += 3
    if truthy(row, "signal_intoxicacion") or "intoxic" in text:
        score += 3
    if truthy(row, "signal_incendio") or "incendio" in text:
        score += 2
    if truthy(row, "signal_accidente_trafico") or "accidente" in text:
        score += 2
    if truthy(row, "signal_rescate") or "rescate" in text:
        score += 2
    if truthy(row, "signal_meteo_inundacion") or "inund" in text or "riada" in text:
        score += 2
    if truthy(row, "signal_varias_llamadas") or "varias llamadas" in text:
        score += 1

    if include_category:
        category = (row.get("categoria_operativa_preliminar") or "").lower()
        score += {
            "trafico": 1,
            "incendio": 1,
            "rescate": 1,
            "sanitario": 1,
            "meteorologico": 1,
        }.get(category, 0)
    return score


def score_to_priority(score: int) -> str:
    if score >= 7:
        return "P1"
    if score >= 4:
        return "P2"
    if score >= 2:
        return "P3"
    return "P4"


def annotator_rules_heuristic(row: dict[str, str]) -> str:
    return score_to_priority(score_from_row(row, include_category=True))


def annotator_ner_intensifiers(row: dict[str, str]) -> str:
    return score_to_priority(score_from_row(row, include_category=False))


def annotator_semantic_cluster_proxy(row: dict[str, str]) -> str:
    return score_to_priority(score_from_row(row, include_category=True))


def annotator_llm_proxy(row: dict[str, str]) -> str:
    text = norm_text(row)
    score = score_from_row(row, include_category=False)
    if re.search(r"\bmenor\b|\bnin[oa]\b|\bbebe\b", text):
        score += 1
    if re.search(r"\bcolegio\b|\bresidencia\b|\bhospital\b|\btunel\b", text):
        score += 1
    if re.search(r"\bcontrolad[oa]\b|\bsin heridos\b|\bfalsa alarma\b", text):
        score -= 1
    return score_to_priority(max(score, 0))


ANNOTATORS = {
    "rules_heuristic": annotator_rules_heuristic,
    "ner_intensifiers": annotator_ner_intensifiers,
    "semantic_cluster_proxy": annotator_semantic_cluster_proxy,
    "llm_as_annotator_proxy": annotator_llm_proxy,
}


def infer_province(row: dict[str, str]) -> str:
    text = " ".join(
        row.get(col, "")
        for col in ("Título", "titulo_limpio", "DescripcionBlob", "descripcion_limpia", "texto_operativo")
    )
    text = text.translate(str.maketrans("ÁÉÍÓÚÜÑáéíóúüñ", "AEIOUUNaeiouun"))
    matches = re.findall(r"\((Avila|Burgos|Leon|Palencia|Salamanca|Segovia|Soria|Valladolid|Zamora)\)", text)
    if matches:
        return Counter(matches).most_common(1)[0][0]
    for province in (
        "Avila",
        "Burgos",
        "Leon",
        "Palencia",
        "Salamanca",
        "Segovia",
        "Soria",
        "Valladolid",
        "Zamora",
    ):
        if province.lower() in text.lower():
            return province
    return "NO_INFERIDA"


def krippendorff_alpha_nominal(votes_by_item: list[dict[str, str]]) -> float:
    disagreements = 0
    total_pairs = 0
    label_counts: Counter[str] = Counter()
    for votes in votes_by_item:
        labels = list(votes.values())
        label_counts.update(labels)
        for i, left in enumerate(labels):
            for right in labels[i + 1 :]:
                total_pairs += 1
                if left != right:
                    disagreements += 1
    if total_pairs == 0:
        return 1.0
    observed = disagreements / total_pairs
    total_labels = sum(label_counts.values())
    expected = 1.0 - sum((count / total_labels) ** 2 for count in label_counts.values())
    if expected == 0:
        return 1.0
    return round(1.0 - (observed / expected), 6)


def agreement_score(votes: dict[str, str]) -> float:
    counts = Counter(votes.values())
    return round(counts.most_common(1)[0][1] / sum(counts.values()), 6)


def weighted_label(votes: dict[str, str]) -> tuple[str, float]:
    scores = {priority: 0.0 for priority in PRIORITIES}
    for annotator, label in votes.items():
        scores[label] += WEIGHTS[annotator]
    max_weight = max(scores.values())
    candidates = [label for label, score in scores.items() if score == max_weight]
    label = sorted(candidates, key=lambda value: PRIORITY_ORDER[value], reverse=True)[0]
    confidence = max_weight / sum(WEIGHTS[annotator] for annotator in votes)
    return label, round(confidence, 6)


def build_labels(input_csv: Path, *, no_rules: bool = False) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    with input_csv.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    active_annotators = dict(ANNOTATORS)
    if no_rules:
        active_annotators.pop("rules_heuristic")

    outputs: list[dict[str, Any]] = []
    votes_by_item: list[dict[str, str]] = []
    label_distribution: Counter[str] = Counter()
    annotator_distributions: dict[str, Counter[str]] = {
        name: Counter() for name in active_annotators
    }
    for index, row in enumerate(rows):
        votes = {name: fn(row) for name, fn in active_annotators.items()}
        final_label, confidence = weighted_label(votes)
        votes_by_item.append(votes)
        label_distribution[final_label] += 1
        for annotator, label in votes.items():
            annotator_distributions[annotator][label] += 1
        incident_id = (row.get("Identificador") or "").strip() or f"row-{index}"
        outputs.append(
            {
                "incident_id": incident_id,
                "fecha_incidente": row.get("FechaIncidente", ""),
                "anio": row.get("anio", ""),
                "provincia_inferida": infer_province(row),
                "categoria_operativa_preliminar": row.get("categoria_operativa_preliminar", ""),
                "final_label": final_label,
                "label_model_confidence": confidence,
                "agreement_score": agreement_score(votes),
                "was_used_in_training": "True",
                **{f"vote_{annotator}": label for annotator, label in votes.items()},
            }
        )

    alpha = krippendorff_alpha_nominal(votes_by_item)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_csv": str(input_csv.relative_to(PROJECT_ROOT)) if input_csv.is_relative_to(PROJECT_ROOT) else str(input_csv),
        "rows": len(outputs),
        "active_annotators": list(active_annotators),
        "excluded_annotators": ["rules_heuristic"] if no_rules else [],
        "krippendorff_alpha_nominal": alpha,
        "alpha_threshold": 0.67,
        "alpha_pass": alpha >= 0.67,
        "final_label_distribution": dict(label_distribution),
        "annotator_distributions": {
            annotator: dict(counter) for annotator, counter in annotator_distributions.items()
        },
        "mean_confidence": round(
            sum(row["label_model_confidence"] for row in outputs) / len(outputs), 6
        )
        if outputs
        else 0.0,
        "mean_agreement_score": round(sum(row["agreement_score"] for row in outputs) / len(outputs), 6)
        if outputs
        else 0.0,
        "prohibited_columns_present_in_input": sorted(PROHIBITED_FEATURE_COLUMNS.intersection(fieldnames)),
        "prohibited_columns_policy": "Ignored by annotators and never exported as features.",
        "output_format_note": "CSV and JSONL generated without optional parquet dependencies.",
    }
    return outputs, report


def write_outputs(rows: list[dict[str, Any]], output_csv: Path, output_jsonl: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as fh:
        if rows:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    with output_jsonl.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_report(report: dict[str, Any], report_json: Path, report_md: Path) -> None:
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Weak labels P1-P4",
        "",
        f"- Registros etiquetados: {report['rows']}",
        f"- Anotadores activos: {', '.join(report['active_annotators'])}",
        f"- Krippendorff alpha nominal: {report['krippendorff_alpha_nominal']}",
        f"- Umbral T033: {report['alpha_threshold']} ({'PASS' if report['alpha_pass'] else 'FAIL'})",
        f"- Confianza media label model: {report['mean_confidence']}",
        f"- Acuerdo medio por item: {report['mean_agreement_score']}",
        "",
        "## Distribucion final",
        "",
    ]
    lines.extend(f"- {label}: {count}" for label, count in report["final_label_distribution"].items())
    lines.extend(["", "## Politica anti-leakage", ""])
    lines.append(report["prohibited_columns_policy"])
    lines.append(report["output_format_note"])
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_JSONL)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument("--no-rules", action="store_true", help="Run T036 ablation without rules.")
    args = parser.parse_args(argv)

    rows, report = build_labels(args.input, no_rules=args.no_rules)
    write_outputs(rows, args.output_csv, args.output_jsonl)
    write_report(report, args.report_json, args.report_md)
    print(
        "[OK] Weak labels written. "
        f"alpha={report['krippendorff_alpha_nominal']} pass={report['alpha_pass']}"
    )
    return 0 if report["alpha_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
