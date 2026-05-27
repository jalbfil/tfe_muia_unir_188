"""POST /predict — Clasifica un incidente y devuelve la recomendación."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fastapi import APIRouter, Request
from pydantic import BaseModel

from backend.orchestrator.pipeline import run_pipeline  # type: ignore[import]
from contracts import IncidentInput, OperatorRecommendation, PriorityRecommendation  # type: ignore[import]

router = APIRouter()


class PredictResponse(BaseModel):
    recommendation: OperatorRecommendation
    priority_details: PriorityRecommendation
    log_id: str
    degraded: bool = False


@router.post("/predict", response_model=PredictResponse)
def predict(incident: IncidentInput, request: Request) -> PredictResponse:
    """Clasifica el incidente y genera la recomendación con explicación."""
    logger = request.app.state.logger
    llm = getattr(request.app.state, "llm", None)

    recommendation, log = run_pipeline(incident, llm=llm)

    import contextlib
    with contextlib.suppress(Exception):
        logger.log(log)

    degraded = (
        "degraded" in recommendation.llm_metadata.llm_model.lower()
    )

    # Cache log_id en request.app.state para que /feedback lo recupere
    cache = getattr(request.app.state, "log_cache", {})
    cache[incident.incident_id] = log.log_id
    request.app.state.log_cache = cache

    return PredictResponse(
        recommendation=recommendation,
        priority_details=log.capa2_output,
        log_id=log.log_id,
        degraded=degraded,
    )
