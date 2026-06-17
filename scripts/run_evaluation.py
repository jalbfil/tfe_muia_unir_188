"""T110-T112 - Evaluacion final de Capa 2, sesgo y errores P1.

El script consolida las metricas obligatorias del Capitulo 9:

* test estratificado y test temporal;
* desglose por provincia, ano y categoria;
* matriz de confusion y falsos negativos P1.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import joblib  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

DEFAULT_CLEAN = (
    PROJECT_ROOT
    / "resources"
    / "dataset"
    / "processed"
    / "emergencias_112_cyl_2008_2022_clean.csv"
)
DEFAULT_SPLIT_DIR = PROJECT_ROOT / "resources" / "dataset" / "splits"
DEFAULT_TEMPORAL_SPLIT_DIR = DEFAULT_SPLIT_DIR / "temporal"
DEFAULT_MODEL = PROJECT_ROOT / "artifacts" / "models" / "capa2" / "v0.1.0" / "rulefit_lite.joblib"
DEFAULT_REPORT_JSON = PROJECT_ROOT / "artifacts" / "reports" / "evaluation_v0.1.0.json"
DEFAULT_REPORT_MD = PROJECT_ROOT / "artifacts" / "reports" / "evaluation_v0.1.0.md"
LABELS = ["P1", "P2", "P3", "P4"]
PRIORITY_ORDER = {label: idx for idx, label in enumerate(LABELS)}


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _load_joined(split_dir: Path, clean_csv: Path, split_name: str) -> pd.DataFrame:
    split = pd.read_csv(split_dir / f"{split_name}.csv")
    clean = pd.read_csv(clean_csv).rename(columns={"Identificador": "incident_id"})
    split["incident_id"] = split["incident_id"].astype(str)
    clean["incident_id"] = clean["incident_id"].astype(str)
    joined = split.merge(clean, on="incident_id", how="left", suffixes=("", "_clean"))
    if joined["FechaIncidente"].isna().any():
        missing = int(joined["FechaIncidente"].isna().sum())
        raise RuntimeError(f"{missing} split rows could not be joined with the clean dataset")
    return joined


def _predict_frame(model: Any, frame: pd.DataFrame) -> pd.DataFrame:
    records = []
    for row in frame.to_dict(orient="records"):
        probabilities = model.predict_proba_from_row(row)
        predicted = max(probabilities, key=probabilities.get)
        records.append(
            {
                "prediction": predicted,
                "confidence": round(float(probabilities[predicted]), 6),
                **{f"proba_{label.lower()}": float(probabilities[label]) for label in LABELS},
            }
        )
    return pd.concat([frame.reset_index(drop=True), pd.DataFrame(records)], axis=1)


def _metrics(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=LABELS,
        zero_division=0,
    )
    cm = confusion_matrix(y_true, y_pred, labels=LABELS)
    per_class = {
        label: {
            "precision": round(float(precision[idx]), 6),
            "recall": round(float(recall[idx]), 6),
            "f1": round(float(f1[idx]), 6),
            "support": int(support[idx]),
        }
        for idx, label in enumerate(LABELS)
    }
    return {
        "rows": int(len(y_true)),
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 6),
        "macro_f1": round(float(f1_score(y_true, y_pred, labels=LABELS, average="macro")), 6),
        "recall_p1": per_class["P1"]["recall"],
        "per_class": per_class,
        "confusion_matrix": {
            label: {pred: int(cm[i, j]) for j, pred in enumerate(LABELS)}
            for i, label in enumerate(LABELS)
        },
    }


def _evaluate_frame(frame: pd.DataFrame) -> dict[str, Any]:
    return _metrics(frame["final_label"].astype(str).tolist(), frame["prediction"].astype(str).tolist())


def _write_group_report(
    frame: pd.DataFrame,
    group_column: str,
    path: Path,
    min_rows: int = 15,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group_value, group in frame.groupby(group_column, dropna=False):
        if len(group) < min_rows:
            continue
        metrics = _evaluate_frame(group)
        row = {
            "group": str(group_value),
            "rows": metrics["rows"],
            "accuracy": metrics["accuracy"],
            "macro_f1": metrics["macro_f1"],
            "recall_p1": metrics["recall_p1"],
            **{f"support_{label.lower()}": metrics["per_class"][label]["support"] for label in LABELS},
        }
        rows.append(row)
    rows.sort(key=lambda item: (float(item["macro_f1"]), -int(item["rows"])))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["group", "rows"])
        writer.writeheader()
        writer.writerows(rows)
    return rows


def _severity_gap(reference: str, prediction: str) -> int:
    return PRIORITY_ORDER[prediction] - PRIORITY_ORDER[reference]


def _write_p1_errors(frame: pd.DataFrame, path: Path) -> list[dict[str, Any]]:
    errors = frame[(frame["final_label"] == "P1") & (frame["prediction"] != "P1")].copy()
    rows: list[dict[str, Any]] = []
    for row in errors.to_dict(orient="records"):
        rows.append(
            {
                "incident_id": row["incident_id"],
                "fecha_incidente": row["fecha_incidente"],
                "anio": row["anio"],
                "provincia_inferida": row["provincia_inferida"],
                "categoria_operativa_preliminar": row["categoria_operativa_preliminar"],
                "reference": row["final_label"],
                "prediction": row["prediction"],
                "severity_gap": _severity_gap(row["final_label"], row["prediction"]),
                "confidence": row["confidence"],
                "agreement_score": row["agreement_score"],
                "texto_operativo": str(row.get("texto_operativo", ""))[:350],
            }
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "incident_id",
        "fecha_incidente",
        "anio",
        "provincia_inferida",
        "categoria_operativa_preliminar",
        "reference",
        "prediction",
        "severity_gap",
        "confidence",
        "agreement_score",
        "texto_operativo",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def _critical_error_counts(frame: pd.DataFrame) -> dict[str, int]:
    p1_errors = frame[(frame["final_label"] == "P1") & (frame["prediction"] != "P1")]
    return {
        "p1_false_negatives": int(len(p1_errors)),
        "p1_to_p2": int(((p1_errors["prediction"]) == "P2").sum()),
        "p1_to_p3": int(((p1_errors["prediction"]) == "P3").sum()),
        "p1_to_p4": int(((p1_errors["prediction"]) == "P4").sum()),
    }


def _write_bar_svg(rows: list[dict[str, Any]], path: Path, title: str) -> None:
    selected = sorted(rows, key=lambda item: item["macro_f1"])[:10]
    width = 900
    row_height = 34
    height = 90 + max(1, len(selected)) * row_height
    label_width = 170
    bar_width = 620
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="24" y="34" font-family="Arial" font-size="20" font-weight="700">{title}</text>',
        '<text x="24" y="58" font-family="Arial" font-size="12" fill="#555">Grupos con menor macro-F1 en test estratificado</text>',
    ]
    for idx, row in enumerate(selected):
        y = 82 + idx * row_height
        score = float(row["macro_f1"])
        bar = int(bar_width * score)
        label = str(row["group"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines.extend(
            [
                f'<text x="24" y="{y + 18}" font-family="Arial" font-size="13">{label}</text>',
                f'<rect x="{label_width}" y="{y}" width="{bar_width}" height="20" fill="#eef2f7"/>',
                f'<rect x="{label_width}" y="{y}" width="{bar}" height="20" fill="#4f46e5"/>',
                (
                    f'<text x="{label_width + bar_width + 12}" y="{y + 15}" '
                    f'font-family="Arial" font-size="12">{score:.3f}</text>'
                ),
            ]
        )
    lines.append("</svg>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_confusion_svg(metrics: dict[str, Any], path: Path) -> None:
    cell = 72
    left = 130
    top = 86
    width = left + cell * 4 + 36
    height = top + cell * 4 + 36
    max_value = max(
        max(row.values()) for row in metrics["confusion_matrix"].values()
    )
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="24" y="34" font-family="Arial" font-size="20" font-weight="700">Matriz de confusion RuleFit-lite</text>',
        '<text x="24" y="58" font-family="Arial" font-size="12" fill="#555">Test estratificado, referencia en filas y prediccion en columnas</text>',
    ]
    for idx, label in enumerate(LABELS):
        lines.append(f'<text x="{left + idx * cell + 25}" y="78" font-family="Arial" font-size="13">{label}</text>')
        lines.append(f'<text x="86" y="{top + idx * cell + 42}" font-family="Arial" font-size="13">{label}</text>')
    for row_idx, reference in enumerate(LABELS):
        for col_idx, prediction in enumerate(LABELS):
            value = metrics["confusion_matrix"][reference][prediction]
            opacity = 0.12 + 0.78 * (value / max_value if max_value else 0)
            x = left + col_idx * cell
            y = top + row_idx * cell
            lines.extend(
                [
                    f'<rect x="{x}" y="{y}" width="{cell - 4}" height="{cell - 4}" fill="#2563eb" opacity="{opacity:.3f}"/>',
                    f'<text x="{x + 26}" y="{y + 40}" font-family="Arial" font-size="15" fill="#111">{value}</text>',
                ]
            )
    lines.append("</svg>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _format_cm(metrics: dict[str, Any]) -> str:
    lines = ["| Referencia / Prediccion | P1 | P2 | P3 | P4 |", "|---|---:|---:|---:|---:|"]
    for label in LABELS:
        row = metrics["confusion_matrix"][label]
        lines.append(f"| {label} | {row['P1']} | {row['P2']} | {row['P3']} | {row['P4']} |")
    return "\n".join(lines)


def _write_markdown(report: dict[str, Any], path: Path) -> None:
    stratified = report["evaluation"]["stratified_test"]
    temporal = report["evaluation"]["temporal_test"]
    critical = stratified["critical_errors"]
    lines = [
        "# Evaluación Capa 2 v0.1.0",
        "",
        f"Generado: `{report['generated_at']}`",
        "",
        "## Resumen",
        "",
        "| Split | Filas | Accuracy | Macro-F1 | Recall P1 |",
        "|---|---:|---:|---:|---:|",
        (
            f"| Test estratificado | {stratified['metrics']['rows']} | "
            f"{stratified['metrics']['accuracy']} | {stratified['metrics']['macro_f1']} | "
            f"{stratified['metrics']['recall_p1']} |"
        ),
        (
            f"| Test temporal | {temporal['metrics']['rows']} | "
            f"{temporal['metrics']['accuracy']} | {temporal['metrics']['macro_f1']} | "
            f"{temporal['metrics']['recall_p1']} |"
        ),
        "",
        "## Matriz de confusión test estratificado",
        "",
        _format_cm(stratified["metrics"]),
        "",
        "## Falsos negativos P1",
        "",
        (
            f"Total: {critical['p1_false_negatives']}; P1->P2: {critical['p1_to_p2']}; "
            f"P1->P3: {critical['p1_to_p3']}; P1->P4: {critical['p1_to_p4']}."
        ),
        "",
        "## Artefactos",
        "",
    ]
    for name, artifact_path in report["artifacts"].items():
        lines.append(f"- {name}: `{artifact_path}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean-csv", type=Path, default=DEFAULT_CLEAN)
    parser.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    parser.add_argument("--temporal-split-dir", type=Path, default=DEFAULT_TEMPORAL_SPLIT_DIR)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    args = parser.parse_args(argv)

    model = joblib.load(args.model_path)
    stratified_test = _predict_frame(model, _load_joined(args.split_dir, args.clean_csv, "test"))
    temporal_test = _predict_frame(model, _load_joined(args.temporal_split_dir, args.clean_csv, "test"))

    reports_dir = args.report_json.parent
    bias_province = reports_dir / "bias_by_province_v0.1.0.csv"
    bias_year = reports_dir / "bias_by_year_v0.1.0.csv"
    bias_category = reports_dir / "bias_by_category_v0.1.0.csv"
    p1_errors_csv = reports_dir / "p1_error_analysis_v0.1.0.csv"
    bias_province_svg = reports_dir / "bias_by_province_v0.1.0.svg"
    bias_year_svg = reports_dir / "bias_by_year_v0.1.0.svg"
    bias_category_svg = reports_dir / "bias_by_category_v0.1.0.svg"
    confusion_svg = reports_dir / "confusion_matrix_rulefit_lite_v0.1.0.svg"

    group_reports = {
        "province": _write_group_report(stratified_test, "provincia_inferida", bias_province),
        "year": _write_group_report(stratified_test, "anio", bias_year),
        "category": _write_group_report(stratified_test, "categoria_operativa_preliminar", bias_category),
    }
    p1_errors = _write_p1_errors(stratified_test, p1_errors_csv)
    _write_bar_svg(group_reports["province"], bias_province_svg, "Macro-F1 por provincia")
    _write_bar_svg(group_reports["year"], bias_year_svg, "Macro-F1 por ano")
    _write_bar_svg(group_reports["category"], bias_category_svg, "Macro-F1 por categoria")
    stratified_metrics = _evaluate_frame(stratified_test)
    _write_confusion_svg(stratified_metrics, confusion_svg)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "T110-T112 final evaluation, bias analysis and P1 error review",
        "model_path": _rel(args.model_path),
        "evaluation": {
            "stratified_test": {
                "metrics": stratified_metrics,
                "critical_errors": _critical_error_counts(stratified_test),
            },
            "temporal_test": {
                "metrics": _evaluate_frame(temporal_test),
                "critical_errors": _critical_error_counts(temporal_test),
            },
        },
        "bias_analysis": group_reports,
        "p1_error_review": {
            "rows": len(p1_errors),
            "path": _rel(p1_errors_csv),
            "review_policy": (
                "Every P1 false negative must be reviewed by the internal panel before "
                "freezing Capa 2 v0.1.0."
            ),
        },
        "artifacts": {
            "json": _rel(args.report_json),
            "markdown": _rel(args.report_md),
            "bias_by_province": _rel(bias_province),
            "bias_by_year": _rel(bias_year),
            "bias_by_category": _rel(bias_category),
            "figure_bias_by_province": _rel(bias_province_svg),
            "figure_bias_by_year": _rel(bias_year_svg),
            "figure_bias_by_category": _rel(bias_category_svg),
            "figure_confusion_matrix": _rel(confusion_svg),
            "p1_error_analysis": _rel(p1_errors_csv),
        },
    }

    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_markdown(report, args.report_md)
    print(
        "[OK] Evaluation completed "
        f"test_macro_f1={report['evaluation']['stratified_test']['metrics']['macro_f1']} "
        f"temporal_macro_f1={report['evaluation']['temporal_test']['metrics']['macro_f1']} "
        f"p1_fn={report['evaluation']['stratified_test']['critical_errors']['p1_false_negatives']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
