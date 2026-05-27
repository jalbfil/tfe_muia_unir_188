"""E-04 — `OperatorRecommendation`: salida visible al operador (Capa 3 LLM/MCP)."""

from __future__ import annotations

from typing import Annotated, Final

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from .enums import NormaID, Priority

_SEMVER_RX = r"^\d+\.\d+\.\d+$"

# 3 tools v0.1.0 (R-13). `get_aemet_context` reservada v0.2.0.
MCP_TOOLS_V0_1: Final[frozenset[str]] = frozenset(
    {"search_normative", "get_rule_details", "cite_legal_basis"}
)


class LegalCitation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    norma_id: NormaID
    articulo_o_seccion: Annotated[str, Field(max_length=120)] | None = None
    texto_relevante: Annotated[str, Field(min_length=1, max_length=300)]
    url_oficial: HttpUrl | None = None


class LLMMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    llm_model: Annotated[str, Field(min_length=1, max_length=120)]
    temperature: Annotated[float, Field(ge=0.0, le=1.0)]
    tools_invoked: list[str] = Field(default_factory=list)
    tokens_input: Annotated[int, Field(ge=0)] | None = None
    tokens_output: Annotated[int, Field(ge=0)] | None = None

    @model_validator(mode="after")
    def _tools_must_be_registered(self) -> LLMMetadata:
        unknown = [t for t in self.tools_invoked if t not in MCP_TOOLS_V0_1]
        if unknown:
            raise ValueError(
                f"tools desconocidas: {unknown}; v0.1.0 acepta {sorted(MCP_TOOLS_V0_1)}"
            )
        return self


class OperatorRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    incident_id: Annotated[str, Field(min_length=1, max_length=64)]
    priority_recommended: Priority
    explanation_text: Annotated[str, Field(min_length=20, max_length=1200)]
    legal_citations: list[LegalCitation] = Field(default_factory=list)
    actuation_hints: list[Annotated[str, Field(max_length=200)]] = Field(default_factory=list)
    activated_rules_summary: list[Annotated[str, Field(max_length=200)]] = Field(
        default_factory=list
    )
    confidence_disclaimer: Annotated[str, Field(max_length=300)] | None = None
    model_version_capa3: Annotated[str, Field(pattern=_SEMVER_RX)]
    llm_metadata: LLMMetadata

    @model_validator(mode="after")
    def _p1p2_requires_legal_citations(self) -> OperatorRecommendation:
        if (
            self.priority_recommended in (Priority.P1, Priority.P2)
            and not self.legal_citations
        ):
            raise ValueError(
                f"{self.priority_recommended.value} requiere ≥1 cita legal "
                f"(Principio VII: trazabilidad normativa)"
            )
        return self


def assert_production_temperature(rec: OperatorRecommendation) -> None:
    """Gate runtime de producción (NFR-009): temperature debe ser exactamente 0.0.

    Se aplica solo cuando el orquestador opera en modo PROD; en tests/dev se omite.
    """
    if rec.llm_metadata.temperature != 0.0:
        raise ValueError(
            f"NFR-009: temperature={rec.llm_metadata.temperature} != 0.0 en producción"
        )
