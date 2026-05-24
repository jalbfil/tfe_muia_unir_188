from __future__ import annotations

import pytest
from pydantic import ValidationError

from contracts import Priority
from tests.factories import WeakLabelFactory


def test_factory_valid_four_annotators() -> None:
    wl = WeakLabelFactory.build()
    assert len(wl.annotator_votes) == 4
    assert 0.0 <= wl.label_model_confidence <= 1.0


def test_fewer_than_three_annotators_rejected() -> None:
    with pytest.raises(ValidationError, match="≥3"):
        WeakLabelFactory.build(
            annotator_votes={"a": Priority.P1, "b": Priority.P1}
        )


def test_three_annotators_accepted() -> None:
    wl = WeakLabelFactory.build(
        annotator_votes={"a": Priority.P1, "b": Priority.P1, "c": Priority.P2}
    )
    assert len(wl.annotator_votes) == 3


def test_agreement_score_range() -> None:
    with pytest.raises(ValidationError):
        WeakLabelFactory.build(agreement_score=1.5)
    with pytest.raises(ValidationError):
        WeakLabelFactory.build(agreement_score=-1.5)
