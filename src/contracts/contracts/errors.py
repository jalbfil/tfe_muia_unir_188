"""T018 — Excepciones tipadas del dominio de contratos."""

from __future__ import annotations


class ContractsError(Exception):
    """Excepción base; toda violación de contrato hereda de aquí."""


class LeakageFieldRejectedError(ContractsError):
    """Principio V: se ha intentado usar una columna prohibida como feature."""

    def __init__(self, field_name: str, reason: str) -> None:
        super().__init__(f"Campo prohibido (Principio V): {field_name!r} — {reason}")
        self.field_name = field_name
        self.reason = reason


class LowConfidenceWarning(ContractsError):
    """`ConfidenceLevel.LOW` o `UNKNOWN` ⇒ se exige revisión humana explícita."""

    def __init__(self, incident_id: str, p_max: float) -> None:
        super().__init__(
            f"Confianza baja para incident_id={incident_id}: p_max={p_max:.3f}"
        )
        self.incident_id = incident_id
        self.p_max = p_max


class SLABreachWarning(ContractsError):
    """Latencia supera el SLA definido para la capa."""

    def __init__(self, capa: str, latency_ms: float, sla_ms: float) -> None:
        super().__init__(
            f"SLA superado en {capa}: {latency_ms:.0f}ms > {sla_ms:.0f}ms"
        )
        self.capa = capa
        self.latency_ms = latency_ms
        self.sla_ms = sla_ms


class DegradedModeActivated(ContractsError):
    """Activado el modo degradado (LLM caído, RAG vacío, etc.)."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Modo degradado activado: {reason}")
        self.reason = reason


class ContractVersionMismatchError(ContractsError):
    """Schemas JSON no coinciden con la versión declarada (CI gate)."""

    def __init__(self, model_name: str, current: str, declared: str) -> None:
        super().__init__(
            f"Schema de {model_name} divergente sin bump: declared={declared}, "
            f"hash_diff={current}. Subir versión y regenerar."
        )
        self.model_name = model_name
        self.current = current
        self.declared = declared
