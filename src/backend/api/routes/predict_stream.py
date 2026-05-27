"""POST /predict/stream — Pipeline de predicción con Server-Sent Events.

Emite eventos SSE durante la ejecución del pipeline:
  event: status   — etapa activa (Capa 1, 2, 3)
  event: priority — prioridad calculada por Capa 2 (P1-P4)
  event: token    — token generado por el LLM (Capa 3, token a token)
  event: result   — OperatorRecommendation final (JSON serializado)
  event: done     — señal de fin de stream

Uso desde Streamlit con sseclient:
    import sseclient, requests
    resp = requests.post("/predict/stream", json=payload, stream=True)
    for event in sseclient.SSEClient(resp).events():
        if event.event == "token": st.write(event.data, end="")
        elif event.event == "result": rec = json.loads(event.data)
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from contracts import IncidentInput  # type: ignore[import]
from backend.orchestrator.stubs import (  # type: ignore[import]
    stub_extract_features,
    stub_predict_priority,
)

try:
    from capa3_llm_mcp.explainer import explain_stream as _explain_stream  # type: ignore[import]
    from capa3_llm_mcp.degraded import degraded_explain as _degraded  # type: ignore[import]

    _CAPA3_AVAILABLE = True
except ImportError:  # pragma: no cover
    _CAPA3_AVAILABLE = False

_CHROMA_DIR = Path(__file__).resolve().parents[4] / "artifacts" / "rag" / "chroma"

router = APIRouter()


def _sse(event: str, data: str) -> str:
    """Formatea una línea SSE conforme a RFC 8895."""
    return f"event: {event}\ndata: {data}\n\n"


@router.post("/predict/stream")
async def predict_stream(incident: IncidentInput, request: Request) -> StreamingResponse:
    """Pipeline de predicción con Server-Sent Events.

    Permite a la UI mostrar el progreso en tiempo real mientras el LLM genera:
    las etapas Capa 1 y Capa 2 son inmediatas (<20 ms); Capa 3 emite tokens
    token a token desde Ollama. En modo degradado emite directamente el resultado.

    Compatible con A2A task lifecycle (submitted → working → completed).
    """
    llm = getattr(request.app.state, "llm", None)

    async def event_generator():
        # ── Capa 1 ─────────────────────────────────────────────────────────
        yield _sse("status", "Capa 1: extracción de características")
        features = await asyncio.to_thread(stub_extract_features, incident)

        # ── Capa 2 ─────────────────────────────────────────────────────────
        yield _sse("status", "Capa 2: cálculo de prioridad")
        rec = await asyncio.to_thread(stub_predict_priority, features)
        yield _sse("priority", rec.priority_recommended.value)

        # ── Capa 3 ─────────────────────────────────────────────────────────
        yield _sse("status", f"Capa 3: explicación normativa ({rec.priority_recommended.value})")

        if not _CAPA3_AVAILABLE or llm is None:
            result = await asyncio.to_thread(_degraded, rec)
            yield _sse("result", result.model_dump_json())
            yield _sse("done", "")
            return

        incident_text = f"{incident.texto_titulo}. {incident.texto_descripcion}"

        # Puente sync→async: ejecuta el generador sincrónico en un thread
        # y pasa los eventos al generador async vía asyncio.Queue.
        q: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def _run_explain() -> None:
            try:
                for evt in _explain_stream(
                    rec, incident_text, llm=llm, chroma_dir=_CHROMA_DIR
                ):
                    loop.call_soon_threadsafe(q.put_nowait, evt)
            finally:
                loop.call_soon_threadsafe(q.put_nowait, None)  # sentinel

        loop.run_in_executor(None, _run_explain)

        result = None
        while True:
            evt = await q.get()
            if evt is None:
                break
            if evt["type"] == "token":
                yield _sse("token", json.dumps(evt["content"]))
            elif evt["type"] == "result":
                result = evt["content"]

        if result is not None:
            yield _sse("result", result.model_dump_json())
        yield _sse("done", "")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Desactiva buffering en nginx/proxies
        },
    )
