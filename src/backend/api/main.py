"""T090 — FastAPI application — Sistema de apoyo a la decisión 112 CyL.

Endpoints:
  POST /predict  → IncidentInput → PredictResponse (OperatorRecommendation + log_id)
  POST /feedback → OperatorDecision → FeedbackResponse
  GET  /healthz  → HealthResponse
  GET  /version  → VersionResponse
"""
from __future__ import annotations

import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # inserta src/ → backend importable

from fastapi import FastAPI

from backend.api.routes import feedback, health, predict, predict_stream  # type: ignore[import]
from backend.logging.inference_logger import InferenceLogger  # type: ignore[import]

_LOG_DIR = Path(__file__).resolve().parents[3] / "artifacts" / "logs"
_DB_PATH = _LOG_DIR / "inference.db"
_JSONL_PATH = _LOG_DIR / "inference.jsonl"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Inicializa el logger y el cliente LLM al arrancar."""
    import logging as _logging

    _log = _logging.getLogger(__name__)

    app.state.logger = InferenceLogger(db_path=_DB_PATH, jsonl_path=_JSONL_PATH)
    app.state.log_cache: dict[str, str] = {}

    # Inicializar wrapper LLM — si Ollama no está disponible, queda en None (modo degradado)
    try:
        from capa3_llm_mcp.llm.qwen_wrapper import QwenWrapper  # type: ignore[import]

        wrapper = QwenWrapper()
        if wrapper.is_available():
            app.state.llm = wrapper
            _log.info("LLM disponible: Qwen2.5-7B-Instruct vía Ollama")
        else:
            app.state.llm = None
            _log.warning("Ollama no disponible → modo degradado")
    except Exception as exc:
        app.state.llm = None
        _log.warning("Error al inicializar LLM: %s → modo degradado", exc)

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
app.include_router(predict_stream.router)
app.include_router(feedback.router)
app.include_router(health.router)


@app.get("/.well-known/agent.json", include_in_schema=False)
def agent_card() -> dict:
    """Agent Card compatible con A2A Protocol (Agent2Agent §4.3).

    Permite el descubrimiento programático de las capacidades del sistema
    por agentes externos, siguiendo el estándar emergente Agent2Agent.

    Referencia: arXiv:2505.02279v2 — Survey of Agent Interoperability Protocols.
    """
    return {
        "id": "sistema-apoyo-emergencias-112-v1",
        "name": "Sistema de Apoyo a la Decisión 112 CyL",
        "version": "0.1.0",
        "status": "live",
        "capabilities": [
            {
                "name": "priorizar_incidente",
                "description": "Clasifica un incidente de emergencia con prioridad P1-P4",
                "endpoint": "/predict",
                "method": "POST",
            },
            {
                "name": "priorizar_incidente_stream",
                "description": "Clasificación con SSE — muestra progreso por capas y tokens LLM",
                "endpoint": "/predict/stream",
                "method": "POST",
            },
        ],
        "protocols": ["MCP", "A2A-lite"],
        "mcpTools": ["search_normative", "cite_legal_basis", "get_rule_details"],
    }


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=False)
