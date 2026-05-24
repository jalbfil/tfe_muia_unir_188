from __future__ import annotations

import pytest

from contracts import (
    ContractsError,
    ContractVersionMismatchError,
    DegradedModeActivated,
    LeakageFieldRejectedError,
    LowConfidenceWarning,
    SLABreachWarning,
)


def test_leakage_error_carries_field_and_reason() -> None:
    exc = LeakageFieldRejectedError(field_name="MediosMov", reason="post-decisión")
    assert exc.field_name == "MediosMov"
    assert "Principio V" in str(exc)
    assert isinstance(exc, ContractsError)


def test_low_confidence_warning_payload() -> None:
    exc = LowConfidenceWarning(incident_id="INC-1", p_max=0.32)
    assert exc.incident_id == "INC-1"
    assert exc.p_max == pytest.approx(0.32)


def test_sla_breach_message_formats_ms() -> None:
    exc = SLABreachWarning(capa="capa3", latency_ms=2500.0, sla_ms=2000.0)
    assert "capa3" in str(exc)
    assert "2500" in str(exc)


def test_degraded_mode_carries_reason() -> None:
    exc = DegradedModeActivated(reason="LLM no disponible")
    assert "Modo degradado" in str(exc)


def test_version_mismatch_carries_model_name() -> None:
    exc = ContractVersionMismatchError(
        model_name="IncidentFeatures", current="abc", declared="0.1.0"
    )
    assert "IncidentFeatures" in str(exc)
