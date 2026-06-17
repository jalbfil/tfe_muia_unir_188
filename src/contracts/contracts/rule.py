"""E-06 — `OperationalRule`: regla auditable (baseline experto o RuleFit aprendida)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import NormaID, Priority, VariableSource


class OperationalRule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    rule_id: Annotated[str, Field(min_length=1, max_length=64)]
    source: VariableSource
    condition_expression: Annotated[str, Field(min_length=1, max_length=500)]
    human_text: Annotated[str, Field(min_length=1, max_length=200)]
    target_priority: Priority
    weight: float
    normative_anchors: list[NormaID] = Field(default_factory=list)
    usage_count: Annotated[int, Field(ge=0)] = 0
    precision_observed: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    recall_observed: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def _timestamps_ordered(self) -> OperationalRule:
        if self.updated_at < self.created_at:
            raise ValueError("updated_at no puede ser anterior a created_at")
        return self

    @model_validator(mode="after")
    def _baseline_must_be_anchored(self) -> OperationalRule:
        # Las reglas EXPERT_BASELINE requieren al menos un anclaje normativo (Principio VII).
        if self.source is VariableSource.EXPERT_BASELINE and not self.normative_anchors:
            raise ValueError(
                "Una OperationalRule EXPERT_BASELINE requiere ≥1 normative_anchor"
            )
        return self
