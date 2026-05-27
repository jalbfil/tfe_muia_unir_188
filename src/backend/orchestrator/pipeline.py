"""T091 — Pipeline orquestador: encadena Capa 1 → Capa 2 → Capa 3 + logging.

Las Capas 1, 2 y 3 se ejecutan utilizando las implementaciones reales y
modelos entrenados y validados del monorepo.
"""
from __future__ import annotations

import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # inserta src/ → contracts/backend importables

from ulid import ULID  # type: ignore[import]

from contracts import (  # type: ignore[import]
    IncidentInput,
    InferenceLog,
    OperatorRecommendation,
    compute_input_hash,
)

from capa1_nlp.inference.feature_extractor import FeatureExtractor
from capa2_rulefit.inference.predictor import predict

# Instancia global única de extracción de variables operativas de la Capa 1
_FEATURE_EXTRACTOR = FeatureExtractor()

# Capa 3 explainer (puede estar ausente en entornos sin LLM)
try:
    from capa3_llm_mcp.degraded import degraded_explain as _degraded  # type: ignore[import]
    from capa3_llm_mcp.explainer import explain as _explain  # type: ignore[import]

    _CAPA3_AVAILABLE = True
except ImportError:  # pragma: no cover
    _CAPA3_AVAILABLE = False

_MODEL_VERSION_CAPA3 = "0.1.0"
_CHROMA_DIR = Path(__file__).resolve().parents[3] / "artifacts" / "rag" / "chroma"


def run_pipeline(
    incident: IncidentInput,
    *,
    llm: object | None = None,
) -> tuple[OperatorRecommendation, InferenceLog]:
    """Ejecuta el pipeline completo para un incidente y devuelve recomendación + log.

    Args:
        incident: Input validado del incidente.
        llm: Cliente LLM inyectado. Si None o no disponible, usa modo degradado.

    Returns:
        Tupla (OperatorRecommendation, InferenceLog) totalmente validados.
    """
    t_start = datetime.now(tz=UTC)
    t0_total = time.perf_counter()

    # ── Capa 1: extracción de características ─────────────────────────────
    t0_c1 = time.perf_counter()
    features = _FEATURE_EXTRACTOR.extract_features(incident)
    latency_c1 = (time.perf_counter() - t0_c1) * 1000

    # ── Capa 2: recomendación de prioridad ────────────────────────────────
    t0_c2 = time.perf_counter()
    recommendation = predict(features)
    latency_c2 = (time.perf_counter() - t0_c2) * 1000

    # ── Capa 3: explicación LLM + MCP (con fallback degradado) ────────────
    capa3_output: OperatorRecommendation | None = None

    latency_c3: float = 0.0

    t0_c3 = time.perf_counter()
    if _CAPA3_AVAILABLE and llm is not None:
        try:
            incident_text = f"{incident.texto_titulo}. {incident.texto_descripcion}"
            capa3_output = _explain(
                recommendation,
                incident_text,
                llm=llm,
                chroma_dir=_CHROMA_DIR,
            )
        except Exception:
            capa3_output = None

    if capa3_output is None and _CAPA3_AVAILABLE:
        capa3_output = _degraded(recommendation)
    elif capa3_output is None:
        # Capa 3 no importable: modo degradado manual mínimo
        capa3_output = _build_minimal_recommendation(recommendation, incident.incident_id)

    latency_c3 = (time.perf_counter() - t0_c3) * 1000
    latency_total = (time.perf_counter() - t0_total) * 1000
    t_end = datetime.now(tz=UTC)

    # ── InferenceLog ──────────────────────────────────────────────────────
    log_id = str(ULID())
    input_hash = compute_input_hash(incident.model_dump_json())

    model_versions: dict[str, str] = {
        "capa1": features.model_version_capa1,
        "capa2": recommendation.model_version_capa2,
        "capa3": _MODEL_VERSION_CAPA3,
    }

    latencias: dict[str, float] = {
        "capa1": latency_c1,
        "capa2": latency_c2,
        "capa3": latency_c3,
        "total": latency_total,
    }

    tools_invoked: list[str] = list(capa3_output.llm_metadata.tools_invoked) if capa3_output else []

    log = InferenceLog(
        log_id=log_id,
        incident_id=incident.incident_id,
        input_hash=input_hash,
        capa1_output=features,
        capa2_output=recommendation,
        capa3_output=capa3_output,
        latencias_ms=latencias,
        model_versions=model_versions,
        tools_invoked=tools_invoked,
        timestamp_start=t_start,
        timestamp_end=t_end,
    )

    return capa3_output, log


def _build_minimal_recommendation(
    rec: object,
    incident_id: str,
) -> OperatorRecommendation:
    """Fallback cuando la Capa 3 no es importable (entorno sin deps de capa3)."""
    from contracts import (  # type: ignore[import]
        LegalCitation,
        LLMMetadata,
        NormaID,
        OperatorRecommendation,
    )

    priority = rec.priority_recommended  # type: ignore[attr-defined]

    citation_needed = priority.value in ("P1", "P2")  # type: ignore[union-attr]
    citations: list[LegalCitation] = []
    if citation_needed:
        citations = [
            LegalCitation(
                norma_id=NormaID.LEY_17_2015,
                articulo_o_seccion="Art. 4",
                texto_relevante="Sistema de protección civil en situaciones de riesgo vital.",
                url_oficial="https://www.boe.es/buscar/act.php?id=BOE-A-2015-8268",
            )
        ]

    return OperatorRecommendation(
        incident_id=incident_id,
        priority_recommended=priority,
        explanation_text=(
            f"[MODO DEGRADADO] Prioridad recomendada: {priority.value}. "
            "El módulo de explicación LLM no está disponible. "
            "Consulte el manual operativo para la actuación según protocolo."
        ),
        actuation_hints=[
            f"Aplicar protocolo {priority.value} según PLANCAL.",
            "Supervisión humana obligatoria (Principio II).",
        ],
        legal_citations=citations,
        llm_metadata=LLMMetadata(
            llm_model="degraded-static-v0.1.0",
            temperature=0.0,
            tools_invoked=[],
        ),
        model_version_capa3=_MODEL_VERSION_CAPA3,
    )
