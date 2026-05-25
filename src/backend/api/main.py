"""T090 — FastAPI application — Sistema de apoyo a la decisión 112 CyL.

Endpoints:
  POST /predict  → IncidentInput → PredictResponse (OperatorRecommendation + log_id)
  POST /feedback → OperatorDecision → FeedbackResponse
  GET  /healthz  → HealthResponse
  GET  /version  → VersionResponse
"""
from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from fastapi import FastAPI

from backend.api.routes import feedback, health, predict  # type: ignore[import]
from backend.logging.inference_logger import InferenceLogger  # type: ignore[import]

_LOG_DIR = Path(__file__).resolve().parents[4] / "artifacts" / "logs"
_DB_PATH = _LOG_DIR / "inference.db"
_JSONL_PATH = _LOG_DIR / "inference.jsonl"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Inicializa el logger y el cliente LLM al arrancar."""
    app.state.logger = InferenceLogger(db_path=_DB_PATH, jsonl_path=_JSONL_PATH)
    app.state.llm = None  # Sin LLM en v0.1.0-stub; se inyecta en producción
    app.state.log_cache: dict[str, str] = {}
    yield
    # Cleanup (si fuera necesario)


app = FastAPI(
    title="112 CyL Decision Support API",
    version="0.1.0",
    description=(
        "Sistema de apoyo a la decisión para puestos de mando de emergencias civiles. "
        "Motor de priorización interpretable de tres capas."
    ),
    lifespan=lifespan,
)

app.include_router(predict.router)
app.include_router(feedback.router)
app.include_router(health.router)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=False)
