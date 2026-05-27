from __future__ import annotations

from contracts import Priority
from tests.factories import OperatorDecisionFactory


def test_factory_no_divergencia() -> None:
    obj = OperatorDecisionFactory.build()
    assert obj.divergencia_niveles == 0
    assert obj.auditoria_especial is False


def test_divergencia_un_nivel() -> None:
    obj = OperatorDecisionFactory.build(priority_assigned_by_operator=Priority.P2)
    assert obj.divergencia_niveles == 1
    assert obj.auditoria_especial is False


def test_divergencia_dos_niveles_dispara_auditoria() -> None:
    obj = OperatorDecisionFactory.build(priority_assigned_by_operator=Priority.P3)
    assert obj.divergencia_niveles == 2
    assert obj.auditoria_especial is True


def test_divergencia_maxima() -> None:
    obj = OperatorDecisionFactory.build(priority_assigned_by_operator=Priority.P4)
    assert obj.divergencia_niveles == 3
    assert obj.auditoria_especial is True


def test_motivo_divergencia_optional_when_no_diverge() -> None:
    obj = OperatorDecisionFactory.build()
    assert obj.motivo_divergencia is None
