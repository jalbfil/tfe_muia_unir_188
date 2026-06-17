"""T120 - Generador del borrador de Gold Standard de explicaciones para la Capa 3.

Uso:
    uv run python scripts/build_gold_standard.py --limit 15
    uv run python scripts/build_gold_standard.py --all
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

# Añadir src/ al path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import pandas as pd  # type: ignore[import-untyped]

from capa3_llm_mcp.explainer import explain, QwenWrapper
from contracts import (  # type: ignore[import]
    ActivatedRule,
    ConfidenceLevel,
    ModelUsed,
    NormaID,
    Priority,
    PriorityRecommendation,
)

DEFAULT_INPUT = PROJECT_ROOT / "resources" / "internal_validation" / "casos_revision_v0.1.0.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts" / "reports" / "gold_standard_draft_v0.1.0.csv"


def _confidence_level(max_probability: float) -> ConfidenceLevel:
    if max_probability >= 0.80:
        return ConfidenceLevel.HIGH
    if max_probability >= 0.60:
        return ConfidenceLevel.MEDIUM
    if max_probability >= 0.40:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.UNKNOWN


def _split_rule_texts(raw: str) -> list[str]:
    marker = "reglas_top_prediccion:"
    if marker not in raw:
        return []
    tail = raw.split(marker, 1)[1]
    return [part.strip() for part in tail.split("|") if part.strip()]


def _anchors_for_row(row: dict) -> list[NormaID]:
    category = str(row.get("categoria_operativa_preliminar", "")).lower()
    anchors = [NormaID.LEY_17_2015, NormaID.PLANCAL_DEC_4_2019]
    if "incendio" in category:
        anchors.append(NormaID.INFOCAL_DEC_6_2025)
    if "meteor" in category or "inund" in category:
        anchors.append(NormaID.INUNCYL)
    if "sanitario" in category:
        anchors.append(NormaID.RGPD)
    return anchors


def _activated_rules(row: dict) -> list[ActivatedRule]:
    rules = []
    texts = _split_rule_texts(str(row.get("reglas_o_senales_mostradas", "")))
    anchors = _anchors_for_row(row)
    for idx, text in enumerate(texts[:5], start=1):
        rules.append(
            ActivatedRule(
                rule_id=f"RF-{row['case_id']}-{idx:02d}",
                human_text=text[:200],
                weight=1.0 / idx,
                normative_anchors=anchors,
            )
        )
    if not rules and row["recomendacion_sistema"] in ("P1", "P2"):
        rules.append(
            ActivatedRule(
                rule_id=f"RF-{row['case_id']}-FALLBACK",
                human_text=str(row.get("reglas_o_senales_mostradas", ""))[:200]
                or "Señales textuales predecisionales compatibles con prioridad alta",
                weight=0.1,
                normative_anchors=anchors,
            )
        )
    return rules


def _priority_recommendation(row: dict) -> PriorityRecommendation:
    probabilities = {
        Priority.P1: float(row["prob_p1"]),
        Priority.P2: float(row["prob_p2"]),
        Priority.P3: float(row["prob_p3"]),
        Priority.P4: float(row["prob_p4"]),
    }
    total = sum(probabilities.values())
    if abs(total - 1.0) > 1e-6:
        probabilities = {p: val / total for p, val in probabilities.items()}
    pmax = max(probabilities.values())
    recommended = Priority(str(row["recomendacion_sistema"]))
    return PriorityRecommendation(
        incident_id=str(row["incident_id"]),
        priority_recommended=recommended,
        probabilities=probabilities,
        activated_rules=_activated_rules(row),
        confidence_level=_confidence_level(pmax),
        model_used=ModelUsed.RULEFIT,
        model_version_capa2="0.1.0",
        requires_human_attention=recommended in (Priority.P1, Priority.P2)
        or str(row.get("sample_type")) == "critical_p1_false_negative",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="T120 - Generador de Gold Standard (Capa 3)")
    parser.add_argument("--sample-csv", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=10, help="Límite de casos a procesar")
    parser.add_argument("--all", action="store_true", help="Procesar todos los casos del CSV")
    args = parser.parse_args()

    if not args.sample_csv.exists():
        print(f"Error: No existe el archivo de muestras en {args.sample_csv}")
        return 1

    llm = QwenWrapper()
    if not llm.is_available():
        print("Error: Ollama o el modelo Llama3.1 no están disponibles localmente.")
        return 2

    df = pd.read_csv(args.sample_csv)
    limit = len(df) if args.all else args.limit
    print(f"Iniciando generación de explicaciones para {limit} casos...")

    results = []
    for idx, row in enumerate(df.to_dict(orient="records")[:limit], start=1):
        case_id = row["case_id"]
        incident_text = row["texto_operativo"]
        priority_rec = _priority_recommendation(row)

        print(f"[{idx}/{limit}] Procesando caso {case_id} (ID: {priority_rec.incident_id}) ...")
        
        try:
            # Llamamos a explain inyectando el LLM real
            operator_rec = explain(priority_rec, incident_text, llm=llm)
            
            results.append({
                "case_id": case_id,
                "incident_id": row["incident_id"],
                "texto_operativo": incident_text,
                "recomendacion_sistema": row["recomendacion_sistema"],
                "explanation_text": operator_rec.explanation_text,
                "confidence_disclaimer": operator_rec.confidence_disclaimer,
                "actuation_hints": "|".join(operator_rec.actuation_hints),
                "legal_citations": len(operator_rec.legal_citations),
                "model_version_capa3": operator_rec.model_version_capa3,
            })
        except Exception as exc:
            print(f"  [ERROR] Falló procesamiento del caso {case_id}: {exc}")
            continue

    if not results:
        print("No se generaron resultados.")
        return 1

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(results)
    out_df.to_csv(args.output_csv, index=False, encoding="utf-8")
    print(f"\n[OK] Borrador inicial del Gold Standard guardado en: {args.output_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
