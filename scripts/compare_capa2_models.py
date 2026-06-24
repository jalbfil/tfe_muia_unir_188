"""Build a model-selection report for Capa 2 alternatives."""

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
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts" / "reports" / "capa2_model_selection_v0.1.0.json"
DEFAULT_OUTPUT_MD = PROJECT_ROOT / "artifacts" / "reports" / "capa2_model_selection_v0.1.0.md"


def _load_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _baseline_row(report: dict[str, Any]) -> dict[str, Any]:
    val = report["splits"]["val"]
    test = report["splits"]["test"]
    return {
        "model": "baseline_expert",
        "available": True,
        "validation_accuracy": val["accuracy"],
        "validation_macro_f1": val["macro_f1"],
        "validation_recall_p1": val["recall_p1"],
        "test_accuracy": test["accuracy"],
        "test_macro_f1": test["macro_f1"],
        "test_recall_p1": test["recall_p1"],
        "active_rules": report.get("rule_count"),
        "training_seconds": None,
        "mean_inference_ms_per_row": None,
        "model_size_bytes": None,
    }


def _rulefit_row(name: str, report: dict[str, Any] | None) -> dict[str, Any]:
    if report is None:
        return {
            "model": name,
            "available": False,
            "reason": "report_not_found",
        }
    val = report["splits"]["val"]
    test = report["splits"]["test"]
    return {
        "model": name,
        "available": True,
        "engine": report.get("engine"),
        "fit_rows": report.get("fit_rows"),
        "validation_accuracy": val["accuracy"],
        "validation_macro_f1": val["macro_f1"],
        "validation_recall_p1": val["recall_p1"],
        "test_accuracy": test["accuracy"],
        "test_macro_f1": test["macro_f1"],
        "test_recall_p1": test["recall_p1"],
        "active_rules": report.get("active_rule_count_exported"),
        "training_seconds": report.get("training_seconds"),
        "mean_inference_ms_per_row": report.get("mean_inference_ms_per_row"),
        "model_size_bytes": report.get("model_size_bytes"),
    }


def _recommend(rows: list[dict[str, Any]]) -> dict[str, Any]:
    available = [row for row in rows if row.get("available")]
    ranked = sorted(
        available,
        key=lambda row: (
            float(row.get("validation_macro_f1") or 0.0),
            float(row.get("validation_recall_p1") or 0.0),
            -float(row.get("active_rules") or 9999),
        ),
        reverse=True,
    )
    winner = ranked[0] if ranked else None
    return {
        "recommended_model": winner["model"] if winner else None,
        "criterion": (
            "Maximize validation macro-F1, keep high validation P1 recall, "
            "prefer fewer rules on ties. Test is reserved for final estimation."
        ),
    }


def _write_md(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Seleccion de modelo Capa 2",
        "",
        f"- Generado: {report['generated_at']}",
        f"- Modelo recomendado: {report['recommendation']['recommended_model']}",
        "",
        "## Comparativa",
        "",
        "| Modelo | Disponible | Accuracy val | Macro-F1 val | Recall P1 val | Reglas | Train s | Infer ms/fila |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["models"]:
        lines.append(
            "| {model} | {available} | {accuracy} | {macro_f1} | {recall_p1} | {rules} | {train} | {infer} |".format(
                model=row["model"],
                available=row.get("available"),
                accuracy=row.get("validation_accuracy", ""),
                macro_f1=row.get("validation_macro_f1", ""),
                recall_p1=row.get("validation_recall_p1", ""),
                rules=row.get("active_rules", ""),
                train=row.get("training_seconds", ""),
                infer=row.get("mean_inference_ms_per_row", ""),
            )
        )
    lines.extend(["", "## Lectura", ""])
    lines.append(
        "La seleccion prioriza macro-F1 y recall P1 en validacion, junto con la parsimonia. "
        "El conjunto de test se reserva para estimar el rendimiento final del modelo seleccionado. "
        "El motor imodels se ha ejecutado en entorno Python 3.12 aislado; si se "
        "incrementan filas/arboles, debe repetirse el reporte con los mismos splits."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--lite", type=Path, default=DEFAULT_LITE)
    parser.add_argument("--imodels", type=Path, default=DEFAULT_IMODELS)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)

    baseline = _load_optional(args.baseline)
    rows = []
    if baseline is not None:
        rows.append(_baseline_row(baseline))
    rows.append(_rulefit_row("rulefit_lite", _load_optional(args.lite)))
    rows.append(_rulefit_row("rulefit_imodels", _load_optional(args.imodels)))
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "models": rows,
        "recommendation": _recommend(rows),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_md(report, args.output_md)
    print(f"[OK] Model-selection report written to {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
