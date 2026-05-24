from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from contracts import VariableSource
from tests.factories import OperationalRuleFactory

MADRID = timezone(timedelta(hours=2))


def test_factory_valid() -> None:
    rule = OperationalRuleFactory.build()
    assert rule.target_priority.value == "P1"
    assert len(rule.normative_anchors) >= 1


def test_updated_before_created_rejected() -> None:
    with pytest.raises(ValidationError, match="anterior"):
        OperationalRuleFactory.build(
            created_at=datetime(2024, 5, 14, tzinfo=MADRID),
            updated_at=datetime(2024, 1, 1, tzinfo=MADRID),
        )


def test_baseline_without_anchors_rejected() -> None:
    with pytest.raises(ValidationError, match="normative_anchor"):
        OperationalRuleFactory.build(
            source=VariableSource.EXPERT_BASELINE, normative_anchors=[]
        )


def test_rulefit_learned_can_omit_anchors() -> None:
    rule = OperationalRuleFactory.build(
        source=VariableSource.RULEFIT_LEARNED, normative_anchors=[]
    )
    assert rule.normative_anchors == []
