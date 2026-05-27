"""T034/T035 - Build reproducible train/val/test splits for weak labels."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "resources" / "dataset" / "processed" / "weak_labels_p1p4.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "resources" / "dataset" / "splits"
DEFAULT_REPORT_JSON = PROJECT_ROOT / "resources" / "dataset" / "audit" / "splits_report.json"
DEFAULT_REPORT_MD = PROJECT_ROOT / "resources" / "dataset" / "audit" / "splits_report.md"
SEED = 42


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def stratification_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (
        row.get("anio", "NO_ANIO") or "NO_ANIO",
        row.get("provincia_inferida", "NO_PROVINCIA") or "NO_PROVINCIA",
        row.get("final_label", "NO_LABEL") or "NO_LABEL",
    )


def stratified_split(
    rows: list[dict[str, str]], train_ratio: float, val_ratio: float, seed: int
) -> dict[str, list[dict[str, str]]]:
    rng = random.Random(seed)
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[stratification_key(row)].append(row)

    splits: dict[str, list[dict[str, str]]] = {"train": [], "val": [], "test": []}
    for group_rows in groups.values():
        group_rows = list(group_rows)
        rng.shuffle(group_rows)
        n = len(group_rows)
        if n == 1:
            splits["train"].extend(group_rows)
            continue
        n_train = max(1, round(n * train_ratio))
        n_val = round(n * val_ratio)
        if n >= 3 and n_val == 0:
            n_val = 1
        if n_train + n_val >= n:
            n_train = max(1, n - 2) if n >= 3 else 1
            n_val = 1 if n >= 3 else 0
        splits["train"].extend(group_rows[:n_train])
        splits["val"].extend(group_rows[n_train : n_train + n_val])
        splits["test"].extend(group_rows[n_train + n_val :])

    for split_rows in splits.values():
        rng.shuffle(split_rows)
    return splits


def temporal_split(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    splits: dict[str, list[dict[str, str]]] = {"train": [], "val": [], "test": []}
    for row in rows:
        try:
            year = int(row.get("anio", "0"))
        except ValueError:
            splits["train"].append(row)
            continue
        if year <= 2020:
            splits["train"].append(row)
        elif year == 2021:
            splits["val"].append(row)
        else:
            splits["test"].append(row)
    return splits


def distribution(rows: list[dict[str, str]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(row.get(key, "NO_VALUE") or "NO_VALUE" for row in rows).items()))


def validate_splits(splits: dict[str, list[dict[str, str]]]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for split_rows in splits.values():
        for row in split_rows:
            incident_id = row.get("incident_id", "")
            if incident_id in seen:
                duplicates.add(incident_id)
            seen.add(incident_id)
    if duplicates:
        raise RuntimeError(f"Incident IDs appear in several splits: {sorted(duplicates)[:10]}")


def build_report(
    input_csv: Path, splits: dict[str, list[dict[str, str]]], *, temporal: bool, seed: int
) -> dict[str, Any]:
    total = sum(len(rows) for rows in splits.values())
    rel_input = str(input_csv.relative_to(PROJECT_ROOT)) if input_csv.is_relative_to(PROJECT_ROOT) else str(input_csv)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_csv": rel_input,
        "mode": "temporal" if temporal else "stratified",
        "seed": seed if not temporal else None,
        "total_rows": total,
        "split_sizes": {name: len(rows) for name, rows in splits.items()},
        "label_distribution": {
            name: distribution(rows, "final_label") for name, rows in splits.items()
        },
        "year_distribution": {name: distribution(rows, "anio") for name, rows in splits.items()},
        "province_distribution": {
            name: distribution(rows, "provincia_inferida") for name, rows in splits.items()
        },
        "output_format_note": "CSV generated without optional parquet dependencies.",
    }


def write_report(report: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        f"# Splits {report['mode']}",
        "",
        f"- Registros totales: {report['total_rows']}",
        f"- Semilla: {report['seed']}",
        f"- Nota formato: {report['output_format_note']}",
        "",
        "## Tamanios",
        "",
    ]
    lines.extend(f"- {name}: {count}" for name, count in report["split_sizes"].items())
    lines.extend(["", "## Distribucion por etiqueta", ""])
    for split_name, labels in report["label_distribution"].items():
        compact = ", ".join(f"{label}={count}" for label, count in labels.items())
        lines.append(f"- {split_name}: {compact}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument("--temporal", action="store_true")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--train-ratio", type=float, default=0.70)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    args = parser.parse_args(argv)

    rows = load_rows(args.input)
    fieldnames = list(rows[0]) if rows else []
    splits = (
        temporal_split(rows)
        if args.temporal
        else stratified_split(rows, args.train_ratio, args.val_ratio, args.seed)
    )
    validate_splits(splits)
    for name, split_rows in splits.items():
        write_csv(args.output_dir / f"{name}.csv", split_rows, fieldnames)
    report = build_report(args.input, splits, temporal=args.temporal, seed=args.seed)
    write_report(report, args.report_json, args.report_md)
    print(f"[OK] {report['mode']} splits written to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
