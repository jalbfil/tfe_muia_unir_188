from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from contracts import compute_input_hash
from tests.factories import InferenceLogFactory

MADRID = timezone(timedelta(hours=2))


def test_factory_valid() -> None:
    log = InferenceLogFactory.build()
    assert len(log.input_hash) == 64
    assert log.latencias_ms["total"] >= log.latencias_ms["capa1"]


def test_compute_input_hash_is_deterministic() -> None:
    h1 = compute_input_hash("a", "b")
    h2 = compute_input_hash("a", "b")
    assert h1 == h2
    assert len(h1) == 64


def test_compute_input_hash_separator_avoids_collisions() -> None:
    # "a","b" debe diferir de "ab" gracias al separador RS 0x1e
    assert compute_input_hash("a", "b") != compute_input_hash("ab")


def test_timestamps_ordered() -> None:
    with pytest.raises(ValidationError, match="anterior"):
        InferenceLogFactory.build(
            timestamp_start=datetime(2024, 5, 14, 18, 33, tzinfo=MADRID),
            timestamp_end=datetime(2024, 5, 14, 18, 32, tzinfo=MADRID),
        )


def test_missing_latency_key_rejected() -> None:
    with pytest.raises(ValidationError, match="latencias_ms"):
        InferenceLogFactory.build(latencias_ms={"capa1": 100.0, "capa2": 50.0})


def test_missing_model_version_capa3_when_capa3_present() -> None:
    with pytest.raises(ValidationError, match="capa3"):
        InferenceLogFactory.build(
            model_versions={"capa1": "0.1.0", "capa2": "0.1.0"}
        )


def test_inconsistent_incident_id_rejected() -> None:
    log = InferenceLogFactory.build()
    other_features = log.capa1_output.model_copy(update={"incident_id": "INC-OTHER"})
    with pytest.raises(ValidationError, match="incident_id"):
        InferenceLogFactory.build(capa1_output=other_features)


def test_input_hash_must_be_64_hex() -> None:
    with pytest.raises(ValidationError):
        InferenceLogFactory.build(input_hash="not-a-sha256")


def test_log_id_must_be_ulid_length() -> None:
    with pytest.raises(ValidationError):
        InferenceLogFactory.build(log_id="too-short")
