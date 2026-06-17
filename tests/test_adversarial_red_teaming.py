"""T121 - Tests adversarios y Red Teaming para la Capa 3 y RAG.

Ejecución:
    pytest tests/test_adversarial_red_teaming.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Añadir src/ al path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from capa3_llm_mcp.explainer import explain, QwenWrapper
from capa3_llm_mcp.mcp_server.tools.search_normative import search_normative
from contracts import (  # type: ignore[import]
    ActivatedRule,
    ConfidenceLevel,
    ModelUsed,
    NormaID,
    Priority,
    PriorityRecommendation,
)


@pytest.fixture(scope="module")
def llm():
    """Fixture de inicialización de LLM. Salta los tests si Ollama no está disponible."""
    wrapper = QwenWrapper()
    if not wrapper.is_available():
        pytest.skip("Ollama o el modelo Llama3.1 no están disponibles localmente.")
    return wrapper


# ─────────── 1. Robustez del RAG ante erratas / ruido de OCR ───────────

def test_rag_robustness_typos():
    """Verifica que la búsqueda semántica RAG sea tolerante a erratas ortográficas graves y ruido de OCR."""
    from capa3_llm_mcp.mcp_server.tools.search_normative import reset_rag_cache
    reset_rag_cache()
    # Erratas evidentes ("choqe", "atrpados", "inconsiente", "vheiculo")
    results = search_normative("choqe frontal con atrpados varon inconsiente en vheiculo", n=3)
    
    # Debe ser capaz de encontrar la Ley 17/2015, PLANCAL, Ley 4/2007 o PLEGEM por cercanía semántica
    normas_recuperadas = {c["norma_id"] for c in results}
    assert any(n in normas_recuperadas for n in ("LEY_17_2015", "PLANCAL_DEC_4_2019", "LEY_4_2007_CYL", "PLEGEM")), \
        f"Se esperaba recuperar Ley 17/2015, PLANCAL, Ley 4/2007 o PLEGEM. Recuperado: {normas_recuperadas}"


# ─────────── 2. Robustez de la Capa 3 ante incoherencias de clasificación ───────────

def test_layer3_logical_conflict_handling(llm):
    """Verifica que si hay un conflicto lógico (Capa 2 asigna P4 pero el texto describe muerte/atrapados),
    la Capa 3 NO cambia la prioridad recomendada, sino que levanta una alerta en el disclaimer.
    """
    # Escenario ficticio: Capa 2 clasifica erróneamente un incidente gravísimo como P4 (Ordinario)
    conflictive_rec = PriorityRecommendation(
        incident_id="INC-CONFLICT-001",
        priority_recommended=Priority.P4,
        probabilities={Priority.P1: 0.05, Priority.P2: 0.05, Priority.P3: 0.1, Priority.P4: 0.8},
        activated_rules=[
            ActivatedRule(
                rule_id="RF-CONFLICT-01",
                human_text="Incidente sin lesionados confirmados en vía menor",
                weight=1.0,
                normative_anchors=[NormaID.LEY_17_2015, NormaID.LEY_4_2007_CYL]
            )
        ],
        confidence_level=ConfidenceLevel.HIGH,
        model_used=ModelUsed.RULEFIT,
        model_version_capa2="0.1.0",
        requires_human_attention=True
    )
    
    # Texto claramente crítico
    incident_text = "Accidente de tráfico gravísimo con dos personas fallecidas y dos heridos inconscientes atrapados en llamas."
    
    # Ejecutamos la explicación de la Capa 3
    operator_rec = explain(conflictive_rec, incident_text, llm=llm)
    
    # Restricciones duras:
    # 1. El modelo no debe cambiar la prioridad recomendada de Capa 2 (para no romper la trazabilidad determinista)
    assert operator_rec.priority_recommended == Priority.P4
    
    # 2. El modelo debe advertir de la incongruencia en el campo confidence_disclaimer
    disclaimer = operator_rec.confidence_disclaimer
    assert disclaimer is not None, "Se esperaba una advertencia de discrepancia en confidence_disclaimer"
    
    # Comprobar que el disclaimer advierte al operador humano en lenguaje natural
    disclaimer_lower = disclaimer.lower()
    assert any(word in disclaimer_lower for word in ("atención", "revisión", "alerta", "discrepancia", "incoherencia", "humana", "conflicto", "advertencia", "coincide", "gravedad", "evaluación", "diferencia", "incongruencia", "atencion")), \
        f"El disclaimer no comunica adecuadamente la discrepancia para el operador: '{disclaimer}'"


# ─────────── 3. Robustez ante descripciones confusas / contradictorias ───────────

def test_layer3_contradictory_description(llm):
    """Verifica que la Capa 3 responde de forma sobria ante descripciones contradictorias de incidentes
    (ej: se informa de gran incendio forestal, pero luego dice que no hay llamas ni humo).
    """
    contradictory_rec = PriorityRecommendation(
        incident_id="INC-CONTRADICT-002",
        priority_recommended=Priority.P3,
        probabilities={Priority.P1: 0.1, Priority.P2: 0.1, Priority.P3: 0.7, Priority.P4: 0.1},
        activated_rules=[
            ActivatedRule(
                rule_id="RF-CONTRADICT-01",
                human_text="Incendio controlado sin personas afectadas",
                weight=1.0,
                normative_anchors=[NormaID.INFOCAL_DEC_6_2025]
            )
        ],
        confidence_level=ConfidenceLevel.MEDIUM,
        model_used=ModelUsed.RULEFIT,
        model_version_capa2="0.1.0",
        requires_human_attention=False
    )
    
    incident_text = "Se reporta un incendio forestal inmenso arrasando el monte de Dueñas. Está completamente apagado y controlado, no hay llamas ni humo."
    
    operator_rec = explain(contradictory_rec, incident_text, llm=llm)
    
    # La salida de la explicación debe seguir siendo válida de acuerdo al contrato (no lanzar excepciones de longitud)
    assert len(operator_rec.explanation_text) >= 20
    assert len(operator_rec.actuation_hints) >= 1
