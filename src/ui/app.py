"""T101 — Streamlit UI — Sistema de apoyo a la decisión 112 CyL.

Formulario de incidente → recomendación con explicación + reglas + citas →
decisión del operador (aceptar / modificar / rechazar).

Lanzar:
    streamlit run src/ui/app.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
import streamlit as st

# ── path setup ────────────────────────────────────────────────────────────────
_UI_DIR = Path(__file__).resolve().parent
_SRC_DIR = _UI_DIR.parent
sys.path.insert(0, str(_SRC_DIR))

from ulid import ULID  # type: ignore[import]

from contracts import (  # type: ignore[import]
    CategoriaPreliminar,
    IncidentInput,
    OperatorDecision,
    OperatorRecommendation,
    Priority,
    ProvinciaCyL,
)
from backend.orchestrator.pipeline import run_pipeline  # type: ignore[import]
from backend.logging.inference_logger import InferenceLogger  # type: ignore[import]

# ── logger singleton ──────────────────────────────────────────────────────────
_LOG_DIR = _SRC_DIR.parent / "artifacts" / "logs"

@st.cache_resource
def _get_logger() -> InferenceLogger:
    return InferenceLogger(
        db_path=_LOG_DIR / "inference.db",
        jsonl_path=_LOG_DIR / "inference.jsonl",
    )


@st.cache_resource
def _get_llm():
    """Singleton del QwenWrapper para la sesión Streamlit.

    Reutiliza la conexión a Ollama entre llamadas sucesivas en lugar de
    crear una instancia nueva por cada análisis.
    """
    try:
        from capa3_llm_mcp.llm.qwen_wrapper import QwenWrapper  # type: ignore[import]
        return QwenWrapper()
    except Exception:
        return None


@st.cache_data(ttl=60)
def _llm_available() -> bool:
    """Comprueba cada 60 s si Ollama está operativo."""
    try:
        llm = _get_llm()
        return llm is not None and llm.is_available()
    except Exception:
        return False


# ── helpers ───────────────────────────────────────────────────────────────────

_PRIORITY_COLOR = {
    "P1": "#d32f2f",  # rojo
    "P2": "#f57c00",  # naranja
    "P3": "#fbc02d",  # amarillo
    "P4": "#388e3c",  # verde
}
_PRIORITY_LABEL = {
    "P1": "🔴 P1 — CRÍTICA",
    "P2": "🟠 P2 — URGENTE",
    "P3": "🟡 P3 — IMPORTANTE",
    "P4": "🟢 P4 — BANAL",
}
_CONFIDENCE_BADGE = {
    "HIGH": "🟢 ALTA",
    "MEDIUM": "🟡 MEDIA",
    "LOW": "🟠 BAJA",
    "UNKNOWN": "⚪ DESCONOCIDA",
}


def _priority_badge(priority: str) -> str:
    color = _PRIORITY_COLOR.get(priority, "#9e9e9e")
    label = _PRIORITY_LABEL.get(priority, priority)
    return (
        f"<div style='background:{color};color:white;padding:14px 20px;"
        f"border-radius:8px;font-size:1.5rem;font-weight:bold;"
        f"text-align:center;margin-bottom:12px'>{label}</div>"
    )

def _stream_events(url: str, payload: dict):
    """Genera pares (event_type, data) parseando un endpoint SSE vía POST."""
    with requests.post(url, json=payload, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        event_type = ""
        for raw_line in resp.iter_lines(decode_unicode=True):
            if raw_line.startswith("event:"):
                event_type = raw_line[6:].strip()
            elif raw_line.startswith("data:"):
                yield event_type, raw_line[5:].strip()
                event_type = ""

# ── page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="112 CyL — Sistema de apoyo a la decisión",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/112_logo.svg/200px-112_logo.svg.png",
             width=80, caption="112 Castilla y León")
    st.title("Sistema IA\nde apoyo a la decisión")
    st.markdown("**Versión:** 0.1.0")
    st.markdown("**Motor:** Reglas interpretables + LLM local")
    if _llm_available():
        st.success("🟢 LLM activo — Ollama")
    else:
        st.warning("🟡 LLM no disponible — modo degradado")
    st.markdown("---")
    st.warning(
        "Este sistema es un **apoyo** a la decisión. "
        "La decisión final corresponde siempre al operador humano."
    )
    st.markdown("---")
    st.markdown("**Principio II** — Supervisión humana")
    st.markdown("**LEY 17/2015** — Protección Civil")
    st.divider()
    st.toggle(
        "🔴 Streaming (SSE)",
        value=False,
        key="stream_mode",
        help="Muestra progreso en tiempo real usando /predict/stream. Requiere el backend activo.",
    )
    if st.session_state.get("stream_mode", False):
        st.text_input("URL backend", value="http://localhost:8000", key="api_url")

    st.caption("TFE MUIA UNIR · 2026")

# ── main layout ───────────────────────────────────────────────────────────────

st.title("🚨 Sistema de Apoyo a la Decisión — 112 CyL")
st.caption("Introduce los datos del incidente para obtener una recomendación de prioridad.")

tab_form, tab_history = st.tabs(["📋 Nueva incidencia", "📂 Historial de sesión"])

# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — FORMULARIO DE INCIDENTE
# ────────────────────────────────────────────────────────────────────────────

with tab_form:
    col_form, col_result = st.columns([1, 1], gap="large")

    # ── Columna izquierda: formulario ──────────────────────────────────────

    with col_form:
        st.subheader("Datos del incidente")

        with st.form("incident_form", clear_on_submit=False):
            auto_id = str(ULID())
            incident_id = st.text_input(
                "ID incidente (ULID)",
                value=auto_id,
                help="Generado automáticamente. Puedes modificarlo.",
                max_chars=64,
            )

            texto_titulo = st.text_input(
                "Título del incidente *",
                placeholder="Ej: Accidente grave N-122",
                max_chars=200,
            )

            texto_descripcion = st.text_area(
                "Descripción del incidente",
                placeholder=(
                    "Describe brevemente: tipo de evento, víctimas, "
                    "estado aparente, condiciones del entorno…"
                ),
                height=120,
                max_chars=5000,
            )

            col_cat, col_prov = st.columns(2)
            with col_cat:
                categoria = st.selectbox(
                    "Categoría preliminar",
                    options=[None] + list(CategoriaPreliminar),
                    format_func=lambda x: "— Sin clasificar —" if x is None else str(x.value),
                )
            with col_prov:
                provincia = st.selectbox(
                    "Provincia",
                    options=[None] + list(ProvinciaCyL),
                    format_func=lambda x: "— No especificada —" if x is None else str(x.value),
                )

            col_loc, col_op = st.columns(2)
            with col_loc:
                localidad = st.text_input("Localidad", max_chars=120)
            with col_op:
                operador_id = st.text_input(
                    "ID operador *", value="OP-CYL-001", max_chars=64
                )

            col_lat, col_lon = st.columns(2)
            with col_lat:
                lat_str = st.text_input(
                    "Latitud", placeholder="41.6235 (opcional)"
                )
            with col_lon:
                lon_str = st.text_input(
                    "Longitud", placeholder="-4.7268 (opcional)"
                )

            submitted = st.form_submit_button(
                "🔍 Analizar incidente", type="primary", use_container_width=True
            )

        # ── procesamiento del formulario ───────────────────────────────────

        if submitted:
            errors = []
            if not texto_titulo.strip():
                errors.append("El **título del incidente** es obligatorio.")
            if not operador_id.strip():
                errors.append("El **ID de operador** es obligatorio.")

            lat: float | None = None
            lon: float | None = None
            if lat_str.strip() or lon_str.strip():
                try:
                    lat = float(lat_str.strip())
                    lon = float(lon_str.strip())
                except ValueError:
                    errors.append("Latitud y longitud deben ser valores numéricos.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                try:
                    incident = IncidentInput(
                        incident_id=incident_id.strip(),
                        texto_titulo=texto_titulo.strip(),
                        texto_descripcion=texto_descripcion.strip(),
                        categoria_preliminar=categoria,
                        latitud=lat,
                        longitud=lon,
                        localidad=localidad.strip() or None,
                        provincia=provincia,
                        fecha_incidente=datetime.now(tz=timezone.utc),
                        operador_id=operador_id.strip(),
                    )
                except Exception as exc:
                    st.error(f"Error al construir el incidente: {exc}")
                    st.stop()

                if st.session_state.get("stream_mode", False):
                    # ── Modo streaming: SSE desde /predict/stream ──────────
                    _api = st.session_state.get("api_url", "http://localhost:8000")
                    _status = st.empty()
                    _priority = st.empty()
                    _tokens = st.empty()
                    _token_buf = ""
                    _result_data = None
                    try:
                        for _ev, _data in _stream_events(
                            f"{_api}/predict/stream",
                            incident.model_dump(mode="json"),
                        ):
                            if _ev == "status":
                                _status.info(f"⏳ {_data}")
                            elif _ev == "priority":
                                _priority.markdown(
                                    _priority_badge(_data), unsafe_allow_html=True
                                )
                            elif _ev == "token":
                                _token_buf += json.loads(_data)
                                _tokens.text_area(
                                    "🧠 Generando explicación…",
                                    value=_token_buf[-600:],
                                    height=120,
                                    disabled=True,
                                    key=f"live_tok_{len(_token_buf)}",
                                )
                            elif _ev == "result":
                                _result_data = json.loads(_data)
                            elif _ev == "done":
                                break
                    except requests.exceptions.ConnectionError:
                        st.error(
                            f"Sin conexión al backend ({_api}). "
                            "Inicia el servidor: `uvicorn backend.api.main:app --port 8000`"
                        )
                    except Exception as exc:
                        st.error(f"Error en streaming: {exc}")

                    _status.empty()
                    _tokens.empty()

                    if _result_data:
                        recommendation = OperatorRecommendation.model_validate(_result_data)
                        st.session_state["last_recommendation"] = recommendation
                        st.session_state["last_log"] = None  # sin InferenceLog en modo streaming
                        st.session_state["last_incident"] = incident
                        st.session_state["decision_submitted"] = False
                        st.rerun()
                else:
                    # ── Modo síncrono: pipeline directo (por defecto) ──────
                    with st.spinner("Analizando incidente…"):
                        try:
                            recommendation, log = run_pipeline(incident, llm=_get_llm())
                            _get_logger().log(log)
                            st.session_state["last_recommendation"] = recommendation
                            st.session_state["last_log"] = log
                            st.session_state["last_incident"] = incident
                            st.session_state["decision_submitted"] = False
                        except Exception as exc:
                            st.error(f"Error al procesar el incidente: {exc}")

    # ── Columna derecha: resultado ─────────────────────────────────────────

    with col_result:
        st.subheader("Recomendación del sistema")

        if "last_recommendation" not in st.session_state:
            st.info("Rellena el formulario y pulsa **Analizar incidente** para obtener la recomendación.")
        else:
            rec = st.session_state["last_recommendation"]
            log = st.session_state["last_log"]
            incident: IncidentInput = st.session_state["last_incident"]
            decision_submitted: bool = st.session_state.get("decision_submitted", False)

            # ── Badge de prioridad ─────────────────────────────────────────
            st.markdown(_priority_badge(rec.priority_recommended.value), unsafe_allow_html=True)

            col_conf, col_mode = st.columns(2)
            with col_conf:
                if log is not None and log.capa2_output is not None:
                    conf_val = log.capa2_output.confidence_level.value
                    st.metric("Confianza", _CONFIDENCE_BADGE.get(conf_val, conf_val))
                else:
                    st.metric("Confianza", "⚪ N/D")
            with col_mode:
                llm_model = (rec.llm_metadata.llm_model if rec.llm_metadata else "") or ""
                degraded = "degraded" in llm_model.lower()
                st.metric("Modo LLM", "⚠️ Degradado" if degraded else "✅ Activo")

            # ── Explicación ────────────────────────────────────────────────
            with st.expander("📄 Explicación", expanded=True):
                st.write(rec.explanation_text)

            # ── Reglas activadas ───────────────────────────────────────────
            activated = rec.activated_rules_summary
            if activated:
                with st.expander(f"⚙️ Reglas activadas ({len(activated)})", expanded=True):
                    for rule_text in activated:
                        st.markdown(f"- {rule_text}")
            else:
                with st.expander("⚙️ Reglas activadas"):
                    capa2_rules = log.capa2_output.activated_rules
                    if capa2_rules:
                        for rule in capa2_rules:
                            st.markdown(f"- **{rule.rule_id}**: {rule.human_text} (w={rule.weight:.2f})")
                    else:
                        st.caption("Sin reglas activadas documentadas.")

            # ── Citas legales ──────────────────────────────────────────────
            if rec.legal_citations:
                with st.expander(f"⚖️ Citas normativas ({len(rec.legal_citations)})", expanded=True):
                    for cita in rec.legal_citations:
                        norma = cita.norma_id.value
                        art = f" · {cita.articulo_o_seccion}" if cita.articulo_o_seccion else ""
                        url = str(cita.url_oficial) if cita.url_oficial else None
                        if url:
                            st.markdown(f"📌 [{norma}{art}]({url}): _{cita.texto_relevante}_")
                        else:
                            st.markdown(f"📌 **{norma}{art}**: _{cita.texto_relevante}_")

            # ── Pistas de actuación ────────────────────────────────────────
            if rec.actuation_hints:
                with st.expander("🎯 Pistas de actuación", expanded=True):
                    for hint in rec.actuation_hints:
                        st.markdown(f"▶ {hint}")

            # ── Metadatos técnicos ─────────────────────────────────────────
            with st.expander("🔧 Metadatos técnicos"):
                if log is not None:
                    st.json({
                        "log_id": log.log_id,
                        "input_hash": log.input_hash[:16] + "…",
                        "latencias_ms": {k: round(v, 1) for k, v in log.latencias_ms.items()},
                        "model_versions": log.model_versions,
                        "tools_invoked": log.tools_invoked,
                    })
                else:
                    st.caption("Log no disponible en modo streaming.")
                    st.json({
                        "llm_model": rec.llm_metadata.llm_model,
                        "tools_invoked": rec.llm_metadata.tools_invoked,
                        "model_version_capa3": rec.model_version_capa3,
                    })

            # ── Panel de decisión del operador ────────────────────────────
            st.divider()
            st.subheader("👮 Decisión del operador")

            if decision_submitted:
                st.success("✅ Decisión registrada correctamente.")
            else:
                decision_action = st.radio(
                    "Acción sobre la recomendación:",
                    options=["Aceptar", "Modificar prioridad", "Rechazar"],
                    horizontal=True,
                    key="decision_action",
                )

                priority_final = rec.priority_recommended
                motivo: str | None = None

                if decision_action in ("Modificar prioridad", "Rechazar"):
                    priority_final = st.selectbox(
                        "Prioridad asignada por el operador:",
                        options=list(Priority),
                        index=list(Priority).index(rec.priority_recommended),
                        format_func=lambda p: _PRIORITY_LABEL.get(p.value, p.value),
                        key="priority_override",
                    )
                    motivo = st.text_area(
                        "Motivo de la divergencia *",
                        placeholder="Describe por qué modifica o rechaza la recomendación del sistema…",
                        max_chars=500,
                        key="motivo_divergencia",
                    )

                if st.button("Confirmar decisión", type="primary", key="btn_confirm"):
                    if decision_action in ("Modificar prioridad", "Rechazar") and not (motivo or "").strip():
                        st.error("El motivo de divergencia es obligatorio al modificar o rechazar.")
                    else:
                        try:
                            op_decision = OperatorDecision(
                                incident_id=incident.incident_id,
                                priority_recommended_by_system=rec.priority_recommended,
                                priority_assigned_by_operator=priority_final,
                                motivo_divergencia=motivo or None,
                                operador_id=incident.operador_id,
                                timestamp=datetime.now(tz=timezone.utc),
                            )
                            # Actualiza log con la decisión
                            if log is not None:
                                existing = _get_logger().get_by_log_id(log.log_id)
                                if existing is not None:
                                    updated = existing.model_copy(update={"operator_decision": op_decision})
                                    _get_logger().update_operator_decision(log.log_id, updated)
                                    st.session_state["last_log"] = updated

                            # Añade al historial de sesión
                            history = st.session_state.get("session_history", [])
                            history.append({
                                "log_id": log.log_id if log is not None else "streaming",
                                "incident_id": incident.incident_id,
                                "titulo": incident.texto_titulo,
                                "recomendado": rec.priority_recommended.value,
                                "asignado": priority_final.value,
                                "divergencia": decision_action != "Aceptar",
                            })
                            st.session_state["session_history"] = history
                            st.session_state["decision_submitted"] = True
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Error al registrar la decisión: {exc}")


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — HISTORIAL DE SESIÓN
# ────────────────────────────────────────────────────────────────────────────

with tab_history:
    st.subheader("Incidentes analizados en esta sesión")
    history = st.session_state.get("session_history", [])

    if not history:
        st.info("Todavía no hay incidentes analizados en esta sesión.")
    else:
        import pandas as pd  # lazy import

        df = pd.DataFrame(history)[
            ["log_id", "incident_id", "titulo", "recomendado", "asignado", "divergencia"]
        ]
        df.columns = ["Log ID", "Incidente", "Título", "Sistema", "Operador", "Divergencia"]

        def _color_priority(val: str) -> str:
            colors = {"P1": "background-color:#ffcdd2", "P2": "background-color:#ffe0b2",
                      "P3": "background-color:#fff9c4", "P4": "background-color:#c8e6c9"}
            return colors.get(val, "")

        styled = df.style.applymap(_color_priority, subset=["Sistema", "Operador"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        divergentes = sum(1 for h in history if h["divergencia"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Total analizados", len(history))
        col2.metric("Aceptados", len(history) - divergentes)
        col3.metric("Divergentes", divergentes)
