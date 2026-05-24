"""E-05 — `OperatorDecision`: cierre del bucle humano (supervisión, Principio II)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from .enums import Priority

_PRIORITY_ORDER: dict[Priority, int] = {
    Priority.P1: 0,
    Priority.P2: 1,
    Priority.P3: 2,
    Priority.P4: 3,
}


class OperatorDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    incident_id: Annotated[str, Field(min_length=1, max_length=64)]
    priority_recommended_by_system: Priority
    priority_assigned_by_operator: Priority
    motivo_divergencia: Annotated[str, Field(min_length=1, max_length=500)] | None = None
    operador_id: Annotated[str, Field(min_length=1, max_length=64)]
    timestamp: datetime

    @property
    def divergencia_niveles(self) -> int:
        return abs(
            _PRIORITY_ORDER[self.priority_assigned_by_operator]
            - _PRIORITY_ORDER[self.priority_recommended_by_system]
        )

    @property
    def auditoria_especial(self) -> bool:
        # ≥2 niveles de salto exige revisión semanal (Cap. 9 monitoring).
        return self.divergencia_niveles >= 2
