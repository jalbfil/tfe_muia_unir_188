from __future__ import annotations

import pytest
from pydantic import ValidationError

from contracts import (
    AvisoAEMET,
    BoolWithConfidence,
    IncidentFeatures,
    IntWithConfidence,
)
from tests.factories import IncidentFeaturesFactory


def test_factory_builds_valid_features() -> None:
    obj = IncidentFeaturesFactory.build()
    assert obj.numero_llamadas >= 1
    assert obj.aviso_aemet_nivel is AvisoAEMET.NO_DISPONIBLE  # V08 diferida


def test_roundtrip_json_golden() -> None:
    obj = IncidentFeaturesFactory.build()
    payload = obj.model_dump_json()
    restored = IncidentFeatures.model_validate_json(payload)
    assert restored == obj


def test_extra_field_forbidden() -> None:
    with pytest.raises(ValidationError):
        IncidentFeaturesFactory.build(extra="boom")


def test_model_version_capa1_must_be_semver() -> None:
    with pytest.raises(ValidationError):
        IncidentFeaturesFactory.build(model_version_capa1="0.1")


def test_inference_latency_must_be_non_negative() -> None:
    with pytest.raises(ValidationError):
        IncidentFeaturesFactory.build(inference_latency_ms=-1.0)


def test_numero_llamadas_must_be_geq_1() -> None:
    with pytest.raises(ValidationError):
        IncidentFeaturesFactory.build(numero_llamadas=0)


def test_confidence_out_of_range_rejected() -> None:
    with pytest.raises(ValidationError):
        BoolWithConfidence(value=True, confidence=1.2)
    with pytest.raises(ValidationError):
        IntWithConfidence(value=3, confidence=-0.1)


def test_int_with_confidence_sentinel() -> None:
    iwc = IntWithConfidence(value=-1, confidence=0.5)
    assert iwc.value == -1


def test_features_immutable() -> None:
    obj = IncidentFeaturesFactory.build()
    with pytest.raises(ValidationError):
        obj.numero_llamadas = 99  # type: ignore[misc]


def test_v08_v11_default_to_diferido_state() -> None:
    obj = IncidentFeaturesFactory.build()
    assert obj.aviso_aemet_nivel is AvisoAEMET.NO_DISPONIBLE
    assert obj.condicion_meteorologica_adversa is None
    assert obj.en_zona_inundable_snczi is None
    assert obj.proximo_instalacion_seveso_km is None
