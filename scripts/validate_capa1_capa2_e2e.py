"""Validate Capa 1 -> Capa 2 -> Capa 3 degraded integration.

This script is intentionally lightweight: it uses curated operational scenarios,
the deterministic Capa 1 extractor, the available Capa 2 predictor, and Capa 3
degraded explanations. It does not require or install the LLM.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))
sys.path.insert(0, str(SRC_ROOT / "contracts"))

from capa1_nlp.inference.feature_extractor import FeatureExtractor  # noqa: E402
from capa2_rulefit.inference.predictor import DEFAULT_RULEFIT_MODEL, predict  # noqa: E402
from capa3_llm_mcp.degraded import degraded_explain  # noqa: E402
from contracts import CategoriaPreliminar, IncidentInput, Priority, ProvinciaCyL  # noqa: E402

DEFAULT_CAPA1_REPORT = PROJECT_ROOT / "artifacts" / "reports" / "capa1_v0.1.0.json"
DEFAULT_E2E_JSON = PROJECT_ROOT / "artifacts" / "reports" / "capa1_capa2_e2e_v0.1.0.json"
DEFAULT_E2E_MD = PROJECT_ROOT / "artifacts" / "reports" / "capa1_capa2_e2e_v0.1.0.md"
DEFAULT_CAPA1_MODEL_META = (
    PROJECT_ROOT / "artifacts" / "models" / "capa1" / "v0.1.0" / "deterministic_extractor.json"
)

SIGNALS = [
    "signal_fallecido",
    "signal_herido_grave",
    "signal_atrapado",
    "signal_intoxicacion",
    "signal_varias_llamadas",
    "signal_incendio",
    "signal_accidente_trafico",
    "signal_rescate",
    "signal_meteo_inundacion",
    "riesgo_vital_textual",
]


@dataclass(frozen=True)
class Scenario:
    incident_id: str
    title: str
    description: str
    category: CategoriaPreliminar
    province: ProvinciaCyL
    expected_signals: dict[str, bool]
    acceptable_priorities: tuple[Priority, ...]
    rationale: str


SCENARIOS = [
    Scenario(
        incident_id="E2E-P1-ATRAPADO-INCENDIO",
        title="Incendio urbano con atrapados",
        description=(
            "Incendio en vivienda con humo denso. Varias llamadas indican que hay "
            "dos personas atrapadas en la planta superior y una no responde."
        ),
        category=CategoriaPreliminar.INCENDIO_URBANO,
        province=ProvinciaCyL.BURGOS,
        expected_signals={
            "signal_incendio": True,
            "signal_atrapado": True,
            "signal_varias_llamadas": True,
            "riesgo_vital_textual": True,
        },
        acceptable_priorities=(Priority.P1,),
        rationale="P1 esperado por incendio, atrapamiento, varias llamadas y riesgo vital textual.",
    ),
    Scenario(
        incident_id="E2E-P1-TRAFICO-INCONSCIENTE",
        title="Accidente de trafico grave",
        description=(
            "Choque frontal entre turismo y camion en autovia. Conductor inconsciente, "
            "posible atrapado y herido grave."
        ),
        category=CategoriaPreliminar.ACCIDENTE_TRAFICO,
        province=ProvinciaCyL.LEON,
        expected_signals={
            "signal_accidente_trafico": True,
            "signal_herido_grave": True,
            "signal_atrapado": True,
        },
        acceptable_priorities=(Priority.P1, Priority.P2),
        rationale="P1/P2 aceptable por accidente grave con inconsciencia y atrapamiento.",
    ),
    Scenario(
        incident_id="E2E-P1-QUIMICO-INTOXICACION",
        title="Fuga quimica en nave industrial",
        description=(
            "Aviso por fuga de gas y olor fuerte en nave. Hay trabajadores mareados "
            "por posible intoxicacion e inhalacion de humo, con dificultad respiratoria "
            "y riesgo vital."
        ),
        category=CategoriaPreliminar.QUIMICO_NRBQ,
        province=ProvinciaCyL.VALLADOLID,
        expected_signals={
            "signal_intoxicacion": True,
            "riesgo_vital_textual": True,
        },
        acceptable_priorities=(Priority.P1, Priority.P2),
        rationale="P1/P2 aceptable por riesgo quimico e intoxicacion.",
    ),
    Scenario(
        incident_id="E2E-P2-INUNDACION",
        title="Inundacion en garajes",
        description=(
            "Lluvia intensa provoca inundacion de varios garajes. No constan heridos, "
            "pero hay agua acumulada y acceso complicado."
        ),
        category=CategoriaPreliminar.METEOROLOGIA,
        province=ProvinciaCyL.SALAMANCA,
        expected_signals={
            "signal_meteo_inundacion": True,
            "signal_herido_grave": False,
        },
        acceptable_priorities=(Priority.P2, Priority.P3, Priority.P4),
        rationale="No hay victimas; se acepta prioridad no P1, con seguimiento operativo.",
    ),
    Scenario(
        incident_id="E2E-P3-INCIDENCIA-VIA",
        title="Arbol caido en carretera secundaria",
        description=(
            "Arbol caido ocupa parcialmente un carril. No hay heridos ni vehiculos "
            "atrapados. Trafico lento en la zona."
        ),
        category=CategoriaPreliminar.INCIDENCIA_VIA,
        province=ProvinciaCyL.SORIA,
        expected_signals={
            "signal_accidente_trafico": True,
            "signal_herido_grave": False,
            "signal_atrapado": False,
        },
        acceptable_priorities=(Priority.P3, Priority.P4),
        rationale="Incidencia ordinaria sin victimas; P3/P4 es coherente.",
    ),
]


def _build_input(scenario: Scenario) -> IncidentInput:
    return IncidentInput(
        incident_id=scenario.incident_id,
        texto_titulo=scenario.title,
        texto_descripcion=scenario.description,
        categoria_preliminar=scenario.category,
        provincia=scenario.province,
        localidad=scenario.province.value.title(),
        fecha_incidente=datetime.now(UTC),
        operador_id="E2E_VALIDATION",
    )


def _signal_value(features: Any, signal_name: str) -> bool:
    return bool(getattr(features, signal_name).value)


def _signal_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    total_tp = total_fp = total_fn = 0
    for signal in SIGNALS:
        tp = fp = fn = tn = 0
        for row in rows:
            expected = bool(row["expected_signals_complete"][signal])
            observed = bool(row["observed_signals"][signal])
            if expected and observed:
                tp += 1
            elif not expected and observed:
                fp += 1
            elif expected and not observed:
                fn += 1
            else:
                tn += 1
        precision = tp / (tp + fp) if tp + fp else 1.0
        recall = tp / (tp + fn) if tp + fn else 1.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        metrics[signal] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1": round(f1, 6),
        }
        total_tp += tp
        total_fp += fp
        total_fn += fn
    micro_precision = total_tp / (total_tp + total_fp) if total_tp + total_fp else 1.0
    micro_recall = total_tp / (total_tp + total_fn) if total_tp + total_fn else 1.0
    micro_f1 = (
        2 * micro_precision * micro_recall / (micro_precision + micro_recall)
        if micro_precision + micro_recall
        else 0.0
    )
    return {
        "signals": metrics,
        "micro": {
            "precision": round(micro_precision, 6),
            "recall": round(micro_recall, 6),
            "f1": round(micro_f1, 6),
        },
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Validacion end-to-end Capa 1 -> Capa 2 -> Capa 3 degradada v0.1.0",
        "",
        f"- Generado: `{payload['generated_at']}`",
        f"- Casos: `{payload['summary']['cases']}`",
        f"- Casos OK: `{payload['summary']['passed_cases']}`",
        f"- Capa 2 usa RuleFit: `{payload['environment']['rulefit_model_available']}`",
        f"- Modelo Capa 2 observado: `{payload['summary']['capa2_models_used']}`",
        f"- Latencia media Capa 1 ms: `{payload['summary']['mean_capa1_latency_ms']}`",
        f"- Latencia media Capa 2 ms: `{payload['summary']['mean_capa2_latency_ms']}`",
        "",
        "| Caso | Prioridad | Modelo C2 | OK | Senales clave |",
        "|---|---:|---|---:|---|",
    ]
    for row in payload["cases"]:
        observed = [
            name
            for name, value in row["observed_signals"].items()
            if value and name in row["expected_signals_subset"]
        ]
        lines.append(
            "| "
            + " | ".join(
                [
                    row["incident_id"],
                    row["priority_recommended"],
                    row["model_used_capa2"],
                    "si" if row["passed"] else "no",
                    ", ".join(observed) or "-",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Interpretacion",
            "",
            "Esta prueba no sustituye la evaluacion offline de Capa 2 sobre el dataset completo. "
            "Su objetivo es comprobar que la salida real de Capa 1 alimenta correctamente el "
            "motor de priorizacion y que la explicacion degradada de Capa 3 conserva la "
            "trazabilidad minima sin instalar el LLM.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_validation() -> dict[str, Any]:
    extractor = FeatureExtractor()
    rows: list[dict[str, Any]] = []

    for scenario in SCENARIOS:
        incident = _build_input(scenario)

        t0 = time.perf_counter()
        features = extractor.extract_features(incident)
        capa1_ms = (time.perf_counter() - t0) * 1000

        t1 = time.perf_counter()
        recommendation = predict(features)
        capa2_ms = (time.perf_counter() - t1) * 1000

        t2 = time.perf_counter()
        operator_recommendation = degraded_explain(recommendation)
        capa3_ms = (time.perf_counter() - t2) * 1000

        expected_complete = {signal: False for signal in SIGNALS}
        expected_complete.update(scenario.expected_signals)
        observed = {signal: _signal_value(features, signal) for signal in SIGNALS}
        signals_ok = all(
            observed[signal] == expected for signal, expected in scenario.expected_signals.items()
        )
        priority_ok = recommendation.priority_recommended in scenario.acceptable_priorities

        rows.append(
            {
                "incident_id": scenario.incident_id,
                "title": scenario.title,
                "category": scenario.category.value,
                "province": scenario.province.value,
                "rationale": scenario.rationale,
                "expected_signals_subset": scenario.expected_signals,
                "expected_signals_complete": expected_complete,
                "observed_signals": observed,
                "signals_ok": signals_ok,
                "acceptable_priorities": [priority.value for priority in scenario.acceptable_priorities],
                "priority_recommended": recommendation.priority_recommended.value,
                "priority_ok": priority_ok,
                "probabilities": {key.value: value for key, value in recommendation.probabilities.items()},
                "confidence_level": recommendation.confidence_level.value,
                "model_used_capa2": recommendation.model_used.value,
                "activated_rules_count": len(recommendation.activated_rules),
                "capa3_model": operator_recommendation.llm_metadata.llm_model,
                "capa3_citations": len(operator_recommendation.legal_citations),
                "explanation_excerpt": operator_recommendation.explanation_text[:240],
                "latency_ms": {
                    "capa1": round(capa1_ms, 6),
                    "capa2": round(capa2_ms, 6),
                    "capa3_degraded": round(capa3_ms, 6),
                },
                "passed": bool(signals_ok and priority_ok),
            }
        )

    capa2_models = sorted({row["model_used_capa2"] for row in rows})
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "scope": "T040-T049/T091 compatibility validation without LLM installation",
        "environment": {
            "python_version": sys.version,
            "rulefit_model_path": str(DEFAULT_RULEFIT_MODEL.relative_to(PROJECT_ROOT)),
            "rulefit_model_available": DEFAULT_RULEFIT_MODEL.exists(),
            "llm_installed": False,
            "capa3_mode": "degraded-static-v0.1.0",
        },
        "summary": {
            "cases": len(rows),
            "passed_cases": sum(1 for row in rows if row["passed"]),
            "failed_cases": sum(1 for row in rows if not row["passed"]),
            "capa2_models_used": capa2_models,
            "mean_capa1_latency_ms": round(
                sum(row["latency_ms"]["capa1"] for row in rows) / len(rows), 6
            ),
            "mean_capa2_latency_ms": round(
                sum(row["latency_ms"]["capa2"] for row in rows) / len(rows), 6
            ),
            "mean_capa3_degraded_latency_ms": round(
                sum(row["latency_ms"]["capa3_degraded"] for row in rows) / len(rows), 6
            ),
        },
        "capa1_signal_metrics": _signal_metrics(rows),
        "cases": rows,
        "limitations": [
            "Curated smoke test, not a replacement for the full offline Capa 2 evaluation.",
            "Capa 1 v0.1.0 uses deterministic lexical rules; transformer training is out of scope for this version.",
            "Capa 3 runs in degraded mode because LLM installation is intentionally deferred.",
        ],
    }
    return payload


def write_capa1_report(payload: dict[str, Any], report_path: Path, model_meta_path: Path) -> None:
    report = {
        "generated_at": payload["generated_at"],
        "model_name": "capa1_deterministic_signal_extractor",
        "model_version_capa1": "0.1.0",
        "implementation": "src/capa1_nlp/inference/feature_extractor.py",
        "training_status": "deterministic_rules_transformer_out_of_scope_v0.1.0",
        "features_output_contract": "IncidentFeatures",
        "signals_evaluated": SIGNALS,
        "evaluation_base": {
            "source": "curated operational E2E scenarios",
            "cases": payload["summary"]["cases"],
        },
        "metrics": payload["capa1_signal_metrics"],
        "latency": {
            "mean_ms": payload["summary"]["mean_capa1_latency_ms"],
            "scenario_latencies_ms": [
                row["latency_ms"]["capa1"] for row in payload["cases"]
            ],
        },
        "artifacts": {
            "model_metadata": str(model_meta_path.relative_to(PROJECT_ROOT)),
            "e2e_report": str(DEFAULT_E2E_JSON.relative_to(PROJECT_ROOT)),
        },
        "limitations": [
            "No se entrena ni valida transformer en v0.1.0; queda como linea futura.",
            "Las metricas proceden de escenarios operativos curados, no de un gold set externo 112.",
            "Debe ampliarse con anotacion manual si se congela Capa 1 como modelo productivo.",
        ],
    }
    model_meta = {
        "model_name": report["model_name"],
        "model_version_capa1": report["model_version_capa1"],
        "type": "deterministic_regex_feature_extractor",
        "source_files": [
            "src/capa1_nlp/extraction/signal_extractor.py",
            "src/capa1_nlp/inference/feature_extractor.py",
        ],
        "llm_dependency": "none",
        "transformer_checkpoint": None,
        "created_at": payload["generated_at"],
    }
    _write_json(report_path, report)
    _write_json(model_meta_path, model_meta)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capa1-report", type=Path, default=DEFAULT_CAPA1_REPORT)
    parser.add_argument("--e2e-json", type=Path, default=DEFAULT_E2E_JSON)
    parser.add_argument("--e2e-md", type=Path, default=DEFAULT_E2E_MD)
    parser.add_argument("--capa1-model-meta", type=Path, default=DEFAULT_CAPA1_MODEL_META)
    args = parser.parse_args(argv)

    payload = run_validation()
    _write_json(args.e2e_json, payload)
    _write_markdown(args.e2e_md, payload)
    write_capa1_report(payload, args.capa1_report, args.capa1_model_meta)

    print(
        "[OK] Capa1->Capa2->Capa3 validation "
        f"passed={payload['summary']['passed_cases']}/{payload['summary']['cases']} "
        f"models={payload['summary']['capa2_models_used']} "
        f"rulefit_available={payload['environment']['rulefit_model_available']}"
    )
    return 0 if payload["summary"]["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
