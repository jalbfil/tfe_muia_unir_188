"""POST /predict - Clasifica un incidente y devuelve la recomendación."""

from __future__ import annotations

import contextlib
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from backend.orchestrator.pipeline import run_pipeline  # type: ignore[import]
from contracts import IncidentFeatures, IncidentInput, OperatorRecommendation  # type: ignore[import]

router = APIRouter()


class RuleEvidence(BaseModel):
    rule_id: str
    human_text: str
    weight: float
    normative_anchors: list[str]


class PriorityDetails(BaseModel):
    priority_recommended: str
    probabilities: dict[str, float]
    confidence_level: str
    model_used: str
    model_version_capa2: str
    requires_human_attention: bool
    activated_rules: list[RuleEvidence]


class ExplanationContext(BaseModel):
    """Stable Capa 2 payload for Capa 3 explanations."""

    incident_id: str
    decision_source: str
    priority_recommended: str
    probability_margin: float
    probabilities: dict[str, float]
    confidence_level: str
    activated_rules_summary: list[str]
    evidence: list[RuleEvidence]
    anti_leakage_status: str
    warnings: list[str]


class PredictResponse(BaseModel):
    recommendation: OperatorRecommendation
    features: IncidentFeatures | None = None
    priority_details: PriorityDetails
    explanation_context: ExplanationContext
    log_id: str
    degraded: bool = False


def _rule_to_evidence(rule: Any) -> RuleEvidence:
    return RuleEvidence(
        rule_id=str(rule.rule_id),
        human_text=str(rule.human_text),
        weight=float(rule.weight),
        normative_anchors=[str(anchor) for anchor in rule.normative_anchors],
    )


def _build_priority_details(capa2_output: Any) -> PriorityDetails:
    return PriorityDetails(
        priority_recommended=capa2_output.priority_recommended.value,
        probabilities={
            priority.value: float(probability)
            for priority, probability in capa2_output.probabilities.items()
        },
        confidence_level=capa2_output.confidence_level.value,
        model_used=capa2_output.model_used.value,
        model_version_capa2=capa2_output.model_version_capa2,
        requires_human_attention=bool(capa2_output.requires_human_attention),
        activated_rules=[
            _rule_to_evidence(rule) for rule in capa2_output.activated_rules[:30]
        ],
    )


def _build_explanation_context(capa2_output: Any) -> ExplanationContext:
    probabilities = {
        priority.value: float(probability)
        for priority, probability in capa2_output.probabilities.items()
    }
    ranked = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
    margin = ranked[0][1] - ranked[1][1] if len(ranked) > 1 else ranked[0][1]

    warnings: list[str] = []
    if capa2_output.requires_human_attention:
        warnings.append("requires_human_attention")
    if margin < 0.15:
        warnings.append("low_probability_margin")
    if not capa2_output.activated_rules:
        warnings.append("no_activated_rules")

    return ExplanationContext(
        incident_id=capa2_output.incident_id,
        decision_source="capa2_rulefit_lite_v0.1.0",
        priority_recommended=capa2_output.priority_recommended.value,
        probability_margin=round(margin, 6),
        probabilities=probabilities,
        confidence_level=capa2_output.confidence_level.value,
        activated_rules_summary=[
            str(rule.human_text) for rule in capa2_output.activated_rules[:5]
        ],
        evidence=[_rule_to_evidence(rule) for rule in capa2_output.activated_rules[:30]],
        anti_leakage_status="ok_no_forbidden_columns_in_capa2_runtime_contract",
        warnings=warnings,
    )


@router.post("/predict", response_model=PredictResponse)
def predict(incident: IncidentInput, request: Request) -> PredictResponse:
    """Clasifica el incidente y genera la recomendación con explicación."""
    logger = request.app.state.logger
    llm = getattr(request.app.state, "llm", None)
    if llm is None:
        try:
            from capa3_llm_mcp.llm.qwen_wrapper import QwenWrapper
            wrapper = QwenWrapper()
            if wrapper.is_available():
                request.app.state.llm = wrapper
                llm = wrapper
        except Exception:
            pass

    recommendation, log = run_pipeline(incident, llm=llm)
    priority_details = _build_priority_details(log.capa2_output)
    explanation_context = _build_explanation_context(log.capa2_output)

    with contextlib.suppress(Exception):
        logger.log(log)

    degraded = "degraded" in recommendation.llm_metadata.llm_model.lower()

    cache = getattr(request.app.state, "log_cache", {})
    cache[incident.incident_id] = log.log_id
    request.app.state.log_cache = cache

    return PredictResponse(
        recommendation=recommendation,
        features=log.capa1_output,
        priority_details=priority_details,
        explanation_context=explanation_context,
        log_id=log.log_id,
        degraded=degraded,
    )
