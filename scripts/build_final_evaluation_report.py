"""Build the final evaluation traceability report for T116.

This script consolidates the already-generated evaluation artifacts into a single
auditable index. It does not recompute metrics; it verifies that each referenced
artifact exists and records the main numbers used in Cap. 9, Anexo D and Anexo L.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVALUATION = PROJECT_ROOT / "artifacts" / "reports" / "evaluation_v0.1.0.json"
DEFAULT_FIDELITY = PROJECT_ROOT / "artifacts" / "reports" / "explanation_fidelity_v0.1.0.json"
DEFAULT_INTERNAL_SAMPLE = PROJECT_ROOT / "resources" / "internal_validation" / "casos_revision_v0.1.0.csv"
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "artifacts" / "reports" / "final_evaluation_traceability_v0.1.0.json"
DEFAULT_OUTPUT_MD = PROJECT_ROOT / "artifacts" / "reports" / "final_evaluation_traceability_v0.1.0.md"

REQUIRED_LOCAL_ARTIFACTS = {
    "evaluation_json": DEFAULT_EVALUATION,
    "evaluation_markdown": PROJECT_ROOT / "artifacts" / "reports" / "evaluation_v0.1.0.md",
    "explanation_fidelity_json": DEFAULT_FIDELITY,
    "explanation_fidelity_markdown": PROJECT_ROOT / "artifacts" / "reports" / "explanation_fidelity_v0.1.0.md",
    "explanation_fidelity_cases": PROJECT_ROOT / "artifacts" / "reports" / "explanation_fidelity_cases_v0.1.0.csv",
    "internal_validation_sample": DEFAULT_INTERNAL_SAMPLE,
    "internal_validation_summary": PROJECT_ROOT / "resources" / "internal_validation" / "casos_revision_v0.1.0.md",
    "internal_validation_protocol": PROJECT_ROOT / "resources" / "internal_validation" / "protocolo_validacion_interna.md",
    "p1_error_analysis": PROJECT_ROOT / "artifacts" / "reports" / "p1_error_analysis_v0.1.0.csv",
    "bias_by_province": PROJECT_ROOT / "artifacts" / "reports" / "bias_by_province_v0.1.0.csv",
    "bias_by_year": PROJECT_ROOT / "artifacts" / "reports" / "bias_by_year_v0.1.0.csv",
    "bias_by_category": PROJECT_ROOT / "artifacts" / "reports" / "bias_by_category_v0.1.0.csv",
}

DOCUMENT_TRACE = {
    "capitulo_9": "latex/chapters/chap9.tex",
    "anexo_d": "latex/chapters/anexo_d.tex",
    "anexo_l": "latex/chapters/anexo_l.tex",
    "capitulo_10": "latex/chapters/chap10.tex",
}


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return sum(1 for _ in reader)


def _assert_artifacts_exist(paths: dict[str, Path]) -> dict[str, dict[str, Any]]:
    inventory: dict[str, dict[str, Any]] = {}
    missing = []
    for name, path in paths.items():
        exists = path.exists()
        if not exists:
            missing.append(f"{name}: {_rel(path)}")
        inventory[name] = {
            "path": _rel(path),
            "exists": exists,
            "bytes": int(path.stat().st_size) if exists else None,
        }
    if missing:
        raise FileNotFoundError("Missing required artifacts:\n- " + "\n- ".join(missing))
    return inventory


def _summary(evaluation: dict[str, Any], fidelity: dict[str, Any], sample_csv: Path) -> dict[str, Any]:
    stratified = evaluation["evaluation"]["stratified_test"]
    temporal = evaluation["evaluation"]["temporal_test"]
    critical = stratified["critical_errors"]
    fidelity_summary = fidelity["summary"]
    return {
        "selected_model": "RuleFit-lite",
        "stratified_test": {
            "rows": stratified["metrics"]["rows"],
            "accuracy": stratified["metrics"]["accuracy"],
            "macro_f1": stratified["metrics"]["macro_f1"],
            "recall_p1": stratified["metrics"]["recall_p1"],
        },
        "temporal_test": {
            "rows": temporal["metrics"]["rows"],
            "accuracy": temporal["metrics"]["accuracy"],
            "macro_f1": temporal["metrics"]["macro_f1"],
            "recall_p1": temporal["metrics"]["recall_p1"],
        },
        "critical_errors": critical,
        "internal_validation": {
            "sample_rows": _count_csv_rows(sample_csv),
            "p1_false_negatives_included": critical["p1_false_negatives"],
            "balanced_extra_cases": _count_csv_rows(sample_csv) - critical["p1_false_negatives"],
        },
        "explanation_fidelity": {
            "rows": fidelity_summary["rows"],
            "pass_rate": fidelity_summary["pass_rate"],
            "mean_fidelity": fidelity_summary["mean_fidelity"],
            "min_fidelity": fidelity_summary["min_fidelity"],
            "judge_mode": fidelity["judge_mode"],
        },
    }


def _write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    artifacts = report["artifact_inventory"]
    lines = [
        "# Reporte final de evaluacion y trazabilidad v0.1.0",
        "",
        f"Generado: `{report['generated_at']}`",
        "",
        "## Resumen ejecutivo",
        "",
        f"- Modelo seleccionado: {summary['selected_model']}",
        (
            "- Test estratificado: "
            f"accuracy {summary['stratified_test']['accuracy']}, "
            f"macro-F1 {summary['stratified_test']['macro_f1']}, "
            f"recall P1 {summary['stratified_test']['recall_p1']}."
        ),
        (
            "- Test temporal 2022: "
            f"accuracy {summary['temporal_test']['accuracy']}, "
            f"macro-F1 {summary['temporal_test']['macro_f1']}, "
            f"recall P1 {summary['temporal_test']['recall_p1']}."
        ),
        (
            "- Falsos negativos P1: "
            f"{summary['critical_errors']['p1_false_negatives']} "
            f"(P1->P2={summary['critical_errors']['p1_to_p2']}, "
            f"P1->P3={summary['critical_errors']['p1_to_p3']}, "
            f"P1->P4={summary['critical_errors']['p1_to_p4']})."
        ),
        (
            "- Validacion interna: "
            f"{summary['internal_validation']['sample_rows']} casos, con "
            f"{summary['internal_validation']['p1_false_negatives_included']} P1 falsos negativos "
            f"y {summary['internal_validation']['balanced_extra_cases']} casos equilibrados."
        ),
        (
            "- Fidelidad explicativa offline: "
            f"pass rate {summary['explanation_fidelity']['pass_rate']}, "
            f"media {summary['explanation_fidelity']['mean_fidelity']}, "
            f"minima {summary['explanation_fidelity']['min_fidelity']}."
        ),
        "",
        "## Trazabilidad documental",
        "",
        "| Documento | Papel en la evaluacion |",
        "|---|---|",
        "| `latex/chapters/chap9.tex` | Narrativa academica de resultados, sesgo, errores P1, validacion y fidelidad. |",
        "| `latex/chapters/anexo_d.tex` | Plantilla y muestra real de validacion interna. |",
        "| `latex/chapters/anexo_l.tex` | Model card de Capa 2 y fidelidad de Capa 3. |",
        "| `latex/chapters/chap10.tex` | Conclusiones, limitaciones y trabajo futuro. |",
        "",
        "## Inventario de artefactos",
        "",
        "| Artefacto | Ruta | Bytes |",
        "|---|---|---:|",
    ]
    for name, item in artifacts.items():
        lines.append(f"| {name} | `{item['path']}` | {item['bytes']} |")
    lines.extend(
        [
            "",
            "## Cierre",
            "",
            "Este reporte es el indice maestro de evaluacion v0.1.0. La conformidad UE-IA extendida "
            "queda reservada para el Anexo M/T115, pero este documento ya enlaza los artefactos "
            "necesarios de metricas, sesgo, errores criticos, validacion interna y fidelidad explicativa.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation-json", type=Path, default=DEFAULT_EVALUATION)
    parser.add_argument("--fidelity-json", type=Path, default=DEFAULT_FIDELITY)
    parser.add_argument("--internal-sample", type=Path, default=DEFAULT_INTERNAL_SAMPLE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)

    artifacts = dict(REQUIRED_LOCAL_ARTIFACTS)
    artifacts["final_traceability_json"] = args.output_json
    artifacts["final_traceability_markdown"] = args.output_md
    document_paths = {name: PROJECT_ROOT / rel_path for name, rel_path in DOCUMENT_TRACE.items()}
    artifacts.update(document_paths)

    # Output files are allowed not to exist before this run.
    preexisting = {key: value for key, value in artifacts.items() if key not in {"final_traceability_json", "final_traceability_markdown"}}
    inventory = _assert_artifacts_exist(preexisting)

    evaluation = _load_json(args.evaluation_json)
    fidelity = _load_json(args.fidelity_json)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "T116 final evaluation traceability report",
        "summary": _summary(evaluation, fidelity, args.internal_sample),
        "documents": {name: _rel(path) for name, path in document_paths.items()},
        "artifact_inventory": inventory,
        "open_items": [
            "T115 official EU-AI checklist / Anexo M remains pending.",
            "External 112 operator validation remains future work.",
            "Independent local LLM-as-Judge can be added over the same 111-case sample.",
        ],
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    inventory["final_traceability_json"] = {
        "path": _rel(args.output_json),
        "exists": True,
        "bytes": int(args.output_json.stat().st_size),
    }
    inventory["final_traceability_markdown"] = {
        "path": _rel(args.output_md),
        "exists": True,
        "bytes": None,
    }
    report["artifact_inventory"] = inventory
    _write_markdown(report, args.output_md)

    # Refresh markdown size after writing.
    report["artifact_inventory"]["final_traceability_markdown"]["bytes"] = int(args.output_md.stat().st_size)
    _write_markdown(report, args.output_md)
    report["artifact_inventory"]["final_traceability_markdown"]["bytes"] = int(args.output_md.stat().st_size)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        "[OK] Final evaluation traceability report built "
        f"macro_f1={report['summary']['stratified_test']['macro_f1']} "
        f"fidelity={report['summary']['explanation_fidelity']['mean_fidelity']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
