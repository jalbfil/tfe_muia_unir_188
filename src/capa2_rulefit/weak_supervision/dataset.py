"""Tipos ligeros para leer artefactos de weak supervision."""

from __future__ import annotations

from dataclasses import dataclass

from contracts import Priority


@dataclass(frozen=True)
class WeakLabelRow:
    incident_id: str
    final_label: Priority
    label_model_confidence: float
    agreement_score: float
