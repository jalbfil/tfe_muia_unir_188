from __future__ import annotations

import pytest
from pydantic import ValidationError

from contracts import (
    MCP_TOOLS_V0_1,
    LegalCitation,
    LLMMetadata,
    NormaID,
    OperatorRecommendation,
    Priority,
    assert_production_temperature,
)
from tests.factories import OperatorRecommendationFactory


def test_factory_valid() -> None:
    obj = OperatorRecommendationFactory.build()
    assert obj.priority_recommended is Priority.P1
    assert obj.llm_metadata.temperature == 0.0


def test_mcp_tools_set_is_three() -> None:
    assert frozenset(
        {"search_normative", "get_rule_details", "cite_legal_basis"}
    ) == MCP_TOOLS_V0_1


def test_p1_requires_citations() -> None:
    with pytest.raises(ValidationError, match="cita legal"):
        OperatorRecommendationFactory.build(citations=[])


def test_p2_requires_citations() -> None:
    with pytest.raises(ValidationError, match="cita legal"):
        OperatorRecommendationFactory.build(priority=Priority.P2, citations=[])


def test_p3_allows_no_citations() -> None:
    obj = OperatorRecommendationFactory.build(priority=Priority.P3, citations=[])
    assert obj.legal_citations == []


def test_explanation_min_length_enforced() -> None:
    with pytest.raises(ValidationError):
        OperatorRecommendation(
            incident_id="INC-1",
            priority_recommended=Priority.P3,
            explanation_text="muy corta",
            model_version_capa3="0.1.0",
            llm_metadata=LLMMetadata(
                llm_model="qwen2.5-7b-instruct-q4_k_m", temperature=0.0
            ),
        )


def test_explanation_max_length_enforced() -> None:
    with pytest.raises(ValidationError):
        OperatorRecommendationFactory.build(
            citations=[
                LegalCitation(
                    norma_id=NormaID.LEY_17_2015,
                    texto_relevante="x" * 301,
                )
            ]
        )


def test_unknown_mcp_tool_rejected() -> None:
    with pytest.raises(ValidationError, match="desconocidas"):
        OperatorRecommendationFactory.build(tools=["search_normative", "get_aemet_context"])


def test_get_aemet_context_is_reserved_not_accepted_v01() -> None:
    """R-13: get_aemet_context queda diferida a v0.2.0."""
    assert "get_aemet_context" not in MCP_TOOLS_V0_1


def test_production_temperature_assertion_passes_at_zero() -> None:
    obj = OperatorRecommendationFactory.build()
    assert_production_temperature(obj)


def test_production_temperature_assertion_fails_above_zero() -> None:
    obj = OperatorRecommendationFactory.build()
    obj_warm = obj.model_copy(
        update={"llm_metadata": obj.llm_metadata.model_copy(update={"temperature": 0.3})}
    )
    with pytest.raises(ValueError, match="NFR-009"):
        assert_production_temperature(obj_warm)


def test_legal_citation_url_validated() -> None:
    LegalCitation(
        norma_id=NormaID.LEY_17_2015,
        texto_relevante="ok",
        url_oficial="https://www.boe.es/eli/es/l/2015/07/09/17",
    )
    with pytest.raises(ValidationError):
        LegalCitation(
            norma_id=NormaID.LEY_17_2015,
            texto_relevante="ok",
            url_oficial="not-a-url",
        )
