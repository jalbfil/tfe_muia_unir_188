from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from contracts import IncidentInput, ProvinciaCyL
from tests.factories import IncidentInputFactory

MADRID = timezone(timedelta(hours=2))


def test_factory_produces_valid_input() -> None:
    obj = IncidentInputFactory.build()
    assert obj.incident_id == "INC-2024-000001"
    assert obj.latitud == 41.6523
    assert obj.fecha_incidente.tzinfo is not None


def test_texto_titulo_no_puede_estar_vacio() -> None:
    with pytest.raises(ValidationError):
        IncidentInputFactory.build(texto_titulo="")


def test_texto_solo_simbolos_rechazado() -> None:
    with pytest.raises(ValidationError, match="alfabético"):
        IncidentInputFactory.build(texto_titulo="!!!", texto_descripcion="???")


def test_coords_must_be_paired() -> None:
    with pytest.raises(ValidationError, match="juntas"):
        IncidentInputFactory.build(latitud=41.6, longitud=None)
    with pytest.raises(ValidationError, match="juntas"):
        IncidentInputFactory.build(latitud=None, longitud=-4.7)


def test_latitud_out_of_range_rejected() -> None:
    with pytest.raises(ValidationError):
        IncidentInputFactory.build(latitud=120.0, longitud=-4.7)


def test_fecha_incidente_must_be_tz_aware() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        IncidentInputFactory.build(fecha_incidente=datetime(2024, 5, 14, 18, 32))


def test_immutable_frozen() -> None:
    obj = IncidentInputFactory.build()
    with pytest.raises(ValidationError):
        obj.incident_id = "OTHER"  # type: ignore[misc]


def test_roundtrip_json() -> None:
    obj = IncidentInputFactory.build()
    payload = obj.model_dump_json()
    restored = IncidentInput.model_validate_json(payload)
    assert restored == obj


def test_extra_fields_forbidden() -> None:
    with pytest.raises(ValidationError):
        IncidentInputFactory.build(extra_unknown_field="x")


def test_provincia_enum_accepted() -> None:
    obj = IncidentInputFactory.build(provincia=ProvinciaCyL.VALLADOLID)
    assert obj.provincia is ProvinciaCyL.VALLADOLID


def test_coords_both_none_allowed() -> None:
    obj = IncidentInputFactory.build(latitud=None, longitud=None)
    assert obj.latitud is None and obj.longitud is None
