from __future__ import annotations

import pytest

from contracts import (
    Accesibilidad,
    AvisoAEMET,
    CategoriaPreliminar,
    ConfidenceLevel,
    GravedadLesiones,
    ModelUsed,
    NormaID,
    Priority,
    ProvinciaCyL,
    VariableSource,
)


@pytest.mark.parametrize("enum_cls", [Priority, ConfidenceLevel, ModelUsed, VariableSource])
def test_enums_are_string_serializable(enum_cls: type) -> None:
    for member in enum_cls:
        assert isinstance(member.value, str)
        assert enum_cls(member.value) is member


def test_priority_order_canonical() -> None:
    assert [p.value for p in Priority] == ["P1", "P2", "P3", "P4"]


def test_provincias_son_las_nueve_de_cyl() -> None:
    assert len(list(ProvinciaCyL)) == 9
    assert ProvinciaCyL.VALLADOLID.value == "VALLADOLID"


def test_norma_id_includes_seveso_reserved() -> None:
    assert NormaID.RD_840_2015_SEVESO.value == "RD_840_2015_SEVESO"


def test_aviso_aemet_includes_no_disponible_default() -> None:
    assert AvisoAEMET.NO_DISPONIBLE in AvisoAEMET


def test_categoria_preliminar_has_desconocida_sentinel() -> None:
    assert CategoriaPreliminar.DESCONOCIDA in CategoriaPreliminar


def test_gravedad_lesiones_ordered() -> None:
    expected = ["NINGUNA", "LEVE", "MODERADA", "GRAVE", "CRITICA", "DESCONOCIDA"]
    assert [g.value for g in GravedadLesiones] == expected


def test_accesibilidad_has_desconocida() -> None:
    assert Accesibilidad.DESCONOCIDA in Accesibilidad
