"""E-08 — `InferenceLog`: traza completa append-only (auditoría UE-IA Anexo III)."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .incident_features import IncidentFeatures
from .operator_decision import OperatorDecision
from .operator_recommendation import OperatorRecommendation
from .priority_recommendation import PriorityRecommendation

# Claves obligatorias en `latencias_ms`
_REQUIRED_LATENCY_KEYS: frozenset[str] = frozenset({"capa1", "capa2", "total"})
# Claves obligatorias en `model_versions`
_REQUIRED_MODEL_VERSION_KEYS: frozenset[str] = frozenset({"capa1", "capa2"})


class InferenceLog(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    log_id: Annotated[str, Field(min_length=26, max_length=26)]  # ULID 26 chars
    incident_id: Annotated[str, Field(min_length=1, max_length=64)]
    input_hash: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]  # SHA-256 hex
    capa1_output: IncidentFeatures
    capa2_output: PriorityRecommendation
    capa3_output: OperatorRecommendation | None = None
    operator_decision: OperatorDecision | None = None
    latencias_ms: dict[str, Annotated[float, Field(ge=0.0)]]
    model_versions: dict[str, Annotated[str, Field(pattern=r"^\d+\.\d+\.\d+$")]]
    tools_invoked: list[str] = Field(default_factory=list)
    timestamp_start: datetime
    timestamp_end: datetime

    @model_validator(mode="after")
    def _timestamps_ordered(self) -> InferenceLog:
        if self.timestamp_end < self.timestamp_start:
            raise ValueError("timestamp_end no puede ser anterior a timestamp_start")
        return self

    @model_validator(mode="after")
    def _required_latency_keys(self) -> InferenceLog:
        missing = _REQUIRED_LATENCY_KEYS - self.latencias_ms.keys()
        if missing:
            raise ValueError(f"latencias_ms requiere claves {sorted(missing)}")
        return self

    @model_validator(mode="after")
    def _required_model_versions(self) -> InferenceLog:
        missing = _REQUIRED_MODEL_VERSION_KEYS - self.model_versions.keys()
        if missing:
            raise ValueError(f"model_versions requiere claves {sorted(missing)}")
        if self.capa3_output is not None and "capa3" not in self.model_versions:
            raise ValueError("model_versions['capa3'] requerido cuando capa3_output != None")
        return self

    @model_validator(mode="after")
    def _incident_ids_consistent(self) -> InferenceLog:
        nested_ids = {self.capa1_output.incident_id, self.capa2_output.incident_id}
        if self.capa3_output is not None:
            nested_ids.add(self.capa3_output.incident_id)
        if self.operator_decision is not None:
            nested_ids.add(self.operator_decision.incident_id)
        if nested_ids != {self.incident_id}:
            raise ValueError(
                f"incident_id inconsistente entre capas: log={self.incident_id}, "
                f"hijos={sorted(nested_ids)}"
            )
        return self


def compute_input_hash(*payloads: str) -> str:
    """SHA-256 sobre payloads concatenados con separador RS (0x1e).

    Determinista — base de la auditoría reproducible (Principio IX).
    """
    h = sha256()
    for p in payloads:
        h.update(p.encode("utf-8"))
        h.update(b"\x1e")
    return h.hexdigest()
