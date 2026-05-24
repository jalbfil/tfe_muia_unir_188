from __future__ import annotations

import pytest
from pydantic import ValidationError

from contracts import (
    ActivatedRule,
    ConfidenceLevel,
    ModelUsed,
    NormaID,
    Priority,
    PriorityRecommendation,
)
from tests.factories import PriorityRecommendationFactory


def _rule() -> ActivatedRule:
    return ActivatedRule(
        rule_id="R-EXPERT-007",
        human_text="Atrapado con herido grave ⇒ P1",
        weight=0.4,
        normative_anchors=[NormaID.LEY_17_2015],
    )


def test_factory_passes_all_invariants() -> None:
    obj = PriorityRecommendationFactory.build()
    assert obj.priority_recommended is Priority.P1
    assert sum(obj.probabilities.values()) == pytest.approx(1.0)


def test_probs_must_sum_to_one() -> None:
    with pytest.raises(ValidationError, match="suma"):
        PriorityRecommendationFactory.build(
            probs={Priority.P1: 0.5, Priority.P2: 0.4, Priority.P3: 0.05, Priority.P4: 0.01}
        )


def test_probs_must_contain_all_four_classes() -> None:
    with pytest.raises(ValidationError, match="P1..P4"):
        PriorityRecommendationFactory.build(
            probs={Priority.P1: 0.6, Priority.P2: 0.3, Priority.P3: 0.1}
        )


def test_argmax_must_match_recommended() -> None:
    with pytest.raises(ValidationError, match="argmax"):
        PriorityRecommendationFactory.build(
            priority=Priority.P3,
            probs={Priority.P1: 0.85, Priority.P2: 0.1, Priority.P3: 0.04, Priority.P4: 0.01},
        )


def test_p1_requires_activated_rule() -> None:
    with pytest.raises(ValidationError, match="regla"):
        PriorityRecommendationFactory.build(rules=[])


def test_p2_requires_activated_rule() -> None:
    with pytest.raises(ValidationError, match="regla"):
        PriorityRecommendationFactory.build(
            priority=Priority.P2,
            probs={Priority.P1: 0.1, Priority.P2: 0.85, Priority.P3: 0.04, Priority.P4: 0.01},
            rules=[],
        )


def test_p4_allows_zero_rules() -> None:
    obj = PriorityRecommendationFactory.build(
        priority=Priority.P4,
        probs={Priority.P1: 0.01, Priority.P2: 0.04, Priority.P3: 0.1, Priority.P4: 0.85},
        rules=[],
    )
    assert obj.activated_rules == []


def test_rulefit_capped_at_30_rules() -> None:
    rules = [_rule().model_copy(update={"rule_id": f"R-{i:03d}"}) for i in range(31)]
    with pytest.raises(ValidationError, match="≤30"):
        PriorityRecommendationFactory.build(rules=rules)


def test_confidence_level_consistent_with_pmax() -> None:
    # p_max=0.85 ⇒ HIGH; MEDIUM debería fallar
    with pytest.raises(ValidationError, match="confidence_level"):
        PriorityRecommendationFactory.build(confidence=ConfidenceLevel.MEDIUM)


def test_confidence_level_unknown_for_diffuse_distribution() -> None:
    obj = PriorityRecommendationFactory.build(
        priority=Priority.P3,
        probs={Priority.P1: 0.30, Priority.P2: 0.30, Priority.P3: 0.35, Priority.P4: 0.05},
        rules=[],
        confidence=ConfidenceLevel.UNKNOWN,
    )
    assert obj.confidence_level is ConfidenceLevel.UNKNOWN


def test_baseline_expert_not_capped_at_30() -> None:
    rules = [_rule().model_copy(update={"rule_id": f"R-{i:03d}"}) for i in range(35)]
    # BASELINE_EXPERT permite >30 — el cap es solo para RuleFit
    obj = PriorityRecommendation(
        incident_id="INC-X",
        priority_recommended=Priority.P1,
        probabilities={Priority.P1: 0.85, Priority.P2: 0.1, Priority.P3: 0.04, Priority.P4: 0.01},
        activated_rules=rules,
        confidence_level=ConfidenceLevel.HIGH,
        model_used=ModelUsed.BASELINE_EXPERT,
        model_version_capa2="0.1.0",
        requires_human_attention=False,
    )
    assert len(obj.activated_rules) == 35
