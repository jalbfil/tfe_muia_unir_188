"""T030 - Audit the cleaned Registro 112 CyL dataset.

The report is dependency-free so it can run in a fresh checkout. It documents
quality, missingness, duplicates, temporal/province coverage and anti-leakage
columns without using those columns as model features.
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
DEFAULT_REPORT_JSON = PROJECT_ROOT / "resources" / "dataset" / "audit" / "audit_112_cyl_clean.json"
DEFAULT_REPORT_MD = PROJECT_ROOT / "resources" / "dataset" / "audit" / "audit_112_cyl_clean.md"

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
PROVINCES = (
    "Avila",
    "Burgos",
    "Leon",
    "Palencia",
    "Salamanca",
    "Segovia",
    "Soria",
    "Valladolid",
    "Zamora",
)


def _norm(value: str) -> str:
    return (value or "").translate(str.maketrans("ÁÉÍÓÚÜÑáéíóúüñ", "AEIOUUNaeiouun"))


def infer_province(row: dict[str, str]) -> str:
    text = _norm(
        " ".join(
            row.get(col, "")
            for col in ("Título", "titulo_limpio", "DescripcionBlob", "descripcion_limpia", "texto_operativo")
        )
    )
    matches = re.findall(r"\((Avila|Burgos|Leon|Palencia|Salamanca|Segovia|Soria|Valladolid|Zamora)\)", text)
    if matches:
        return Counter(matches).most_common(1)[0][0]
    lower = text.lower()
    for province in PROVINCES:
        if province.lower() in lower:
            return province
    return "NO_INFERIDA"


def load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return reader.fieldnames or [], list(reader)


def top(counter: Counter[str], n: int = 20) -> dict[str, int]:
    return dict(counter.most_common(n))


def audit_dataset(input_csv: Path) -> dict[str, Any]:
    fieldnames, rows = load_rows(input_csv)
    row_count = len(rows)
    missing = {col: 0 for col in fieldnames}
    non_empty = {col: 0 for col in fieldnames}
    identifiers: Counter[str] = Counter()
    years: Counter[str] = Counter()
    provinces: Counter[str] = Counter()
    categories: Counter[str] = Counter()
    incident_types: Counter[str] = Counter()
    signal_counts: Counter[str] = Counter()
    valid_dates: list[str] = []
    invalid_dates = 0
    coords_ok = 0
    signal_columns = [col for col in fieldnames if col.startswith("signal_")]

    for row in rows:
        for col in fieldnames:
            value = (row.get(col) or "").strip()
            if value:
                non_empty[col] += 1
            else:
                missing[col] += 1
        if row.get("Identificador"):
            identifiers[row["Identificador"].strip()] += 1
        if row.get("anio"):
            years[row["anio"].strip()] += 1
        provinces[infer_province(row)] += 1
        categories[(row.get("categoria_operativa_preliminar") or "NO_INFERIDA").strip()] += 1
        incident_types[(row.get("TipoIncidente") or "NO_INFERIDO").strip()] += 1
        if (row.get("tiene_coordenadas") or "").strip().lower() == "true":
            coords_ok += 1
        for signal in signal_columns:
            if (row.get(signal) or "").strip().lower() == "true":
                signal_counts[signal] += 1
        date_value = (row.get("FechaIncidente") or "").strip()
        try:
            datetime.strptime(date_value, "%Y-%m-%d")
        except ValueError:
            invalid_dates += 1
        else:
            valid_dates.append(date_value)

    duplicates = {key: value for key, value in identifiers.items() if value > 1}
    leakage_columns_present = sorted(PROHIBITED_FEATURE_COLUMNS.intersection(fieldnames))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_csv": str(input_csv.relative_to(PROJECT_ROOT)),
        "rows": row_count,
        "columns": len(fieldnames),
        "column_names": fieldnames,
        "missing_by_column": missing,
        "missing_ratio_by_column": {
            col: round(missing[col] / row_count, 6) if row_count else 0.0 for col in fieldnames
        },
        "duplicate_identifiers": {
            "count": sum(value - 1 for value in duplicates.values()),
            "affected_ids": len(duplicates),
            "sample": dict(list(duplicates.items())[:20]),
        },
        "date_range": {
            "min": min(valid_dates) if valid_dates else None,
            "max": max(valid_dates) if valid_dates else None,
            "invalid_count": invalid_dates,
        },
        "distribution_by_year": dict(sorted(years.items())),
        "distribution_by_province_inferred": dict(sorted(provinces.items())),
        "distribution_by_tipo_incidente": top(incident_types),
        "distribution_by_categoria_operativa_preliminar": top(categories),
        "coordinates": {
            "valid_count": coords_ok,
            "missing_or_invalid_count": row_count - coords_ok,
            "coverage_ratio": round(coords_ok / row_count, 6) if row_count else 0.0,
        },
        "signal_true_counts": dict(sorted(signal_counts.items())),
        "prohibited_columns": {
            "present": leakage_columns_present,
            "non_empty_counts": {col: non_empty.get(col, 0) for col in leakage_columns_present},
            "policy": "Audit/evaluation-only; never model features.",
        },
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Auditoría del dataset limpio 112 CyL",
        "",
        f"- Fichero: `{report['input_csv']}`",
        f"- Registros: {report['rows']}",
        f"- Columnas: {report['columns']}",
        f"- Rango temporal válido: {report['date_range']['min']} a {report['date_range']['max']}",
        f"- Fechas inválidas: {report['date_range']['invalid_count']}",
        f"- Identificadores duplicados: {report['duplicate_identifiers']['affected_ids']}",
        f"- Cobertura de coordenadas: {report['coordinates']['coverage_ratio']:.2%}",
        "",
        "## Distribución por año",
        "",
    ]
    lines.extend(f"- {year}: {count}" for year, count in report["distribution_by_year"].items())
    lines.extend(["", "## Distribución por provincia inferida", ""])
    lines.extend(
        f"- {province}: {count}"
        for province, count in report["distribution_by_province_inferred"].items()
    )
    lines.extend(["", "## Categorías operativas preliminares", ""])
    lines.extend(
        f"- {category}: {count}"
        for category, count in report["distribution_by_categoria_operativa_preliminar"].items()
    )
    lines.extend(["", "## Señales textuales", ""])
    lines.extend(f"- {signal}: {count}" for signal, count in report["signal_true_counts"].items())
    lines.extend(["", "## Columnas prohibidas por leakage", ""])
    lines.append("Se documentan para auditoría, pero quedan excluidas de weak labels y training.")
    lines.extend(
        f"- {col}: {count} valores no vacíos"
        for col, count in report["prohibited_columns"]["non_empty_counts"].items()
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    args = parser.parse_args(argv)

    report = audit_dataset(args.input)
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, args.report_md)
    print(f"[OK] Audit written to {args.report_json} and {args.report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
