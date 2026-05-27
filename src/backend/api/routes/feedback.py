"""POST /feedback — Recibe la decisión del operador y actualiza el log."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fastapi import APIRouter, Request
from pydantic import BaseModel

from contracts import OperatorDecision  # type: ignore[import]

router = APIRouter()


class FeedbackResponse(BaseModel):
    ok: bool
    log_id: str


@router.post("/feedback", response_model=FeedbackResponse)
def feedback(decision: OperatorDecision, request: Request) -> FeedbackResponse:
    """Registra la decisión del operador y la asocia al log de inferencia."""
    logger = request.app.state.logger

    # Obtener log_id del cache
    cache = getattr(request.app.state, "log_cache", {})
    log_id = cache.get(decision.incident_id, "unknown")

    if log_id != "unknown":
        try:
            existing = logger.get_by_log_id(log_id)
            if existing is not None:
                updated = existing.model_copy(update={"operator_decision": decision})
                logger.update_operator_decision(log_id, updated)
        except Exception:
            pass

    return FeedbackResponse(ok=True, log_id=log_id)
