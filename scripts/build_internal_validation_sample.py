"""Build the internal human-review sample for T113/T114.

The sample contains:

* every P1 false negative from the stratified test split;
* a balanced P1-P4 supplement for human review.
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

DEFAULT_CLEAN = (
    PROJECT_ROOT
    / "resources"
    / "dataset"
    / "processed"
    / "emergencias_112_cyl_2008_2022_clean.csv"
)
DEFAULT_SPLIT = PROJECT_ROOT / "resources" / "dataset" / "splits" / "test.csv"
DEFAULT_MODEL = PROJECT_ROOT / "artifacts" / "models" / "capa2" / "v0.1.0" / "rulefit_lite.joblib"
DEFAULT_OUTPUT = PROJECT_ROOT / "resources" / "internal_validation" / "casos_revision_v0.1.0.csv"
DEFAULT_SUMMARY = PROJECT_ROOT / "resources" / "internal_validation" / "casos_revision_v0.1.0.md"
LABELS = ["P1", "P2", "P3", "P4"]
SIGNAL_COLUMNS = [
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


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _load_joined(clean_csv: Path, split_csv: Path) -> pd.DataFrame:
    split = pd.read_csv(split_csv)
    clean = pd.read_csv(clean_csv).rename(columns={"Identificador": "incident_id"})
    split["incident_id"] = split["incident_id"].astype(str)
    clean["incident_id"] = clean["incident_id"].astype(str)
    joined = split.merge(clean, on="incident_id", how="left", suffixes=("", "_clean"))
    if joined["FechaIncidente"].isna().any():
        missing = int(joined["FechaIncidente"].isna().sum())
        raise RuntimeError(f"{missing} split rows could not be joined with the clean dataset")
    return joined


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value) > 0
    return str(value or "").strip().lower() == "true"


def _signals(row: dict[str, Any]) -> str:
    active = [column for column in SIGNAL_COLUMNS if _truthy(row.get(column))]
    return "; ".join(active) if active else "sin_senales_criticas"


def _predict(model: Any, frame: pd.DataFrame) -> pd.DataFrame:
    records = []
    for row in frame.to_dict(orient="records"):
        probabilities = model.predict_proba_from_row(row)
        predicted = max(probabilities, key=probabilities.get)
        top_rules = model.top_rules_for_label(predicted, limit=3)
        records.append(
            {
                "prediction": predicted,
                "confidence": round(float(probabilities[predicted]), 6),
                "prob_p1": round(float(probabilities["P1"]), 6),
                "prob_p2": round(float(probabilities["P2"]), 6),
                "prob_p3": round(float(probabilities["P3"]), 6),
                "prob_p4": round(float(probabilities["P4"]), 6),
                "rules_preview": " | ".join(str(rule["rule"]) for rule in top_rules),
            }
        )
    return pd.concat([frame.reset_index(drop=True), pd.DataFrame(records)], axis=1)


def _build_sample(predicted: pd.DataFrame, per_class: int, random_state: int) -> pd.DataFrame:
    p1_false_negatives = predicted[
        (predicted["final_label"] == "P1") & (predicted["prediction"] != "P1")
    ].copy()
    p1_false_negatives["sample_type"] = "critical_p1_false_negative"

    supplements = []
    already_selected = set(p1_false_negatives["incident_id"].astype(str))
    for label in LABELS:
        candidates = predicted[
            (predicted["final_label"] == label)
            & (~predicted["incident_id"].astype(str).isin(already_selected))
        ]
        sample_size = min(per_class, len(candidates))
        sampled = candidates.sample(n=sample_size, random_state=random_state).copy()
        sampled["sample_type"] = f"balanced_{label.lower()}"
        supplements.append(sampled)

    sample = pd.concat([p1_false_negatives, *supplements], ignore_index=True)
    sample = sample.sort_values(
        by=["sample_type", "final_label", "anio", "incident_id"],
        kind="stable",
    ).reset_index(drop=True)
    sample.insert(0, "case_id", [f"REV-{idx:03d}" for idx in range(1, len(sample) + 1)])
    return sample


def _review_rows(sample: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    for row in sample.to_dict(orient="records"):
        signals = _signals(row)
        rules_or_signals = f"senales: {signals}; reglas_top_prediccion: {row['rules_preview']}"
        audit = "si" if row["sample_type"] == "critical_p1_false_negative" else ""
        rows.append(
            {
                "case_id": row["case_id"],
                "sample_type": row["sample_type"],
                "incident_id": row["incident_id"],
                "fecha_incidente": row["fecha_incidente"],
                "provincia_inferida": row["provincia_inferida"],
                "categoria_operativa_preliminar": row["categoria_operativa_preliminar"],
                "split": "test",
                "weak_label_p1p4": row["final_label"],
                "recomendacion_sistema": row["prediction"],
                "confianza": row["confidence"],
                "prob_p1": row["prob_p1"],
                "prob_p2": row["prob_p2"],
                "prob_p3": row["prob_p3"],
                "prob_p4": row["prob_p4"],
                "agreement_score": row["agreement_score"],
                "texto_operativo": str(row.get("texto_operativo", ""))[:500],
                "reglas_o_senales_mostradas": rules_or_signals[:700],
                "evidencia_normativa_mostrada": "pendiente_revision_capa3",
                "accion_revisor": "",
                "prioridad_asignada_revisor": "",
                "motivo_divergencia": "",
                "operador_id": "",
                "timestamp_revision": "",
                "auditoria_especial": audit,
                "observaciones": "",
            }
        )
    return rows


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_summary(rows: list[dict[str, Any]], path: Path, output_csv: Path) -> None:
    frame = pd.DataFrame(rows)
    by_type = frame["sample_type"].value_counts().sort_index()
    by_label = frame["weak_label_p1p4"].value_counts().reindex(LABELS, fill_value=0)
    supplement = frame[frame["sample_type"].str.startswith("balanced_")]
    supplement_by_label = supplement["weak_label_p1p4"].value_counts().reindex(LABELS, fill_value=0)
    lines = [
        "# Muestra de validación interna v0.1.0",
        "",
        f"Generado: `{datetime.now(timezone.utc).isoformat()}`",
        f"CSV: `{_rel(output_csv)}`",
        "",
        "## Composición",
        "",
        f"- Casos totales: {len(rows)}",
        f"- Falsos negativos P1 incluidos: {int(by_type.get('critical_p1_false_negative', 0))}",
        (
            "- Muestra equilibrada adicional por clase: "
            + ", ".join(f"{label}={int(supplement_by_label[label])}" for label in LABELS)
        ),
        f"- Distribución total por weak label: {', '.join(f'{label}={int(by_label[label])}' for label in LABELS)}",
        "",
        "## Distribución por tipo de muestra",
        "",
    ]
    for sample_type, count in by_type.items():
        lines.append(f"- {sample_type}: {int(count)}")

    preview_columns = [
        "case_id",
        "sample_type",
        "incident_id",
        "weak_label_p1p4",
        "recomendacion_sistema",
        "confianza",
        "provincia_inferida",
        "categoria_operativa_preliminar",
    ]
    lines.extend(["", "## Primeros 20 casos", "", "| " + " | ".join(preview_columns) + " |"])
    lines.append("|" + "|".join(["---"] * len(preview_columns)) + "|")
    for row in rows[:20]:
        values = [str(row[column]).replace("|", "/") for column in preview_columns]
        lines.append("| " + " | ".join(values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean-csv", type=Path, default=DEFAULT_CLEAN)
    parser.add_argument("--split-csv", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-md", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--balanced-per-class", type=int, default=15)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args(argv)

    model = joblib.load(args.model_path)
    joined = _load_joined(args.clean_csv, args.split_csv)
    predicted = _predict(model, joined)
    sample = _build_sample(predicted, args.balanced_per_class, args.random_state)
    rows = _review_rows(sample)
    _write_csv(rows, args.output_csv)
    _write_summary(rows, args.summary_md, args.output_csv)

    print(
        "[OK] Internal validation sample built "
        f"rows={len(rows)} p1_fn={sum(row['sample_type'] == 'critical_p1_false_negative' for row in rows)} "
        f"csv={_rel(args.output_csv)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
