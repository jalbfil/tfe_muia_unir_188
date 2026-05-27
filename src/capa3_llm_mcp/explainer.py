"""T081 — Orquestador Capa 3: PriorityRecommendation → OperatorRecommendation.

Flujo nominal:
    1. Busca contexto normativo relevante en RAG (search_normative).
    2. Recoge citas legales desde los normative_anchors de reglas activadas.
    3. Construye prompt: system_prompt + few-shots + contexto.
    4. Llama al LLM (QwenWrapper) → JSON con explanation_text + hints.
    5. Parsea y valida contra el contrato OperatorRecommendation.

Flujo degradado (LLM no disponible):
    - Llama a `degraded_explain()` → explicación estática, siempre válida.
    - El campo `confidence_disclaimer` indica el modo degradado.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
import time
from collections.abc import Generator
from pathlib import Path

# ── imports de contratos ──────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from contracts import (  # type: ignore[import]
    LegalCitation,
    LLMMetadata,
    NormaID,
    OperatorRecommendation,
    Priority,
    PriorityRecommendation,
)

from .degraded import degraded_explain
from .llm.qwen_wrapper import QwenWrapper
from .mcp_server.tools.cite_legal_basis import cite_legal_basis
from .mcp_server.tools.search_normative import search_normative
from .prompts.few_shots import FEW_SHOTS
from .prompts.system_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_SLA_MS = 2_000.0  # NFR-009: p95 ≤ 2000 ms
_MODEL_VERSION = "0.1.0"
_LLM_MODEL_NAME = "ollama-local"

# Caché de explicaciones por sesión. Clave: SHA-256(texto_incidente + prioridad).
_EXPLAIN_CACHE: dict[str, OperatorRecommendation] = {}

# Regex para extraer JSON del output del LLM (puede incluir texto antes/después)
_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


# ── helpers ───────────────────────────────────────────────────────────────────

def _collect_citations(rec: PriorityRecommendation) -> list[LegalCitation]:
    """Construye LegalCitation para cada NormaID único en las reglas activadas."""
    seen: set[str] = set()
    citations: list[LegalCitation] = []
    for rule in rec.activated_rules:
        for norma in rule.normative_anchors:
            nid = str(norma)
            if nid in seen:
                continue
            seen.add(nid)
            raw = cite_legal_basis(nid)
            citations.append(
                LegalCitation(
                    norma_id=norma,
                    articulo_o_seccion=raw["articulo_o_seccion"],
                    texto_relevante=raw["texto_relevante"],
                    url_oficial=raw["url_oficial"] or None,
                )
            )
    # Garantía P1/P2: ≥1 cita
    if not citations and rec.priority_recommended in (Priority.P1, Priority.P2):
        raw = cite_legal_basis(NormaID.LEY_17_2015)
        citations.append(
            LegalCitation(
                norma_id=NormaID.LEY_17_2015,
                articulo_o_seccion=raw["articulo_o_seccion"],
                texto_relevante=raw["texto_relevante"],
                url_oficial=raw["url_oficial"],
            )
        )
    return citations


def _build_context_block(
    rec: PriorityRecommendation,
    incident_text: str,
    rag_chunks: list[dict],
) -> str:
    """Ensambla el bloque de contexto para el user message."""
    priority_label = rec.priority_recommended.value  # "P1" / "P2" / ...

    rules_lines = "\n".join(f"- {r.human_text}" for r in rec.activated_rules[:5]) or (
        "- Sin evidencias adicionales estructuradas."
    )

    rag_lines = "\n".join(
        f"- [{c['norma_id']} {c['articulo']}] {c['text'][:200]}…"
        for c in rag_chunks[:3]
    ) or "- (corpus no disponible)"

    return (
        f"INCIDENTE: \"{incident_text}\"\n"
        f"PRIORIDAD RECOMENDADA: {priority_label}\n"
        f"EVIDENCIAS OPERATIVAS:\n{rules_lines}\n"
        f"FRAGMENTOS NORMATIVOS:\n{rag_lines}\n"
        "Devuelve solo el JSON solicitado."
    )


def _build_messages(
    rec: PriorityRecommendation,
    incident_text: str,
    rag_chunks: list[dict],
) -> list[dict[str, str]]:
    """Construye el historial de mensajes: system + few-shots + user."""
    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for user_ctx, assistant_resp in FEW_SHOTS:
        messages.append({"role": "user", "content": user_ctx})
        messages.append({"role": "assistant", "content": assistant_resp})
    context = _build_context_block(rec, incident_text, rag_chunks)
    messages.append({"role": "user", "content": context})
    return messages


def _parse_llm_output(raw: str) -> dict:
    """Extrae el JSON del output del LLM; devuelve {} si el parsing falla."""
    match = _JSON_RE.search(raw)
    if not match:
        logger.warning("LLM output no contiene JSON válido: %.200s", raw)
        raw = raw.strip()
        if len(raw) >= 20:
            return {
                "explanation_text": raw[:600],
                "actuation_hints": [],
                "confidence_disclaimer": (
                    "Respuesta LLM convertida a formato contractual por no venir en JSON."
                ),
            }
        return {}
    try:
        parsed = json.loads(match.group())
        explanation = str(parsed.get("explanation_text", "")).strip()
        if len(explanation) < 20:
            logger.warning("explanation_text demasiado corto: %r", explanation)
            return {}
        return parsed
    except json.JSONDecodeError as exc:
        logger.warning("JSONDecodeError en output LLM: %s", exc)
        return {}


def _cache_key(incident_text: str, priority: str) -> str:
    """Genera clave SHA-256 para el caché de explicaciones."""
    return hashlib.sha256(f"{incident_text}||{priority}".encode()).hexdigest()


def _build_operator_result(
    rec: PriorityRecommendation,
    parsed: dict,
    citations: list[LegalCitation],
    rag_chunks: list[dict],
    llm_model_name: str = _LLM_MODEL_NAME,
) -> OperatorRecommendation:
    """Construye OperatorRecommendation a partir del JSON parseado del LLM."""
    explanation_text = parsed["explanation_text"][:1200]
    actuation_hints = [str(h)[:200] for h in parsed.get("actuation_hints", [])[:6]]
    disclaimer = parsed.get("confidence_disclaimer")
    if disclaimer:
        disclaimer = str(disclaimer)[:300]
    tools_used = ["search_normative", "cite_legal_basis"] if rag_chunks or citations else []
    return OperatorRecommendation(
        incident_id=rec.incident_id,
        priority_recommended=rec.priority_recommended,
        explanation_text=explanation_text,
        legal_citations=citations,
        actuation_hints=actuation_hints,
        activated_rules_summary=[r.human_text[:200] for r in rec.activated_rules[:5]],
        confidence_disclaimer=disclaimer,
        model_version_capa3=_MODEL_VERSION,
        llm_metadata=LLMMetadata(
            llm_model=llm_model_name,
            temperature=0.0,
            tools_invoked=tools_used,
        ),
    )


# ── API pública ───────────────────────────────────────────────────────────────

def explain(
    rec: PriorityRecommendation,
    incident_text: str,
    *,
    llm: QwenWrapper | None = None,
    chroma_dir: Path | None = None,
) -> OperatorRecommendation:
    """Genera la explicación para el operador del 112.

    Args:
        rec:           Salida de Capa 2 (PriorityRecommendation).
        incident_text: Texto libre del incidente (para RAG + contexto LLM).
        llm:           Instancia de QwenWrapper; si None se crea una por defecto.
        chroma_dir:    Directorio ChromaDB; si None usa el predeterminado.

    Returns:
        OperatorRecommendation válido según contrato E-04.

    Raises:
        SLABreachWarning: Si la latencia supera 2000 ms p95 (loguea warning).
    """
    t0 = time.perf_counter()

    if llm is None:
        llm = QwenWrapper()

    # Modo degradado si el modelo no está disponible
    if not llm.is_available():
        logger.info("LLM no disponible → modo degradado (incident_id=%s)", rec.incident_id)
        result = degraded_explain(rec)
        _check_sla(rec.incident_id, t0)
        return result

    # Caché de sesión: evita invocar el LLM para textos ya procesados
    _ckey = _cache_key(incident_text, rec.priority_recommended.value)
    if _ckey in _EXPLAIN_CACHE:
        logger.info("Cache hit (incident_id=%s)", rec.incident_id)
        _check_sla(rec.incident_id, t0)
        return _EXPLAIN_CACHE[_ckey]

    # Contexto RAG
    rag_chunks = search_normative(incident_text, n=3)

    # Citas legales desde reglas
    citations = _collect_citations(rec)

    # Prompt
    messages = _build_messages(rec, incident_text, rag_chunks)

    # Llamada LLM
    try:
        raw_output = llm.chat(messages, max_tokens=600, temperature=0.0)
    except Exception as exc:
        logger.error("Error en LLM chat: %s → modo degradado", exc)
        result = degraded_explain(rec)
        _check_sla(rec.incident_id, t0)
        return result

    # Parsear output
    parsed = _parse_llm_output(raw_output)
    if not parsed:
        logger.warning("Fallback a modo degradado por JSON inválido (incident_id=%s)", rec.incident_id)
        result = degraded_explain(rec)
        _check_sla(rec.incident_id, t0)
        return result

    llm_model_name = getattr(llm, "model_name", _LLM_MODEL_NAME)
    if not isinstance(llm_model_name, str):
        llm_model_name = _LLM_MODEL_NAME
    result = _build_operator_result(rec, parsed, citations, rag_chunks, llm_model_name)
    _EXPLAIN_CACHE[_ckey] = result
    _check_sla(rec.incident_id, t0)
    return result


def explain_stream(
    rec: PriorityRecommendation,
    incident_text: str,
    *,
    llm: QwenWrapper | None = None,
    chroma_dir: Path | None = None,
) -> Generator[dict, None, None]:
    """Variante streaming de explain(): yields tokens del LLM y el resultado final.

    Yields dicts con estructura:
        {"type": "token",  "content": str}                  — token generado por LLM
        {"type": "cached", "content": ""}                   — cache hit
        {"type": "result", "content": OperatorRecommendation} — resultado final

    Si el LLM no está disponible, emite directamente el resultado degradado.
    Ideal para endpoints SSE donde se quiere mostrar progreso al usuario.
    """
    t0 = time.perf_counter()

    if llm is None:
        llm = QwenWrapper()

    if not llm.is_available():
        yield {"type": "result", "content": degraded_explain(rec)}
        return

    _ckey = _cache_key(incident_text, rec.priority_recommended.value)
    if _ckey in _EXPLAIN_CACHE:
        logger.info("Cache hit stream (incident_id=%s)", rec.incident_id)
        yield {"type": "cached", "content": ""}
        yield {"type": "result", "content": _EXPLAIN_CACHE[_ckey]}
        return

    rag_chunks = search_normative(incident_text, n=3)
    citations = _collect_citations(rec)
    messages = _build_messages(rec, incident_text, rag_chunks)

    collected: list[str] = []
    try:
        for token in llm.chat_stream(messages, max_tokens=600, temperature=0.0):
            collected.append(token)
            yield {"type": "token", "content": token}
    except Exception as exc:
        logger.error("Error en streaming LLM: %s → modo degradado", exc)
        yield {"type": "result", "content": degraded_explain(rec)}
        _check_sla(rec.incident_id, t0)
        return

    raw_output = "".join(collected)
    parsed = _parse_llm_output(raw_output)
    if not parsed:
        result = degraded_explain(rec)
    else:
        llm_model_name = getattr(llm, "model_name", _LLM_MODEL_NAME)
        if not isinstance(llm_model_name, str):
            llm_model_name = _LLM_MODEL_NAME
        result = _build_operator_result(rec, parsed, citations, rag_chunks, llm_model_name)
        _EXPLAIN_CACHE[_ckey] = result

    yield {"type": "result", "content": result}
    _check_sla(rec.incident_id, t0)


def _check_sla(incident_id: str, t0: float) -> None:
    elapsed_ms = (time.perf_counter() - t0) * 1000
    if elapsed_ms > _SLA_MS:
        logger.warning(
            "SLA Capa 3 superado: %.0f ms > %.0f ms (incident_id=%s)",
            elapsed_ms,
            _SLA_MS,
            incident_id,
        )
