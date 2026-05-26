"""Wrapper inicial de inferencia Capa 2.

T050-T052 dejan preparado el contrato estable. T054-T056 sustituiran o
complementaran este baseline con un modelo RuleFit entrenado.
"""

from __future__ import annotations

from contracts import (
    ActivatedRule,
    ConfidenceLevel,
    IncidentFeatures,
    ModelUsed,
    Priority,
    PriorityRecommendation,
)

from capa2_rulefit.baseline_expert.rules import evaluate_baseline_rules

MODEL_VERSION_CAPA2 = "0.1.0"


def _confidence_level(p_max: float) -> ConfidenceLevel:
    if p_max >= 0.80:
        return ConfidenceLevel.HIGH
    if p_max >= 0.60:
        return ConfidenceLevel.MEDIUM
    if p_max >= 0.40:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.UNKNOWN


def _priority_scores(features: IncidentFeatures) -> dict[Priority, float]:
    scores = {
        Priority.P1: 0.20,
        Priority.P2: 0.25,
        Priority.P3: 0.30,
        Priority.P4: 0.25,
    }
    hits = evaluate_baseline_rules(features)
    for hit in hits:
        scores[hit.rule.target_priority] += hit.contribution
    active_priorities = {hit.rule.target_priority for hit in hits}
    if Priority.P1 in active_priorities:
        scores[Priority.P1] = max(scores.values()) + 0.75
    elif Priority.P2 in active_priorities:
        scores[Priority.P2] = max(scores.values()) + 0.35
    has_urgent_rule = any(
        hit.rule.target_priority in (Priority.P1, Priority.P2)
        for hit in hits
    )
    if not has_urgent_rule:
        if features.numero_victimas_estimado.value <= 0 and features.numero_llamadas == 1:
            scores[Priority.P4] += 0.8
        else:
            scores[Priority.P3] += 0.5
    return scores


def _normalise(scores: dict[Priority, float]) -> dict[Priority, float]:
    total = sum(scores.values())
    raw = {priority: value / total for priority, value in scores.items()}
    rounded = {priority: round(value, 6) for priority, value in raw.items()}
    drift = round(1.0 - sum(rounded.values()), 6)
    winner = max(rounded, key=rounded.get)
    rounded[winner] = round(rounded[winner] + drift, 6)
    return rounded


def _activated_rules(features: IncidentFeatures) -> list[ActivatedRule]:
    hits = sorted(
        evaluate_baseline_rules(features),
        key=lambda hit: abs(hit.rule.weight),
        reverse=True,
    )
    return [
        ActivatedRule(
            rule_id=hit.rule.rule_id,
            human_text=hit.rule.human_text,
            weight=hit.rule.weight,
            normative_anchors=hit.rule.normative_anchors,
        )
        for hit in hits[:30]
    ]


def predict(features: IncidentFeatures) -> PriorityRecommendation:
    """Predice prioridad P1-P4 cumpliendo el contrato de Capa 2."""

    probabilities = _normalise(_priority_scores(features))
    recommended = max(probabilities, key=probabilities.get)
    p_max = probabilities[recommended]
    return PriorityRecommendation(
        incident_id=features.incident_id,
        priority_recommended=recommended,
        probabilities=probabilities,
        activated_rules=_activated_rules(features),
        confidence_level=_confidence_level(p_max),
        model_used=ModelUsed.BASELINE_EXPERT,
        model_version_capa2=MODEL_VERSION_CAPA2,
        requires_human_attention=recommended in (Priority.P1, Priority.P2) or p_max < 0.60,
    )
