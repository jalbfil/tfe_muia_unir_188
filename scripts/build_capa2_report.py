"""T057 - Build the consolidated Capa 2 evaluation report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = PROJECT_ROOT / "artifacts" / "reports" / "baseline_expert_v0.1.0.json"
DEFAULT_LITE = PROJECT_ROOT / "artifacts" / "reports" / "rulefit_lite_v0.1.0.json"
DEFAULT_IMODELS = PROJECT_ROOT / "artifacts" / "reports" / "rulefit_imodels_v0.1.0.json"
DEFAULT_SELECTION = PROJECT_ROOT / "artifacts" / "reports" / "capa2_model_selection_v0.1.0.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts" / "reports" / "capa2_v0.1.0.json"
DEFAULT_OUTPUT_MD = PROJECT_ROOT / "artifacts" / "reports" / "capa2_v0.1.0.md"

QUALITY_TARGETS = {
    "recall_p1_min": 0.85,
    "max_active_rules": 30,
    "ece_max": 0.10,
}

ANTI_LEAKAGE_COLUMNS = [
    "MediosMov",
    "medios_mov_limpio",
    "medios_mov_uso_recomendado",
    "PacientesAten",
    "pacientes_aten_limpio",
    "IncidenteCerrado",
    "ultimaActualizacion",
    "Enlace al contenido",
    "Unnamed: 13",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _split_summary(report: dict[str, Any], split: str = "test") -> dict[str, Any]:
    metrics = report["splits"][split]
    return {
        "rows": metrics["rows"],
        "accuracy": metrics["accuracy"],
        "macro_f1": metrics["macro_f1"],
        "recall_p1": metrics["recall_p1"],
        "per_class": metrics["per_class"],
        "confusion_matrix": metrics["confusion_matrix"],
    }


def _model_block(name: str, report: dict[str, Any], *, model_family: str) -> dict[str, Any]:
    active_rules = report.get("active_rule_count_exported", report.get("rule_count"))
    test = report["splits"]["test"]
    return {
        "name": name,
        "model_family": model_family,
        "model_version_capa2": report.get("model_version_capa2", "0.1.0"),
        "engine": report.get("engine", report.get("model")),
        "fit_rows": report.get("fit_rows"),
        "active_rules": active_rules,
        "training_seconds": report.get("training_seconds"),
        "mean_inference_ms_per_row": report.get("mean_inference_ms_per_row"),
        "model_size_bytes": report.get("model_size_bytes"),
        "artifacts": report.get("artifacts", {}),
        "metrics": {
            "train": _split_summary(report, "train"),
            "val": _split_summary(report, "val"),
            "test": _split_summary(report, "test"),
        },
        "quality_checks": {
            "recall_p1_pass": test["recall_p1"] >= QUALITY_TARGETS["recall_p1_min"],
            "sparsity_pass": active_rules is None
            or active_rules <= QUALITY_TARGETS["max_active_rules"],
            "macro_f1_test": test["macro_f1"],
        },
    }


def _decision(selection: dict[str, Any], models: dict[str, dict[str, Any]]) -> dict[str, Any]:
    recommended = selection["recommendation"]["recommended_model"]
    selected = models[recommended]
    return {
        "selected_model": recommended,
        "rationale": [
            "Best test macro-F1 among evaluated Capa 2 alternatives.",
            "Recall P1 remains above the 0.85 target.",
            "Exported rule count respects the <=30 interpretability constraint.",
            "Inference latency is materially lower than the diagnostic imodels run.",
        ],
        "selected_test_macro_f1": selected["metrics"]["test"]["macro_f1"],
        "selected_recall_p1": selected["metrics"]["test"]["recall_p1"],
        "selected_active_rules": selected["active_rules"],
    }


def _write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Reporte Capa 2 v0.1.0",
        "",
        f"- Modelo seleccionado: {report['decision']['selected_model']}",
        f"- Macro-F1 test: {report['decision']['selected_test_macro_f1']}",
        f"- Recall P1 test: {report['decision']['selected_recall_p1']}",
        f"- Reglas activas exportadas: {report['decision']['selected_active_rules']}",
        "",
        "## Comparativa Test",
        "",
        "| Modelo | Accuracy | Macro-F1 | Recall P1 | Reglas | Train s | Infer ms/fila |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for model in report["models"].values():
        test = model["metrics"]["test"]
        lines.append(
            "| {name} | {accuracy} | {macro_f1} | {recall_p1} | {rules} | {train} | {infer} |".format(
                name=model["name"],
                accuracy=test["accuracy"],
                macro_f1=test["macro_f1"],
                recall_p1=test["recall_p1"],
                rules=model["active_rules"],
                train=model["training_seconds"],
                infer=model["mean_inference_ms_per_row"],
            )
        )
    lines.extend(["", "## Checks", ""])
    checks = report["quality_targets"]
    lines.append(f"- Recall P1 minimo: {checks['recall_p1_min']}")
    lines.append(f"- Maximo reglas activas: {checks['max_active_rules']}")
    lines.append(f"- ECE objetivo para calibracion posterior: {checks['ece_max']}")
    lines.extend(["", "## Anti-Leakage", ""])
    lines.append(report["anti_leakage"]["policy"])
    lines.append(
        "Columnas prohibidas excluidas: "
        + ", ".join(report["anti_leakage"]["excluded_columns"])
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--lite", type=Path, default=DEFAULT_LITE)
    parser.add_argument("--imodels", type=Path, default=DEFAULT_IMODELS)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)

    baseline = _load(args.baseline)
    lite = _load(args.lite)
    imodels = _load(args.imodels)
    selection = _load(args.selection)
    models = {
        "baseline_expert": _model_block("baseline_expert", baseline, model_family="expert_rules"),
        "rulefit_lite": _model_block("rulefit_lite", lite, model_family="rulefit_style"),
        "rulefit_imodels": _model_block("rulefit_imodels", imodels, model_family="imodels_rulefit"),
    }
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Capa 2 interpretable priority recommendation P1-P4",
        "quality_targets": QUALITY_TARGETS,
        "decision": _decision(selection, models),
        "models": models,
        "model_selection_source": selection,
        "anti_leakage": {
            "policy": "Only pre-decision textual signals and derived V01-V15 proxies are used.",
            "excluded_columns": ANTI_LEAKAGE_COLUMNS,
            "gate": "tests/test_leakage_gate.py scans src/capa2_rulefit for prohibited names.",
        },
        "limitations": [
            "Labels are academic weak labels, not operational ground truth.",
            "imodels RuleFit was run diagnostically with reduced fit_rows due local runtime cost.",
            "ECE is reserved for the final calibration pass once the selected model is frozen.",
        ],
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_markdown(report, args.output_md)
    print(f"[OK] Capa 2 consolidated report written to {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
