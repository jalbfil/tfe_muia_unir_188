"""T101 — Streamlit UI — Sistema de apoyo a la decisión 112 CyL.

Formulario de incidente → recomendación con explicación + reglas + citas →
decisión del operador (aceptar / modificar / rechazar).

Lanzar:
    streamlit run src/ui/app.py
"""
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import requests
import streamlit as st

# ── path setup ────────────────────────────────────────────────────────────────
_UI_DIR = Path(__file__).resolve().parent
_SRC_DIR = _UI_DIR.parent
sys.path.insert(0, str(_SRC_DIR))

from ulid import ULID  # type: ignore[import]

from backend.logging.inference_logger import InferenceLogger  # type: ignore[import]
from backend.orchestrator.pipeline import run_pipeline  # type: ignore[import]
from contracts import (  # type: ignore[import]
    CategoriaPreliminar,
    IncidentInput,
    OperatorDecision,
    OperatorRecommendation,
    Priority,
    ProvinciaCyL,
)

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
    page_title="112 CyL · Asistente CECOP",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS (estética centro de mando) ────────────────────────────────────────────
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.2rem; }
    .stTextArea textarea { font-size: 1.05rem; line-height: 1.45; }
    .cmd-card {
        border-radius: 12px; padding: 18px 22px; margin-bottom: 14px;
        background: var(--background-color); border: 1px solid rgba(128,128,128,0.18);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .cmd-strip {
        padding: 10px 18px; border-radius: 10px; color: white;
        display:flex; justify-content:space-between; align-items:center;
        font-weight:600; margin-bottom: 16px;
    }
    .pill {
        display:inline-block; padding:2px 10px; border-radius:999px;
        font-size:0.78rem; font-weight:600;
        background:rgba(255,255,255,0.18); color:white;
    }
    .rule-row {
        padding:8px 12px; border-left:3px solid #1976d2;
        background: rgba(25,118,210,0.06); border-radius:6px; margin-bottom:6px;
    }
    .step-row {
        padding:8px 12px; border-radius:6px; margin-bottom:6px;
        background: rgba(56,142,60,0.06); border-left:3px solid #388e3c;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── helpers de UI rica ────────────────────────────────────────────────────────

def _command_strip(rec: OperatorRecommendation, incident: IncidentInput, latency_ms: float | None) -> str:
    """Banda superior tipo cabecera de centro de mando."""
    p = rec.priority_recommended.value
    color = _PRIORITY_COLOR.get(p, "#555")
    label = _PRIORITY_LABEL.get(p, p)
    ts = incident.fecha_incidente.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    lat_pill = f"<span class='pill'>⏱ {latency_ms:.0f} ms</span>" if latency_ms is not None else ""
    prov = incident.provincia.value if incident.provincia else "—"
    return (
        f"<div class='cmd-strip' style='background:{color}'>"
        f"<div style='font-size:1.55rem'>{label}</div>"
        f"<div style='display:flex;gap:10px;align-items:center'>"
        f"<span class='pill'>📍 {prov}</span>"
        f"<span class='pill'>🕒 {ts}</span>"
        f"{lat_pill}"
        f"</div></div>"
    )


def _session_counters() -> dict[str, int]:
    history = st.session_state.get("session_history", [])
    counters = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}
    for h in history:
        counters[h.get("recomendado", "")] = counters.get(h.get("recomendado", ""), 0) + 1
    return counters


# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("# 🚨")
    st.markdown("### CECOP · Castilla y León")
    st.caption("Asistente IA de apoyo a la decisión")

    # Reloj UTC en vivo (se refresca con cada rerun)
    _now = datetime.now(tz=UTC)
    st.metric("🕒 Hora UTC", _now.strftime("%H:%M:%S"))

    # Estado del sistema
    st.markdown("#### Estado del sistema")
    col_a, col_b = st.columns(2)
    if _llm_available():
        col_a.success("🟢 LLM")
    else:
        col_a.warning("🟡 LLM")
    col_b.info("🟢 RAG")

    # Métricas de sesión
    _c = _session_counters()
    _total = sum(_c.values())
    st.markdown("#### Sesión actual")
    st.metric("Incidentes", _total)
    col_p1, col_p2 = st.columns(2)
    col_p3, col_p4 = st.columns(2)
    col_p1.metric("🔴 P1", _c["P1"])
    col_p2.metric("🟠 P2", _c["P2"])
    col_p3.metric("🟡 P3", _c["P3"])
    col_p4.metric("🟢 P4", _c["P4"])

    st.divider()
    st.toggle(
        "Streaming en vivo (SSE)",
        value=True,
        key="stream_mode",
        help="Muestra progreso token a token vía /predict/stream.",
    )
    if st.session_state.get("stream_mode", False):
        st.text_input("URL backend", value="http://localhost:8000", key="api_url")

    with st.expander("⚙️ Avanzado"):
        st.text_input("ID operador", value="OP-CYL-001", key="operador_id")
        st.text_input("Override ID incidente", value="", key="incident_id_override",
                      help="Si vacío, se genera un ULID automáticamente.")

    st.divider()
    st.caption(
        "⚖️ **Apoyo a la decisión.** La decisión final corresponde "
        "siempre al operador humano (Principio II · Ley 17/2015)."
    )
    st.caption("TFE MUIA · UNIR · 2026")


# ── header principal ──────────────────────────────────────────────────────────

st.markdown("## 🚨 Asistente CECOP — Triage 112 CyL")
st.caption(
    "Describe la situación tal como te la transmiten. El sistema extrae las señales, "
    "propone una prioridad **P1–P4** y la justifica con normativa vigente."
)

tab_triage, tab_history, tab_about = st.tabs(
    ["🎯 Triage", "📂 Historial", "ℹ️ Sobre el sistema"]
)


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — TRIAGE CONVERSACIONAL
# ────────────────────────────────────────────────────────────────────────────

with tab_triage:

    # ── Entrada conversacional ─────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("#### 📥 Situación recibida")

        descripcion = st.text_area(
            label="Cuéntame qué está ocurriendo",
            placeholder=(
                "Ej: «Llamada de un vecino en Aranda de Duero. Dice que hay humo denso "
                "saliendo de una nave industrial en el polígono Allendeduero. "
                "Se oyen explosiones pequeñas. No hay heridos confirmados todavía.»"
            ),
            height=140,
            label_visibility="collapsed",
            key="descripcion_input",
        )

        col_titulo, col_prov, col_loc = st.columns([2, 1, 1])
        with col_titulo:
            titulo = st.text_input(
                "Título corto *",
                placeholder="Ej: Humo y explosiones en nave industrial",
                max_chars=200,
                key="titulo_input",
            )
        with col_prov:
            provincia = st.selectbox(
                "Provincia",
                options=[None] + list(ProvinciaCyL),
                format_func=lambda x: "— Sin especificar —" if x is None else x.value,
                key="provincia_input",
            )
        with col_loc:
            localidad = st.text_input(
                "Localidad",
                placeholder="Ej: Aranda de Duero",
                max_chars=120,
                key="localidad_input",
            )

        with st.expander("➕ Datos adicionales (opcional)"):
            col_cat, col_lat, col_lon = st.columns(3)
            with col_cat:
                categoria = st.selectbox(
                    "Categoría preliminar",
                    options=[None] + list(CategoriaPreliminar),
                    format_func=lambda x: "— Que la IA la infiera —" if x is None else x.value,
                    key="categoria_input",
                )
            with col_lat:
                lat_str = st.text_input("Latitud", placeholder="41.6235", key="lat_input")
            with col_lon:
                lon_str = st.text_input("Longitud", placeholder="-4.7268", key="lon_input")

        analizar = st.button(
            "🔍 Analizar incidente",
            type="primary",
            use_container_width=True,
            key="btn_analizar",
        )

    # ── Procesamiento ──────────────────────────────────────────────────────
    if analizar:
        errors: list[str] = []
        if not (titulo or "").strip():
            errors.append("El **título** es obligatorio.")
        if not (descripcion or "").strip():
            errors.append("La **descripción** de la situación es obligatoria.")
        operador_id = (st.session_state.get("operador_id") or "OP-CYL-001").strip()
        if not operador_id:
            errors.append("Falta **ID de operador** en el panel Avanzado.")

        lat: float | None = None
        lon: float | None = None
        if (lat_str or "").strip() or (lon_str or "").strip():
            try:
                lat = float(lat_str.strip())
                lon = float(lon_str.strip())
            except ValueError:
                errors.append("Latitud y longitud deben ser numéricas.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            incident_id = (st.session_state.get("incident_id_override") or "").strip() or str(ULID())
            try:
                incident = IncidentInput(
                    incident_id=incident_id,
                    texto_titulo=titulo.strip(),
                    texto_descripcion=descripcion.strip(),
                    categoria_preliminar=categoria,
                    latitud=lat,
                    longitud=lon,
                    localidad=(localidad or "").strip() or None,
                    provincia=provincia,
                    fecha_incidente=datetime.now(tz=UTC),
                    operador_id=operador_id,
                )
            except Exception as exc:
                st.error(f"Error al construir el incidente: {exc}")
                st.stop()

            stream_mode = st.session_state.get("stream_mode", True)

            if stream_mode:
                _api = st.session_state.get("api_url", "http://localhost:8000")

                with st.status("Analizando incidente…", expanded=True) as status:
                    _step1 = st.empty()
                    _step2 = st.empty()
                    _step3 = st.empty()
                    _tok_holder = st.empty()
                    _token_buf = ""
                    _result_data = None
                    _t0 = datetime.now(tz=UTC)
                    try:
                        for _ev, _data in _stream_events(
                            f"{_api}/predict/stream",
                            incident.model_dump(mode="json"),
                        ):
                            if _ev == "status":
                                # Routing visual de las 3 capas
                                msg = _data
                                if "Capa 1" in msg:
                                    _step1.markdown("🔎 **Capa 1** — extracción de señales… ✅")
                                elif "Capa 2" in msg:
                                    _step2.markdown("⚖️ **Capa 2** — prioridad por reglas… ✅")
                                elif "Capa 3" in msg:
                                    _step3.markdown("🧠 **Capa 3** — explicación normativa…")
                            elif _ev == "priority":
                                _step2.markdown(
                                    f"⚖️ **Capa 2** — prioridad por reglas… "
                                    f"**{_data}** asignada ✅"
                                )
                            elif _ev == "token":
                                _token_buf += json.loads(_data)
                                _tok_holder.markdown(
                                    f"<div class='cmd-card' style='max-height:180px;overflow-y:auto;"
                                    f"font-family:monospace;font-size:0.85rem;white-space:pre-wrap'>"
                                    f"{_token_buf[-1200:]}</div>",
                                    unsafe_allow_html=True,
                                )
                            elif _ev == "result":
                                _result_data = json.loads(_data)
                            elif _ev == "done":
                                break
                        status.update(label="Análisis completado", state="complete")
                    except requests.exceptions.ConnectionError:
                        status.update(label="Sin conexión al backend", state="error")
                        st.error(
                            f"Sin conexión al backend ({_api}). "
                            "Inicia: `uvicorn backend.api.main:app --port 8000`"
                        )
                    except Exception as exc:
                        status.update(label="Error en streaming", state="error")
                        st.error(f"Error en streaming: {exc}")

                    _latency = (datetime.now(tz=UTC) - _t0).total_seconds() * 1000

                if _result_data:
                    recommendation = OperatorRecommendation.model_validate(_result_data)
                    st.session_state["last_recommendation"] = recommendation
                    st.session_state["last_log"] = None
                    st.session_state["last_incident"] = incident
                    st.session_state["last_latency_ms"] = _latency
                    st.session_state["decision_submitted"] = False
                    st.rerun()
            else:
                with st.spinner("Analizando incidente (modo síncrono)…"):
                    _t0 = datetime.now(tz=UTC)
                    try:
                        recommendation, log = run_pipeline(incident, llm=_get_llm())
                        _latency = (datetime.now(tz=UTC) - _t0).total_seconds() * 1000
                        _get_logger().log(log)
                        st.session_state["last_recommendation"] = recommendation
                        st.session_state["last_log"] = log
                        st.session_state["last_incident"] = incident
                        st.session_state["last_latency_ms"] = _latency
                        st.session_state["decision_submitted"] = False
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Error al procesar el incidente: {exc}")

    # ── Resultado: ficha de operación ──────────────────────────────────────
    if "last_recommendation" not in st.session_state:
        st.info(
            "👆 Introduce la descripción de la situación y pulsa **Analizar incidente**. "
            "El sistema responderá con prioridad propuesta, reglas activadas, citas normativas "
            "y pasos sugeridos."
        )
    else:
        rec: OperatorRecommendation = st.session_state["last_recommendation"]
        log = st.session_state["last_log"]
        incident = st.session_state["last_incident"]
        latency_ms = st.session_state.get("last_latency_ms")
        decision_submitted = st.session_state.get("decision_submitted", False)

        # Banda superior tipo cabecera de mando
        st.markdown(_command_strip(rec, incident, latency_ms), unsafe_allow_html=True)

        # Identificador + título del incidente
        st.markdown(
            f"<div class='cmd-card'>"
            f"<div style='font-weight:600;font-size:1.1rem;margin-bottom:4px'>"
            f"{incident.texto_titulo}</div>"
            f"<div style='color:#666;font-size:0.85rem'>"
            f"ID: <code>{incident.incident_id}</code> · "
            f"Operador: <code>{incident.operador_id}</code></div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        col_sit, col_why, col_do = st.columns([1, 1.1, 1], gap="medium")

        # ── (1) SITUACIÓN DETECTADA ────────────────────────────────────────
        with col_sit:
            st.markdown("##### 🧭 Situación")
            if log is not None and log.capa2_output is not None:
                conf_val = log.capa2_output.confidence_level.value
                st.markdown(f"**Confianza Capa 2:** {_CONFIDENCE_BADGE.get(conf_val, conf_val)}")
                # Distribución de probabilidad
                probs = log.capa2_output.probabilities
                if probs:
                    st.caption("Distribución de probabilidad")
                    for p_enum in Priority:
                        v = float(probs.get(p_enum, 0.0))
                        st.progress(min(max(v, 0.0), 1.0), text=f"{p_enum.value} · {v*100:.0f}%")
            else:
                st.caption("⚪ Confianza no disponible (modo streaming)")

            if incident.localidad or incident.provincia:
                st.markdown(
                    f"**📍 Ubicación:** "
                    f"{incident.localidad or '—'}, "
                    f"{incident.provincia.value if incident.provincia else '—'}"
                )

        # ── (2) POR QUÉ — Reglas + citas ───────────────────────────────────
        with col_why:
            st.markdown("##### ⚖️ Por qué")
            st.markdown(
                f"<div style='font-style:italic;color:#444;margin-bottom:10px'>"
                f"{rec.explanation_text}</div>",
                unsafe_allow_html=True,
            )

            activated = rec.activated_rules_summary or []
            if not activated and log is not None and log.capa2_output is not None:
                activated = [
                    f"**{r.rule_id}** · {r.human_text} (w={r.weight:.2f})"
                    for r in log.capa2_output.activated_rules
                ]
            if activated:
                st.markdown("**Reglas activadas**")
                for rule_text in activated:
                    st.markdown(
                        f"<div class='rule-row'>{rule_text}</div>",
                        unsafe_allow_html=True,
                    )

            if rec.legal_citations:
                with st.expander(f"📚 Anclaje normativo ({len(rec.legal_citations)})", expanded=False):
                    for cita in rec.legal_citations:
                        norma = cita.norma_id.value
                        art = f" · {cita.articulo_o_seccion}" if cita.articulo_o_seccion else ""
                        url = str(cita.url_oficial) if cita.url_oficial else None
                        head = f"[{norma}{art}]({url})" if url else f"**{norma}{art}**"
                        st.markdown(f"📌 {head}<br><span style='color:#555'>{cita.texto_relevante}</span>",
                                    unsafe_allow_html=True)

        # ── (3) QUÉ HACER — Checklist tachable ─────────────────────────────
        with col_do:
            st.markdown("##### 🎯 Pasos sugeridos")
            hints = list(rec.actuation_hints or [])
            if hints:
                st.caption("Marca los pasos a medida que los coordines.")
                for i, hint in enumerate(hints):
                    st.checkbox(hint, key=f"step_{rec.priority_recommended.value}_{i}")
            else:
                st.caption("Sin pasos sugeridos para esta recomendación.")

            if log is not None and log.latencias_ms:
                with st.expander("⏱ Latencias por capa"):
                    for k, v in log.latencias_ms.items():
                        st.markdown(f"- **{k}**: {v:.1f} ms")

        # ── Decisión del operador ──────────────────────────────────────────
        st.divider()
        st.markdown("##### 👮 Decisión del operador")

        if decision_submitted:
            st.success("✅ Decisión registrada. Puedes analizar un nuevo incidente arriba.")
        else:
            col_dec, col_pri, col_btn = st.columns([1.1, 1, 1])
            with col_dec:
                decision_action = st.radio(
                    "Acción",
                    options=["Aceptar", "Modificar prioridad", "Rechazar"],
                    horizontal=False,
                    key="decision_action",
                )
            with col_pri:
                if decision_action in ("Modificar prioridad", "Rechazar"):
                    priority_final = st.selectbox(
                        "Prioridad final",
                        options=list(Priority),
                        index=list(Priority).index(rec.priority_recommended),
                        format_func=lambda p: _PRIORITY_LABEL.get(p.value, p.value),
                        key="priority_override",
                    )
                else:
                    priority_final = rec.priority_recommended
                    st.caption(f"Se asignará: {_PRIORITY_LABEL.get(priority_final.value, priority_final.value)}")
            with col_btn:
                st.markdown("&nbsp;")
                confirm = st.button("Confirmar", type="primary", use_container_width=True, key="btn_confirm")

            motivo = None
            if decision_action in ("Modificar prioridad", "Rechazar"):
                motivo = st.text_area(
                    "Motivo de la divergencia *",
                    placeholder="Explica brevemente por qué modifica o rechaza la recomendación…",
                    max_chars=500,
                    key="motivo_divergencia",
                )

            if confirm:
                if decision_action in ("Modificar prioridad", "Rechazar") and not (motivo or "").strip():
                    st.error("El motivo es obligatorio al modificar o rechazar.")
                else:
                    try:
                        op_decision = OperatorDecision(
                            incident_id=incident.incident_id,
                            priority_recommended_by_system=rec.priority_recommended,
                            priority_assigned_by_operator=priority_final,
                            motivo_divergencia=motivo or None,
                            operador_id=incident.operador_id,
                            timestamp=datetime.now(tz=UTC),
                        )
                        if log is not None:
                            existing = _get_logger().get_by_log_id(log.log_id)
                            if existing is not None:
                                updated = existing.model_copy(update={"operator_decision": op_decision})
                                _get_logger().update_operator_decision(log.log_id, updated)
                                st.session_state["last_log"] = updated

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
# TAB 2 — HISTORIAL
# ────────────────────────────────────────────────────────────────────────────

with tab_history:
    st.subheader("Incidentes analizados en esta sesión")
    history = st.session_state.get("session_history", [])
    if not history:
        st.info("Aún no se ha analizado ningún incidente en esta sesión.")
    else:
        import pandas as pd
        df = pd.DataFrame(history)[
            ["incident_id", "titulo", "recomendado", "asignado", "divergencia"]
        ]
        df.columns = ["Incidente", "Título", "Sistema", "Operador", "Divergencia"]

        def _color_priority(val: str) -> str:
            colors = {"P1": "background-color:#ffcdd2", "P2": "background-color:#ffe0b2",
                      "P3": "background-color:#fff9c4", "P4": "background-color:#c8e6c9"}
            return colors.get(val, "")

        styled = df.style.map(_color_priority, subset=["Sistema", "Operador"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        divergentes = sum(1 for h in history if h["divergencia"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", len(history))
        col2.metric("Aceptados", len(history) - divergentes)
        col3.metric("Divergentes", divergentes)


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — SOBRE EL SISTEMA
# ────────────────────────────────────────────────────────────────────────────

with tab_about:
    st.markdown(
        """
        ### Sistema de Apoyo a la Decisión — 112 CyL

        Prototipo académico del **TFE MUIA (UNIR)** que asiste a los operadores
        del centro de mando (CECOP) en la **priorización P1–P4** de incidentes
        de protección civil.

        #### Arquitectura de 3 capas
        - **Capa 1 — NLP** · Extracción de variables V01–V15 desde texto libre.
        - **Capa 2 — Reglas interpretables (RuleFit)** · Recomendación P1–P4
          con probabilidades calibradas y reglas trazables.
        - **Capa 3 — LLM + MCP + RAG** · Explicación en lenguaje natural anclada
          en normativa vigente (Ley 17/2015, Norma Básica, planes autonómicos).

        #### Principios constitucionales
        1. **Supervisión humana** — el sistema *sugiere*, el operador *decide*.
        2. **Explicabilidad por diseño** — toda recomendación viene con reglas y citas.
        3. **Anti-leakage** — el modelo no usa información posterior al instante 0.
        4. **Trazabilidad completa** — cada inferencia queda registrada.

        ⚠️ Este sistema es **académico** y **no sustituye** los procedimientos
        operativos del 112 ni la formación profesional del personal CECOP.
        """
    )
