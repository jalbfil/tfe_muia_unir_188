"""E-03 — `PriorityRecommendation`: salida de Capa 2 (RuleFit), núcleo interpretable."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import ConfidenceLevel, ModelUsed, NormaID, Priority

_SEMVER_RX = r"^\d+\.\d+\.\d+$"
_PROB_TOLERANCE = 1e-6
_MAX_RULEFIT_RULES = 30  # Principio III: sparsity LASSO ≤30 reglas

# Umbrales de mapeo p_max → ConfidenceLevel (Cap. 9 — calibración)
_THR_HIGH = 0.80
_THR_MEDIUM = 0.60
_THR_LOW = 0.40


class ActivatedRule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    rule_id: Annotated[str, Field(min_length=1, max_length=64)]
    human_text: Annotated[str, Field(min_length=1, max_length=200)]
    weight: float
    normative_anchors: list[NormaID] = Field(default_factory=list)


class PriorityRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    incident_id: Annotated[str, Field(min_length=1, max_length=64)]
    priority_recommended: Priority
    probabilities: dict[Priority, Annotated[float, Field(ge=0.0, le=1.0)]]
    activated_rules: list[ActivatedRule] = Field(default_factory=list)
    confidence_level: ConfidenceLevel
    model_used: ModelUsed
    model_version_capa2: Annotated[str, Field(pattern=_SEMVER_RX)]
    requires_human_attention: bool

    @model_validator(mode="after")
    def _probs_complete_and_sum_to_one(self) -> PriorityRecommendation:
        if set(self.probabilities.keys()) != set(Priority):
            missing = set(Priority) - set(self.probabilities.keys())
            raise ValueError(f"probabilities debe contener P1..P4 (faltan: {sorted(missing)})")
        total = sum(self.probabilities.values())
        if abs(total - 1.0) > _PROB_TOLERANCE:
            raise ValueError(f"probabilities suma {total:.6f}; debe ser 1.0 ± {_PROB_TOLERANCE}")
        return self

    @model_validator(mode="after")
    def _argmax_matches_recommended(self) -> PriorityRecommendation:
        argmax = max(self.probabilities.items(), key=lambda kv: kv[1])[0]
        if argmax != self.priority_recommended:
            raise ValueError(
                f"priority_recommended={self.priority_recommended.value} "
                f"no coincide con argmax({argmax.value}) "
                f"={self.probabilities[argmax]:.4f}"
            )
        return self

    @model_validator(mode="after")
    def _rulefit_sparsity_and_p1p2_rules(self) -> PriorityRecommendation:
        if self.model_used is ModelUsed.RULEFIT and len(self.activated_rules) > _MAX_RULEFIT_RULES:
            raise ValueError(
                f"RuleFit debe producir ≤{_MAX_RULEFIT_RULES} reglas activas; "
                f"se recibieron {len(self.activated_rules)}"
            )
        if (
            self.priority_recommended in (Priority.P1, Priority.P2)
            and not self.activated_rules
        ):
            raise ValueError(
                f"{self.priority_recommended.value} requiere ≥1 regla activada (trazabilidad)"
            )
        return self

    @model_validator(mode="after")
    def _confidence_consistent_with_pmax(self) -> PriorityRecommendation:
        p_max = max(self.probabilities.values())
        if p_max >= _THR_HIGH:
            expected = ConfidenceLevel.HIGH
        elif p_max >= _THR_MEDIUM:
            expected = ConfidenceLevel.MEDIUM
        elif p_max >= _THR_LOW:
            expected = ConfidenceLevel.LOW
        else:
            expected = ConfidenceLevel.UNKNOWN
        if self.confidence_level != expected:
            raise ValueError(
                f"confidence_level={self.confidence_level.value} inconsistente con "
                f"p_max={p_max:.3f} (esperado={expected.value})"
            )
        return self
