"""Roundtrip JSON para TODOS los modelos: garantía de serialización estable."""

from __future__ import annotations

import json

import pytest

from contracts import (
    IncidentFeatures,
    IncidentInput,
    InferenceLog,
    OperatorDecision,
    OperatorRecommendation,
    PriorityRecommendation,
    OperationalRule,
    WeakLabel,
)
from tests.factories import (
    IncidentFeaturesFactory,
    IncidentInputFactory,
    InferenceLogFactory,
    OperationalRuleFactory,
    OperatorDecisionFactory,
    OperatorRecommendationFactory,
    PriorityRecommendationFactory,
    WeakLabelFactory,
)


@pytest.mark.parametrize(
    "factory, model",
    [
        (IncidentInputFactory, IncidentInput),
        (IncidentFeaturesFactory, IncidentFeatures),
        (PriorityRecommendationFactory, PriorityRecommendation),
        (OperatorRecommendationFactory, OperatorRecommendation),
        (OperatorDecisionFactory, OperatorDecision),
        (OperationalRuleFactory, OperationalRule),
        (WeakLabelFactory, WeakLabel),
        (InferenceLogFactory, InferenceLog),
    ],
)
def test_roundtrip_json_for_every_model(factory, model) -> None:  # type: ignore[no-untyped-def]
    obj = factory.build()
    payload = obj.model_dump_json()
    restored = model.model_validate_json(payload)
    assert restored == obj
    # El payload también debe ser JSON parseable
    json.loads(payload)
