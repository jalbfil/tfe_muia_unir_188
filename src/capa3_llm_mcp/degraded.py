"""T082 — Modo degradado: explicación estática derivada de reglas activadas.

Activado cuando el LLM no está disponible (modelo .gguf no descargado,
llama-cpp-python no instalado, o fallo en inferencia).

Garantías:
- Siempre devuelve un `OperatorRecommendation` válido.
- Para P1/P2, incluye ≥1 `LegalCitation` (desde normative_anchors de las reglas
  o fallback a LEY_17_2015).
- `confidence_disclaimer` indica explícitamente el modo degradado.
- `llm_metadata.llm_model` = "degraded-static-v0.1.0".
"""
from __future__ import annotations

import sys
from pathlib import Path

# Añadir src/ al path para importar contratos sin instalación editable adicional
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # inserta src/ (un nivel menos de profundidad)

from contracts import (  # type: ignore[import]
    LegalCitation,
    LLMMetadata,
    NormaID,
    OperatorRecommendation,
    Priority,
    PriorityRecommendation,
)

from .mcp_server.tools.cite_legal_basis import cite_legal_basis

# Hints genéricos por nivel de prioridad
_HINTS: dict[Priority, list[str]] = {
    Priority.P1: [
        "Movilizar recursos de rescate de forma inmediata",
        "Notificar al CECOP Castilla y León para coordinación",
        "Establecer perímetro de seguridad en zona afectada",
    ],
    Priority.P2: [
        "Avisar al responsable de guardia",
        "Movilizar recursos especializados según tipo de incidente",
        "Mantener comunicación continua con unidades en campo",
    ],
    Priority.P3: [
        "Enviar primera unidad de evaluación",
        "Monitorear evolución del incidente",
        "Confirmar recursos disponibles en la zona",
    ],
    Priority.P4: [
        "Derivar al servicio ordinario correspondiente",
        "Registrar el aviso para seguimiento",
    ],
}

_DISCLAIMER = (
    "MODO DEGRADADO: explicación generada sin LLM. "
    "Revisar manualmente y contrastar con normativa vigente."
)


def _collect_citations(rec: PriorityRecommendation) -> list[LegalCitation]:
    """Recoge LegalCitation desde los normative_anchors de las reglas activadas."""
    seen: set[str] = set()
    citations: list[LegalCitation] = []

    for rule in rec.activated_rules:
        for norma in rule.normative_anchors:
            nid = str(norma)
            if nid in seen:
                continue
            seen.add(nid)
            raw = cite_legal_basis(nid)
            citations.append(
                LegalCitation(
                    norma_id=norma,
                    articulo_o_seccion=raw["articulo_o_seccion"],
                    texto_relevante=raw["texto_relevante"],
                    url_oficial=raw["url_oficial"] or None,
                )
            )

    # Garantía P1/P2: ≥1 cita mínima aunque no haya anchors
    if not citations and rec.priority_recommended in (Priority.P1, Priority.P2):
        raw = cite_legal_basis(NormaID.LEY_17_2015)
        citations.append(
            LegalCitation(
                norma_id=NormaID.LEY_17_2015,
                articulo_o_seccion=raw["articulo_o_seccion"],
                texto_relevante=raw["texto_relevante"],
                url_oficial=raw["url_oficial"],
            )
        )
    return citations


def degraded_explain(rec: PriorityRecommendation) -> OperatorRecommendation:
    """Genera una `OperatorRecommendation` estática sin invocar el LLM.

    Usa el human_text de las reglas activadas como cuerpo de la explicación.
    """
    priority = rec.priority_recommended
    priority_label = {
        Priority.P1: "MÁXIMA URGENCIA (P1)",
        Priority.P2: "URGENCIA ALTA (P2)",
        Priority.P3: "URGENCIA MEDIA (P3)",
        Priority.P4: "PRIORIDAD BAJA (P4)",
    }[priority]

    # Construir explanation_text a partir de reglas
    rule_texts = [r.human_text for r in rec.activated_rules[:3]]
    if rule_texts:
        rules_str = "; ".join(rule_texts)
        explanation = (
            f"Incidente clasificado como {priority_label}. "
            f"Reglas activadas: {rules_str}."
        )
    else:
        explanation = (
            f"Incidente clasificado como {priority_label} por el motor de priorización. "
            f"No hay reglas adicionales disponibles. Proceder según protocolo estándar."
        )

    # Truncar si excede el límite del contrato (max 1200 chars)
    if len(explanation) > 1190:
        explanation = explanation[:1190] + "…"

    citations = _collect_citations(rec)
    hints = _HINTS.get(priority, [])

    return OperatorRecommendation(
        incident_id=rec.incident_id,
        priority_recommended=priority,
        explanation_text=explanation,
        legal_citations=citations,
        actuation_hints=hints,
        activated_rules_summary=[r.human_text for r in rec.activated_rules[:5]],
        confidence_disclaimer=_DISCLAIMER,
        model_version_capa3="0.1.0",
        llm_metadata=LLMMetadata(
            llm_model="degraded-static-v0.1.0",
            temperature=0.0,
            tools_invoked=[],
        ),
    )
