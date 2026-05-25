"""T071 — Test contrato Capa 3: PriorityRecommendation → OperatorRecommendation.

No requiere modelo .gguf ni ChromaDB: se mockea el LLM con respuesta fija.

Casos cubiertos:
- P1 con reglas + anchors → OperatorRecommendation válido + ≥1 cita legal.
- P4 sin reglas → válido en modo degradado.
- explanation_text dentro de límites del contrato (20–1200 chars).
- tools_invoked contienen solo tools registradas (MCP_TOOLS_V0_1).
- temperature == 0.0.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ── path setup ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from contracts import (  # type: ignore[import]
    ActivatedRule,
    ConfidenceLevel,
    MCP_TOOLS_V0_1,
    ModelUsed,
    NormaID,
    OperatorRecommendation,
    Priority,
    PriorityRecommendation,
)
from capa3_llm_mcp.explainer import explain  # type: ignore[import]
from capa3_llm_mcp.llm.qwen_wrapper import QwenWrapper  # type: ignore[import]

# ── fixtures ──────────────────────────────────────────────────────────────────

_MOCK_LLM_RESPONSE_P1 = """\
{
  "explanation_text": "Emergencia de prioridad máxima: víctima atrapada con riesgo vital confirmado. Se activan protocolos de rescate urgente conforme a Ley 17/2015.",
  "actuation_hints": [
    "Movilizar unidad de rescate de forma inmediata",
    "Notificar al CECOP Castilla y León",
    "Establecer perímetro de seguridad en la zona"
  ],
  "confidence_disclaimer": "Alta confianza: múltiples reglas de P1 activadas."
}"""

_MOCK_LLM_RESPONSE_P3 = """\
{
  "explanation_text": "Incidente de prioridad media. Sin riesgo vital inmediato pero requiere atención en los próximos minutos.",
  "actuation_hints": ["Enviar primera unidad de evaluación", "Monitorear evolución"],
  "confidence_disclaimer": null
}"""


def _make_p1_rec() -> PriorityRecommendation:
    return PriorityRecommendation(
        incident_id="TEST-001",
        priority_recommended=Priority.P1,
        probabilities={
            Priority.P1: 0.75,
            Priority.P2: 0.15,
            Priority.P3: 0.07,
            Priority.P4: 0.03,
        },
        activated_rules=[
            ActivatedRule(
                rule_id="RD-01",
                human_text="Víctimas atrapadas con riesgo vital → P1 fija",
                weight=1.0,
                normative_anchors=[NormaID.LEY_17_2015, NormaID.PLANCAL_DEC_4_2019],
            )
        ],
        confidence_level=ConfidenceLevel.MEDIUM,
        model_used=ModelUsed.RULEFIT,
        model_version_capa2="0.1.0",
        requires_human_attention=True,
    )


def _make_p4_rec() -> PriorityRecommendation:
    return PriorityRecommendation(
        incident_id="TEST-002",
        priority_recommended=Priority.P4,
        probabilities={
            Priority.P1: 0.02,
            Priority.P2: 0.03,
            Priority.P3: 0.10,
            Priority.P4: 0.85,
        },
        activated_rules=[],
        confidence_level=ConfidenceLevel.HIGH,
        model_used=ModelUsed.RULEFIT,
        model_version_capa2="0.1.0",
        requires_human_attention=False,
    )


def _mock_llm(response: str) -> QwenWrapper:
    """Crea un QwenWrapper mock que devuelve `response` en chat()."""
    mock = MagicMock(spec=QwenWrapper)
    mock.is_available.return_value = True
    mock.chat.return_value = response
    return mock


# ── tests T071 ────────────────────────────────────────────────────────────────

def test_t071_p1_returns_valid_operator_recommendation():
    """T071-A: P1 con reglas → OperatorRecommendation Pydantic válido."""
    rec = _make_p1_rec()
    llm = _mock_llm(_MOCK_LLM_RESPONSE_P1)
    result = explain(rec, "conductor atrapado en vehículo volcado", llm=llm)

    assert isinstance(result, OperatorRecommendation)
    assert result.incident_id == "TEST-001"
    assert result.priority_recommended == Priority.P1


def test_t071_p1_requires_legal_citations():
    """T071-B: P1 → ≥1 LegalCitation (Principio VII: trazabilidad normativa)."""
    rec = _make_p1_rec()
    llm = _mock_llm(_MOCK_LLM_RESPONSE_P1)
    result = explain(rec, "accidente grave", llm=llm)

    assert len(result.legal_citations) >= 1
    assert all(c.norma_id in NormaID for c in result.legal_citations)


def test_t071_explanation_text_within_bounds():
    """T071-C: explanation_text entre 20 y 1200 chars."""
    rec = _make_p1_rec()
    llm = _mock_llm(_MOCK_LLM_RESPONSE_P1)
    result = explain(rec, "accidente", llm=llm)

    assert 20 <= len(result.explanation_text) <= 1200


def test_t071_tools_invoked_are_registered():
    """T071-D: tools_invoked ⊆ MCP_TOOLS_V0_1 (validado por Pydantic vía LLMMetadata)."""
    rec = _make_p1_rec()
    llm = _mock_llm(_MOCK_LLM_RESPONSE_P1)
    result = explain(rec, "accidente", llm=llm)

    for tool in result.llm_metadata.tools_invoked:
        assert tool in MCP_TOOLS_V0_1


def test_t071_temperature_is_zero():
    """T071-E: temperature == 0.0 en producción (NFR-009)."""
    rec = _make_p1_rec()
    llm = _mock_llm(_MOCK_LLM_RESPONSE_P1)
    result = explain(rec, "accidente", llm=llm)

    assert result.llm_metadata.temperature == 0.0


def test_t071_p4_valid_without_rules():
    """T071-F: P4 sin reglas activas → OperatorRecommendation válido (modo degradado si JSON falla)."""
    rec = _make_p4_rec()
    llm = _mock_llm(_MOCK_LLM_RESPONSE_P3)
    result = explain(rec, "árbol caído en calzada", llm=llm)

    assert isinstance(result, OperatorRecommendation)
    assert result.priority_recommended == Priority.P4
    assert len(result.explanation_text) >= 20


def test_t071_degraded_mode_when_llm_unavailable():
    """T071-G: si LLM no disponible → modo degradado, OperatorRecommendation válido."""
    rec = _make_p1_rec()
    mock_llm = MagicMock(spec=QwenWrapper)
    mock_llm.is_available.return_value = False

    result = explain(rec, "accidente grave", llm=mock_llm)

    assert isinstance(result, OperatorRecommendation)
    assert result.priority_recommended == Priority.P1
    assert len(result.legal_citations) >= 1  # P1 garantiza ≥1 cita
    assert "DEGRADADO" in (result.confidence_disclaimer or "").upper()
    assert result.llm_metadata.llm_model == "degraded-static-v0.1.0"
