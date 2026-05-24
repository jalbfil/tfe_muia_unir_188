"""E-07 — `WeakLabel`: etiqueta P1–P4 derivada por weak supervision (R-03)."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import Priority

# Principio IV: ≥3 anotadores con Krippendorff α ≥ 0.67.
_MIN_ANNOTATORS = 3


class WeakLabel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    incident_id: Annotated[str, Field(min_length=1, max_length=64)]
    annotator_votes: dict[Annotated[str, Field(min_length=1, max_length=64)], Priority]
    final_label: Priority
    label_model_confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    agreement_score: Annotated[float, Field(ge=-1.0, le=1.0)]
    was_used_in_training: bool

    @model_validator(mode="after")
    def _min_three_annotators(self) -> WeakLabel:
        n = len(self.annotator_votes)
        if n < _MIN_ANNOTATORS:
            raise ValueError(
                f"WeakLabel requiere ≥{_MIN_ANNOTATORS} anotadores; se recibieron {n}"
            )
        return self
