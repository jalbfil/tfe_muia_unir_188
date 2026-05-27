"""Tipos primitivos compuestos reutilizados (`<valor, confidence>`)."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

Confidence = Annotated[float, Field(ge=0.0, le=1.0)]


class _FrozenBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class BoolWithConfidence(_FrozenBase):
    value: bool
    confidence: Confidence


class IntWithConfidence(_FrozenBase):
    # `-1` se reserva como sentinela "desconocido" (ver data-model V02).
    value: Annotated[int, Field(ge=-1)]
    confidence: Confidence
