"""Evaluate the expert baseline against weak-label splits.

The script is dependency-free and writes reproducible artifacts for comparing
RuleFit later. It joins split labels with the clean dataset by incident id.
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
sys.path.insert(0, str(SRC_ROOT))

from capa2_rulefit.baseline_expert import export_rules_metadata, predict_expert  # noqa: E402

DEFAULT_CLEAN = (
    PROJECT_ROOT
    / "resources"
    / "dataset"
    / "processed"
    / "emergencias_112_cyl_2008_2022_clean.csv"
)
DEFAULT_SPLIT_DIR = PROJECT_ROOT / "resources" / "dataset" / "splits"
DEFAULT_REPORT_JSON = PROJECT_ROOT / "artifacts" / "reports" / "baseline_expert_v0.1.0.json"
DEFAULT_REPORT_MD = PROJECT_ROOT / "artifacts" / "reports" / "baseline_expert_v0.1.0.md"
DEFAULT_RULES_JSON = (
    PROJECT_ROOT / "artifacts" / "models" / "capa2" / "v0.1.0" / "baseline_expert_rules.json"
)
LABELS = ("P1", "P2", "P3", "P4")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _clean_index(path: Path) -> dict[str, dict[str, str]]:
    return {row["Identificador"]: row for row in _read_csv(path)}


def _safe_div(num: float, den: float) -> float:
    return round(num / den, 6) if den else 0.0


def evaluate_split(split_path: Path, clean_rows: dict[str, dict[str, str]]) -> dict[str, Any]:
    rows = _read_csv(split_path)
    confusion: dict[str, Counter[str]] = {label: Counter() for label in LABELS}
    rule_usage: Counter[str] = Counter()
    missing_clean = 0

    for row in rows:
        incident_id = row["incident_id"]
        clean = clean_rows.get(incident_id)
        if clean is None:
            missing_clean += 1
            continue
        pred = predict_expert(clean)
        y_true = row["final_label"]
        y_pred = str(pred["priority_recommended"])
        confusion[y_true][y_pred] += 1
        for hit in pred["activated_rules"]:  # type: ignore[index]
            rule_usage[str(hit["rule_id"])] += 1

    per_class: dict[str, dict[str, float]] = {}
    total_ok = 0
    total = sum(sum(preds.values()) for preds in confusion.values())
    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in LABELS if other != label)
        fn = sum(confusion[label][other] for other in LABELS if other != label)
        total_ok += tp
        precision = _safe_div(tp, tp + fp)
        recall = _safe_div(tp, tp + fn)
        f1 = _safe_div(2 * precision * recall, precision + recall)
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1}

    macro_f1 = round(sum(metrics["f1"] for metrics in per_class.values()) / len(LABELS), 6)
    return {
        "rows": len(rows),
        "evaluated_rows": total,
        "missing_clean_rows": missing_clean,
        "accuracy": _safe_div(total_ok, total),
        "macro_f1": macro_f1,
        "recall_p1": per_class["P1"]["recall"],
        "per_class": per_class,
        "confusion_matrix": {
            label: {pred: confusion[label][pred] for pred in LABELS} for label in LABELS
        },
        "top_rules": dict(rule_usage.most_common(20)),
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Baseline experto Capa 2 v0.1.0",
        "",
        f"- Reglas expertas: {report['rule_count']}",
        f"- Generado: {report['generated_at']}",
        "",
        "## Metricas por split",
        "",
    ]
    for split_name, metrics in report["splits"].items():
        lines.append(
            f"- {split_name}: accuracy={metrics['accuracy']}, "
            f"macro_f1={metrics['macro_f1']}, recall_p1={metrics['recall_p1']}"
        )
    lines.extend(["", "## Criterio experimental", ""])
    lines.append(
        "RuleFit debera superar este baseline interpretable en macro-F1 y mantener "
        "recall P1 competitivo sin violar el limite de 30 reglas activas."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean-csv", type=Path, default=DEFAULT_CLEAN)
    parser.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument(
        "--rules-json",
        type=Path,
        default=DEFAULT_RULES_JSON,
    )
    args = parser.parse_args(argv)

    clean_rows = _clean_index(args.clean_csv)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "baseline_expert",
        "model_version_capa2": "0.1.0",
        "rule_count": len(export_rules_metadata()),
        "splits": {
            split: evaluate_split(args.split_dir / f"{split}.csv", clean_rows)
            for split in ("train", "val", "test")
        },
        "anti_leakage_policy": "Only pre-decision textual signals and derived V01-V15 proxies are used.",
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, args.report_md)
    args.rules_json.parent.mkdir(parents=True, exist_ok=True)
    args.rules_json.write_text(
        json.dumps(export_rules_metadata(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] Baseline expert report written to {args.report_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
