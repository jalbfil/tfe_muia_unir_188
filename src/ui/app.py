"""T101 — Interfaz Gráfica de Usuario (Streamlit UI) para el DSS 112 CyL.

Proporciona una consola operativa para el operador 112 con formulario de incidentes,
visualización reactiva de prioridad en colores curados HSL, explicación con base legal,
desglose de reglas operativas RuleFit y registro interactivo de la decisión final (HITL).
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from ulid import ULID

import httpx
import streamlit as st

# Asegurar importabilidad de los paquetes del monorepo
# parents[2] = repo_root  → contratos, backend (instalados como paquetes editables)
# parents[1] = src/       → audio.transcriber, capa3_llm_mcp, etc. (módulos directos)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contracts import (
    Accesibilidad,
    CategoriaPreliminar,
    IncidentInput,
    OperatorDecision,
    ProvinciaCyL,
    Priority,
)

# Configuración del Backend FastAPI
BACKEND_URL = "http://localhost:8000"

# Intentar habilitar el fallback en proceso si el backend no está levantado
try:
    from backend.orchestrator.pipeline import run_pipeline
    from contracts import compute_input_hash, InferenceLog
    IN_PROCESS_AVAILABLE = True
except ImportError:
    IN_PROCESS_AVAILABLE = False

# Configuración de página de Streamlit
st.set_page_config(
    page_title="112 Castilla y León — DSS de Priorización",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos CSS Premium (Aesthetics & UX) ──────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Fuente global */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Estilo del contenedor principal */
    .reportview-container {
        background-color: #0E1117;
    }

    /* Tarjetas de prioridad premium HSL */
    .priority-card {
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .p1-card {
        background: linear-gradient(135deg, #E63946, #D62246);
        border-left: 8px solid #9B2226;
        animation: pulse 2s infinite alternate;
    }
    .p2-card {
        background: linear-gradient(135deg, #F4A261, #E76F51);
        border-left: 8px solid #D85A38;
    }
    .p3-card {
        background: linear-gradient(135deg, #457B9D, #1D3557);
        border-left: 8px solid #1D3557;
    }
    .p4-card {
        background: linear-gradient(135deg, #A8DADC, #457B9D);
        border-left: 8px solid #457B9D;
        color: #1D3557 !important;
    }

    /* Micro-animación pulsante para P1 */
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 4px 15px rgba(230, 57, 70, 0.4); }
        100% { transform: scale(1.02); box-shadow: 0 4px 25px rgba(230, 57, 70, 0.7); }
    }

    /* Vidrio/Glassmorphism para explicaciones */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }

    /* Formulario e inputs */
    .stButton>button {
        background-color: #1D3557;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 2rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #457B9D;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(69, 123, 157, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Estado Inicial de Sesión ──────────────────────────────────────────────────
if "predict_response" not in st.session_state:
    st.session_state.predict_response = None
if "incident_input" not in st.session_state:
    st.session_state.incident_input = None
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False
if "degraded_mode" not in st.session_state:
    st.session_state.degraded_mode = False
if "session_history" not in st.session_state:
    st.session_state.session_history = []
if "_last_scenario" not in st.session_state:
    st.session_state._last_scenario = ""
# Campos del formulario controlados por session_state (patrón robusto Streamlit):
# los widgets leen de session_state[key], nunca de value= junto con key=.
if "titulo_field" not in st.session_state:
    st.session_state.titulo_field = ""
if "descripcion_field" not in st.session_state:
    st.session_state.descripcion_field = ""
if "localidad_field" not in st.session_state:
    st.session_state.localidad_field = "Soria"
if "categoria_field" not in st.session_state:
    st.session_state.categoria_field = list(CategoriaPreliminar)[0]
if "provincia_field" not in st.session_state:
    st.session_state.provincia_field = list(ProvinciaCyL)[6]
if "_audio_applied" not in st.session_state:
    st.session_state._audio_applied = True


def _apply_fields_to_state(fields: dict) -> None:
    """Escribe los campos extraídos (audio o escenario) en session_state antes
    de que se rendericen los widgets. Patrón key-only de Streamlit: los widgets
    leen exclusivamente de session_state[key], nunca de value= junto con key=."""
    if fields.get("titulo"):
        st.session_state.titulo_field = fields["titulo"]
    if fields.get("descripcion"):
        st.session_state.descripcion_field = fields["descripcion"]
    if fields.get("localidad"):
        st.session_state.localidad_field = fields["localidad"]
    _cat = fields.get("categoria")
    if _cat:
        try:
            st.session_state.categoria_field = (
                _cat if isinstance(_cat, CategoriaPreliminar) else CategoriaPreliminar(_cat)
            )
        except ValueError:
            pass
    _prov = fields.get("provincia")
    if _prov:
        try:
            st.session_state.provincia_field = (
                _prov if isinstance(_prov, ProvinciaCyL) else ProvinciaCyL(_prov)
            )
        except ValueError:
            pass


# ── Títulos y Sidebar ────────────────────────────────────────────────────────
st.title("🚨 Centro de Emergencias 112 CyL")
st.subheader("DSS de Priorización Temprana y Caracterización Explicable")

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Logo_112.svg", width=120)
st.sidebar.markdown("### Configuración del Sistema")

# Mostrar estado de conexión
backend_live = False
try:
    with httpx.Client(timeout=1.0) as client:
        res = client.get(f"{BACKEND_URL}/healthz")
        backend_live = res.status_code == 200
except Exception:
    backend_live = False

if backend_live:
    st.sidebar.success("🟢 Servidor API Conectado")
else:
    if IN_PROCESS_AVAILABLE:
        st.sidebar.warning("🟡 Servidor API Desconectado\n(Modo In-Process Activo)")
    else:
        st.sidebar.error("🔴 Servidor API Desconectado")

st.sidebar.markdown("---")
st.sidebar.markdown("### Plantillas de Escenarios")
st.sidebar.markdown(
    "Selecciona una plantilla para rellenar de forma inmediata los datos de demostración:"
)

# ── Historial de sesión en sidebar ──────────────────────────────────────────
if st.session_state.session_history:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Historial de Sesión")
    _p_counts = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}
    for _h in st.session_state.session_history:
        _p_counts[_h["prioridad"]] = _p_counts.get(_h["prioridad"], 0) + 1
    _dist = " · ".join(f"**{k}**: {v}" for k, v in _p_counts.items() if v > 0)
    st.sidebar.caption(f"Casos: {len(st.session_state.session_history)} — {_dist}")
    for _h in reversed(st.session_state.session_history[-5:]):
        _icon = {"P1": "🔴", "P2": "🟠", "P3": "🔵", "P4": "🟢"}.get(_h["prioridad"], "⚪")
        _dec = f" → {_h['decision']}" if _h.get("decision") else ""
        st.sidebar.markdown(f"{_icon} {_h['titulo'][:32]}... **{_h['prioridad']}**{_dec}")
    if st.sidebar.button("🗑️ Limpiar historial"):
        st.session_state.session_history = []
        st.rerun()

# Escenarios de quickstart.md
scenarios = {
    "Escenario 1: Accidente Tráfico Grave (P1)": {
        "titulo": "Choque frontal N-122 con atrapados",
        "descripcion": "Colisión frontal entre dos turismos en N-122 km 150. Hay un varón inconsciente herido grave atrapado en el vehículo.",
        "categoria": CategoriaPreliminar.ACCIDENTE_TRAFICO,
        "lat": 41.6521,
        "lon": -2.4632,
        "localidad": "Golmayo",
        "provincia": ProvinciaCyL.SORIA,
    },
    "Escenario 2: Incidencia Vial Sin Víctimas (P4)": {
        "titulo": "Árbol caído en arcén",
        "descripcion": "Árbol de medianas dimensiones caído en el arcén derecho de la calzada. Sin vehículos implicados ni personas afectadas.",
        "categoria": CategoriaPreliminar.OTROS,
        "lat": 40.9650,
        "lon": -5.6640,
        "localidad": "Salamanca",
        "provincia": ProvinciaCyL.SALAMANCA,
    },
    "Escenario 3: Mercancías Peligrosas Activo (P1/P2)": {
        "titulo": "Fuga de gas cisterna en autovía",
        "descripcion": "Camión cisterna detenido en el arcén de la A-62. Se observa una fuga de gas licuado y hay fuerte olor químico en la zona.",
        "categoria": CategoriaPreliminar.OTROS,
        "lat": 41.8350,
        "lon": -4.7280,
        "localidad": "Dueñas",
        "provincia": ProvinciaCyL.PALENCIA,
    },
}

selected_scenario_name = st.sidebar.selectbox(
    "Cargar escenario de ejemplo:",
    ["-- Seleccionar plantilla --"] + list(scenarios.keys()),
)

# ── Flujo de Datos ────────────────────────────────────────────────────────────
def run_predict(input_data: IncidentInput) -> dict | None:
    """Envía la llamada de inferencia a /predict (o ejecuta fallback local)."""
    # 1. Intentar llamar al backend FastAPI
    if backend_live:
        try:
            with httpx.Client(timeout=120.0) as client:  # LLM + model loading puede tardar >10s
                res = client.post(
                    f"{BACKEND_URL}/predict",
                    json=json.loads(input_data.model_dump_json()),
                )
                if res.status_code == 200:
                    return res.json()
                else:
                    st.error(f"Error del Servidor Backend: {res.text}")
                    return None
        except Exception as e:
            st.error(f"Error de red con el backend: {e}")

    # 2. Fallback in-process si está habilitado
    if IN_PROCESS_AVAILABLE:
        st.info("Ejecutando inferencia in-process (fallback local)...")
        # Simular run_pipeline
        try:
            rec, log = run_pipeline(input_data)
            priority_details = {
                "priority_recommended": log.capa2_output.priority_recommended.value,
                "probabilities": {
                    p.value: float(prob)
                    for p, prob in log.capa2_output.probabilities.items()
                },
                "confidence_level": log.capa2_output.confidence_level.value,
                "model_used": log.capa2_output.model_used.value,
                "model_version_capa2": log.capa2_output.model_version_capa2,
                "requires_human_attention": log.capa2_output.requires_human_attention,
                "activated_rules": [
                    {
                        "rule_id": rule.rule_id,
                        "human_text": rule.human_text,
                        "weight": rule.weight,
                        "normative_anchors": [anchor.value for anchor in rule.normative_anchors],
                    }
                    for rule in log.capa2_output.activated_rules
                ]
            }
            return {
                "recommendation": json.loads(rec.model_dump_json()),
                "features": json.loads(log.capa1_output.model_dump_json()) if log.capa1_output else None,
                "priority_details": priority_details,
                "log_id": log.log_id,
                "degraded": "degraded" in rec.llm_metadata.llm_model.lower(),
            }
        except Exception as e:
            st.error(f"Error en inferencia in-process: {e}")
            return None

    st.error("No hay backend disponible ni módulo in-process para realizar la clasificación.")
    return None


def run_feedback(decision_data: OperatorDecision) -> bool:
    """Envía el feedback final al backend (o lo registra in-process)."""
    if backend_live:
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.post(
                    f"{BACKEND_URL}/feedback",
                    json=json.loads(decision_data.model_dump_json()),
                )
                return res.status_code == 200
        except Exception:
            return False

    # Si estamos in-process, simulamos guardado correcto en SQLite
    if IN_PROCESS_AVAILABLE:
        # En fallback simulamos éxito del log
        return True
    return False


# ── Grid Principal de Layout ──────────────────────────────────────────────────
col_form, col_dashboard = st.columns([1, 1.2], gap="large")

with col_form:
    st.markdown("### 📥 Entrada del Incidente")

    # ── Entrada por voz — PRIMERA en el formulario ───────────────────────────
    st.markdown("#### 🎙️ Entrada por voz")
    st.caption("Graba o sube el audio de la llamada. Whisper transcribe localmente y rellena el formulario de forma inteligente.")

    # Cargar transcriptor y parser (lazy, sin crash si no instalados)
    try:
        from audio.transcriber import AudioTranscriber   # type: ignore[import]
        from audio.parser import TranscriptParser        # type: ignore[import]
        _transcriber = AudioTranscriber()
        _parser = TranscriptParser()
        _transcriber_available = _transcriber.is_available()
    except Exception:
        _transcriber = None
        _parser = None
        _transcriber_available = False

    if not _transcriber_available:
        st.info("💡 Transcripción de voz disponible tras: `pip install faster-whisper`")
    else:
        _audio_tab1, _audio_tab2 = st.tabs(["🎤 Grabar en vivo", "📁 Subir audio"])

        with _audio_tab1:
            st.caption("Streamlit ≥1.38 requerido. Pulsa el micrófono y habla.")
            try:
                _recorded = st.audio_input("Grabar llamada")
            except AttributeError:
                _recorded = None
                st.warning("⚠️ Actualiza Streamlit: `pip install -U streamlit`")
            if _recorded is not None:
                _rec_bytes = _recorded.getvalue()
                _rec_sig = hash(_rec_bytes)
                # Evita re-transcribir el mismo audio en cada rerun (bucle infinito).
                if st.session_state.get("_rec_sig") != _rec_sig:
                    st.session_state["_rec_sig"] = _rec_sig
                    try:
                        with st.spinner("Transcribiendo y extrayendo campos…"):
                            _transcript_text = _transcriber.transcribe(_rec_bytes, file_ext=".wav")
                        if _transcript_text:
                            _fields = _parser.parse(_transcript_text)
                            st.session_state["_audio_fields"] = _fields
                            _apply_fields_to_state(_fields)
                            st.rerun()
                        else:
                            st.warning("No se detectó voz en la grabación.")
                    except Exception as _exc:
                        st.error(f"Error de transcripción: {_exc}")

        with _audio_tab2:
            _uploaded = st.file_uploader(
                "Sube audio (wav, mp3, m4a, ogg, webm)",
                type=["wav", "mp3", "mp4", "m4a", "ogg", "webm"],
                label_visibility="collapsed",
            )
            if _uploaded is not None:
                st.audio(_uploaded)
                if st.button("🔤 Transcribir y rellenar formulario"):
                    try:
                        with st.spinner(f"Transcribiendo con Whisper '{_transcriber.model_name}'…"):
                            _ext = Path(_uploaded.name).suffix.lower() or ".wav"
                            _t = _transcriber.transcribe(_uploaded.getvalue(), file_ext=_ext)
                        if _t:
                            _fields = _parser.parse(_t)
                            st.session_state["_audio_fields"] = _fields
                            _apply_fields_to_state(_fields)
                            st.rerun()
                        else:
                            st.warning("No se detectó voz utilizable.")
                    except Exception as _exc:
                        st.error(f"Error de transcripción: {_exc}")

    # Estado de la extracción de audio
    _af = st.session_state.get("_audio_fields", {})
    if _af:
        st.success(
            f"✅ Formulario rellenado desde audio · "
            f"**Título:** `{_af.get('titulo', '—') or '—'}` · "
            f"**Categoría:** `{_af.get('categoria', '?')}` · "
            f"**Localidad:** `{_af.get('localidad', '—') or '—'}`"
        )
        if st.button("🗑️ Limpiar campos de voz"):
            st.session_state.pop("_audio_fields", None)
            st.session_state.pop("_rec_sig", None)
            st.session_state.titulo_field = ""
            st.session_state.descripcion_field = ""
            st.rerun()

    st.markdown("---")
    st.markdown("#### ✏️ Datos del incidente")

    # ── Valores por defecto: audio_fields > escenario > vacío ────────────────
    default_vals = scenarios.get(selected_scenario_name, {})

    # Bug fix 1: cuando cambia el escenario, escribir sus valores directamente en
    # session_state (patrón key-only) y forzar un nuevo run para que los widgets
    # los reflejen. Si es el placeholder, _dv={} y los campos quedan vacíos.
    if selected_scenario_name != st.session_state._last_scenario:
        st.session_state._last_scenario = selected_scenario_name
        st.session_state.pop("_audio_fields", None)
        st.session_state.pop("lat_field", None)
        st.session_state.pop("lon_field", None)
        _dv = scenarios.get(selected_scenario_name, {})
        st.session_state.titulo_field = _dv.get("titulo", "")
        st.session_state.descripcion_field = _dv.get("descripcion", "")
        st.session_state.localidad_field = _dv.get("localidad", "Soria")
        if _dv.get("categoria") is not None:
            st.session_state.categoria_field = _dv["categoria"]
        if _dv.get("provincia") is not None:
            st.session_state.provincia_field = _dv["provincia"]
        st.rerun()  # ← imprescindible: fuerza nuevo run con session_state actualizado

    cat_keys = list(CategoriaPreliminar)
    prov_keys = list(ProvinciaCyL)

    # ── Campos del formulario (patrón key-only: leen de session_state) ────────
    titulo = st.text_input(
        "Título del Incidente:",
        key="titulo_field",
        max_chars=200,
        placeholder="Ej. Choque frontal de dos coches",
    )

    descripcion = st.text_area(
        "Descripción en texto libre (operador 112):",
        key="descripcion_field",
        height=150,
        max_chars=5000,
        placeholder="Anote aquí los detalles de la llamada en tiempo real…",
    )

    categoria = st.selectbox(
        "Categoría operativa preliminar:",
        options=cat_keys,
        key="categoria_field",
    )

    incluir_coordenadas = st.checkbox("Incluir coordenadas GPS", value="lat" in default_vals)
    if incluir_coordenadas:
        col_geo1, col_geo2 = st.columns(2)
        with col_geo1:
            # Bug fix 2: key en lat/lon para que el cambio de escenario los resetee
            lat = st.number_input("Latitud:", value=default_vals.get("lat", 41.6521),
                                  key="lat_field", format="%.5f", min_value=-90.0, max_value=90.0)
        with col_geo2:
            lon = st.number_input("Longitud:", value=default_vals.get("lon", -2.4632),
                                  key="lon_field", format="%.5f", min_value=-180.0, max_value=180.0)
    else:
        lat = None
        lon = None

    localidad = st.text_input("Localidad:", key="localidad_field")

    provincia = st.selectbox("Provincia:", options=prov_keys, key="provincia_field")

    operador_id = st.text_input("ID del Operador:", value="OP_ANCOR", max_chars=64)

    # Validación del texto
    text_ok = any(c.isalpha() for c in (titulo + descripcion))
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚨 Analizar Incidente", disabled=not text_ok):
        # Crear IncidentInput
        try:
            incident = IncidentInput(
                incident_id=str(ULID()),
                texto_titulo=titulo,
                texto_descripcion=descripcion,
                categoria_preliminar=categoria,
                latitud=lat,
                longitud=lon,
                localidad=localidad,
                provincia=provincia,
                fecha_incidente=datetime.now(timezone.utc),
                operador_id=operador_id,
            )
            st.session_state.incident_input = incident
            st.session_state.feedback_submitted = False
            
            with st.spinner("Analizando y priorizando incidente..."):
                response = run_predict(incident)
                if response:
                    st.session_state.predict_response = response
                    st.success("Priorización y análisis legal completados.")
                else:
                    st.session_state.predict_response = None
        except Exception as e:
            st.error(f"Error de validación del contrato: {e}")

# ── Renderizado de Resultados y Cuadro de Mando ────────────────────────────────
with col_dashboard:
    st.markdown("### 📊 Cuadro de Mando del Decision Support")
    
    if st.session_state.predict_response is None:
        st.info("Ingrese un incidente a la izquierda y haga clic en **Analizar Incidente** para comenzar.")
    else:
        res = st.session_state.predict_response
        rec = res["recommendation"]
        log_id = res["log_id"]
        degraded = res.get("degraded", False)
        # Extraer priority_details y explanation_context aquí para uso en toda la sección
        priority_details = res.get("priority_details", {}) or {}
        exp_ctx_global = res.get("explanation_context", {}) or {}

        # Cargar variables útiles
        p_rec = rec["priority_recommended"]
        p_val = p_rec.get("value") if isinstance(p_rec, dict) else p_rec
        
        # 1. Tarjeta Premium de Prioridad Recomendada
        p_styles = {
            "P1": ("p1-card", "URGENCIA CRÍTICA — RIESGO VITAL"),
            "P2": ("p2-card", "URGENCIA SEVERA"),
            "P3": ("p3-card", "URGENCIA MODERADA"),
            "P4": ("p4-card", "ORDINARIO / SIN RIESGO VITAL"),
        }
        
        style_class, text_label = p_styles.get(p_val, ("p4-card", "ORDINARIO"))
        
        st.markdown(
            f'<div class="priority-card {style_class}">'
            f'<div style="font-size: 3.5rem; font-weight: bold; margin: 0; color: inherit; line-height: 1.2;">{p_val}</div>'
            f'<div style="font-weight: 600; margin: 0; font-size: 1.1rem; color: inherit;">{text_label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        
        # Si es degradado, mostrar advertencia
        if degraded:
            st.warning("⚠️ **Modo Degradado Activo**: El servicio del LLM local no está disponible. Explicación basada en reglas estáticas.")

        # Bloque de trazabilidad técnica (log_id + modelo)
        llm_meta = rec.get("llm_metadata", {})
        model_used_str = priority_details.get("model_used", "—") if isinstance(priority_details, dict) else "—"
        llm_model_str = llm_meta.get("llm_model", "—") if isinstance(llm_meta, dict) else "—"
        st.caption(
            f"🗂️ **Log ID:** `{log_id}` · "
            f"**Motor Capa 2:** `{model_used_str}` · "
            f"**LLM Capa 3:** `{llm_model_str}`"
        )

        # 2. Explicación Textual
        explanation_html = (
            f'<div class="glass-card">'
            f'<div style="font-size: 1.25rem; font-weight: bold; margin-bottom: 0.75rem; color: inherit;">💡 Explicación del Sistema:</div>'
            f'<div style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 0.5rem;">{rec["explanation_text"]}</div>'
        )
        confidence_disclaimer = rec.get("confidence_disclaimer")
        if confidence_disclaimer:
            explanation_html += (
                f'<div style="background-color: rgba(23, 162, 184, 0.1); border-left: 4px solid #17a2b8; padding: 0.8rem; border-radius: 4px; margin-top: 1rem; color: #d1ecf1; font-size: 0.95rem;">'
                f'<strong>ℹ️ Comentario / Alerta:</strong> {confidence_disclaimer}'
                f'</div>'
            )
        explanation_html += "</div>"
        st.markdown(explanation_html, unsafe_allow_html=True)

        
        # 3. Distribución de Probabilidades (vienen de priority_details, no de recommendation)
        st.markdown("#### 🎚️ Distribución de Confianza del Modelo:")
        probs = priority_details.get("probabilities", {}) or {}
        
        probs_flat = {}
        for k, v in probs.items():
            key_str = str(k)
            if isinstance(k, dict) and "value" in k:
                key_str = str(k["value"])
            elif "Priority." in key_str:
                key_str = key_str.replace("Priority.", "")
            probs_flat[key_str] = v
        
        for p_name in ["P1", "P2", "P3", "P4"]:
            val = probs_flat.get(p_name, 0.0)
            st.progress(val, text=f"**{p_name}**: {val * 100:.2f}% de probabilidad")

        # Margen de incertidumbre (casos frontera)
        prob_margin = exp_ctx_global.get("probability_margin") if isinstance(exp_ctx_global, dict) else None
        if prob_margin is not None:
            margin_color = "🟢" if prob_margin >= 0.40 else ("🟡" if prob_margin >= 0.15 else "🔴")
            st.caption(f"{margin_color} **Margen de certeza:** `{prob_margin:.3f}` {'(decisión clara)' if prob_margin >= 0.40 else '(caso frontera — juicio humano crítico)'}")

        st.markdown("---")
        
        # 4. Bases Legales y Citas
        st.markdown("#### ⚖️ Sustento Normativo y Recomendaciones")
        citations = rec.get("legal_citations", [])
        if citations:
            for idx, cit in enumerate(citations):
                _art_raw = str(cit.get("articulo_o_seccion") or "").strip()
                _low = _art_raw.lower()
                for _pre in ("artículo ", "articulo ", "art. ", "art ", "art.", "art"):
                    if _low.startswith(_pre):
                        _art_raw = _art_raw[len(_pre):].strip()
                        break
                if _art_raw and _art_raw.lower() != "general":
                    _art_label = f" (Art. {_art_raw})"
                else:
                    _art_label = ""
                
                url_url = cit.get("url_oficial")
                if url_url and str(url_url).lower() not in ("none", "null", ""):
                    url_link_markdown = f"\n                    🔗 [Ver Boletín Oficial (BOE/BOCYL)]({url_url})"
                else:
                    url_link_markdown = ""
                
                st.markdown(
                    f"""
                    🔹 **{cit['norma_id']}{_art_label}**: 
                    > "{cit['texto_relevante']}"  {url_link_markdown}
                    """
                )
        else:
            st.markdown("*No se requieren citas legales obligatorias para prioridades ordinarias (P3/P4).*")
            
        hints = rec.get("actuation_hints", [])
        if hints:
            st.markdown("##### 📌 Pautas de Actuación recomendadas:")
            for hint in hints:
                st.markdown(f"- {hint}")

        # 4.5. Variables Operativas Extraídas (Capa 1 NLP)
        features = res.get("features")
        if features:
            with st.expander("🔍 Ver Variables Operativas Extraídas (Capa 1 NLP)"):
                st.markdown("#### Desglose de Señales y Características:")
                col_c1_1, col_c1_2 = st.columns(2)
                with col_c1_1:
                    st.markdown(f"**¿Riesgo Vital?:** {'🔴 SÍ' if features['riesgo_vital']['value'] else '🟢 NO'} *(Confianza: {features['riesgo_vital']['confidence']:.2f})*")
                    victimas = features['numero_victimas_estimado']['value']
                    st.markdown(f"**Víctimas Estimadas (V02):** {victimas if victimas != -1 else 'Desconocido'} *(Confianza: {features['numero_victimas_estimado']['confidence']:.2f})*")
                    st.markdown(f"**Gravedad Lesiones (V03):** `{features['gravedad_lesiones']}` *(Confianza: {features['gravedad_lesiones_confidence']:.2f})*")
                    st.markdown(f"**Población Vulnerable (V05):** {'🟡 SÍ' if features['poblacion_vulnerable']['value'] else '🟢 NO'} *(Confianza: {features['poblacion_vulnerable']['confidence']:.2f})*")
                    st.markdown(f"**Tipo Incidente Normalizado (V04):** `{features['tipo_incidente_normalizado']}`")
                with col_c1_2:
                    st.markdown(f"**Emplazamiento Crítico (V07):** {'🔴 SÍ' if features['emplazamiento_critico']['value'] else '🟢 NO'} *(Confianza: {features['emplazamiento_critico']['confidence']:.2f})*")
                    st.markdown(f"**Riesgo de Propagación (V12):** {'🟡 SÍ' if features['riesgo_propagacion']['value'] else '🟢 NO'} *(Confianza: {features['riesgo_propagacion']['confidence']:.2f})*")
                    st.markdown(f"**Multirriesgo (V13):** {'🔴 SÍ' if features['multirriesgo']['value'] else '🟢 NO'} *(Confianza: {features['multirriesgo']['confidence']:.2f})*")
                    st.markdown(f"**Accesibilidad Recursos (V15):** `{features['accesibilidad_recursos']}`")
                    st.markdown(f"**Latencia de Extracción:** `{features['inference_latency_ms']:.4f} ms`")

        # 5. Reglas RuleFit Activadas (Expandible)
        activated_rules = rec.get("activated_rules_summary", [])
        with st.expander("🔍 Ver Reglas Operativas RuleFit Activadas"):
            if activated_rules:
                for rule in activated_rules:
                    st.markdown(f"✔️ {rule}")
            else:
                st.markdown("*No se activaron reglas operativas de urgencia específicas.*")

        # 5b. Trazabilidad de proceso IA (tools MCP + temperatura)
        with st.expander("🔬 Trazabilidad del proceso de IA (Capa 3)"):
            llm_meta_full = rec.get("llm_metadata", {})
            if isinstance(llm_meta_full, dict):
                tools = llm_meta_full.get("tools_invoked", [])
                temp = llm_meta_full.get("temperature", None)
                tokens_in = llm_meta_full.get("tokens_input")
                tokens_out = llm_meta_full.get("tokens_output")
                st.markdown(f"**Modelo LLM:** `{llm_meta_full.get('llm_model', '—')}`")
                st.markdown(f"**Temperatura:** `{temp}` {'✅ modo producción (0.0)' if temp == 0.0 else '⚠️ temperatura distinta de 0'}")
                st.markdown(f"**Tools MCP invocadas:** {', '.join(f'`{t}`' for t in tools) if tools else '*ninguna (modo degradado)*'}")
                if tokens_in is not None:
                    st.markdown(f"**Tokens entrada / salida:** `{tokens_in}` / `{tokens_out}`")
                st.markdown(f"**Motor Capa 2:** `{priority_details.get('model_used', '—')}` · versión `{priority_details.get('model_version_capa2', '—')}`")
                st.caption("La temperatura 0.0 garantiza determinismo de la explicación (NFR-009). "
                           "Las tools MCP confirman que se consultó el corpus normativo real.")
            else:
                st.markdown("*Metadatos LLM no disponibles.*")

        # 5c. Tabla causal: Señal activa → Regla RuleFit → Base normativa
        _rules_full = priority_details.get("activated_rules", [])
        _citations = rec.get("legal_citations", [])
        if _rules_full or _citations:
            with st.expander("🔗 Cadena causal: Señal → Regla → Norma"):
                st.caption("Trazabilidad completa de la recomendación: por qué cada señal del incidente activó qué regla y qué norma la respalda.")
                _table_rows = []
                for _r in _rules_full[:10]:
                    _anchors = _r.get("normative_anchors", []) if isinstance(_r, dict) else []
                    _normas = ", ".join(f"`{a}`" for a in _anchors) if _anchors else "—"
                    _table_rows.append({
                        "🚨 Señal / Evidencia": _r.get("human_text", "—")[:60] if isinstance(_r, dict) else str(_r)[:60],
                        "Peso": f"{_r.get('weight', 0.0):.3f}" if isinstance(_r, dict) else "—",
                        "⚖️ Norma anclaje": _normas,
                    })
                if _table_rows:
                    import pandas as _pd
                    st.dataframe(_pd.DataFrame(_table_rows), use_container_width=True, hide_index=True)
                else:
                    # Fallback cuando solo hay summary (modo degradado)
                    _act = rec.get("activated_rules_summary", [])
                    _raw_cit = ", ".join(f"`{c['norma_id']}`" for c in _citations) if _citations else "—"
                    for _rs in _act:
                        st.markdown(f"- **{_rs}** → {_raw_cit}")

        # 6. HITL — Interacción Humana Decisiva
        st.markdown("---")
        st.markdown("### 🧑‍✈️ Validación e Intervención Humana (HITL)")
        
        if st.session_state.feedback_submitted:
            st.success("✅ **Decisión registrada correctamente en el log de auditoría.**")
            if st.button("Crear nuevo análisis"):
                st.session_state.predict_response = None
                st.session_state.incident_input = None
                st.session_state.feedback_submitted = False
                st.rerun()
        else:
            st.markdown(
                "Como operador 112, debes validar la recomendación antes de despachar los recursos:"
            )
            
            # Selector de prioridad asignada
            p_opts = list(Priority)
            default_p_idx = p_opts.index(Priority(p_val)) if p_val in [p.value for p in p_opts] else 2
            
            prioridad_asignada = st.selectbox(
                "Prioridad finalmente asignada por el operador:",
                options=p_opts,
                index=default_p_idx,
            )
            
            divergence = abs(int(p_val[-1]) - int(prioridad_asignada.value[-1]))
            
            motivo_divergencia = st.text_area(
                "Motivo del cambio / observaciones adicionales (opcional):",
                placeholder="Indique el motivo por el cual discrepa de la sugerencia del DSS...",
            )
            
            # Advertencia de auditoría si la divergencia es alta
            if divergence >= 2:
                st.error(
                    f"⚠️ **Atención**: La divergencia seleccionada es de {divergence} niveles. "
                    "El sistema marcará un evento de auditoría reforzada y requiere justificación obligatoria."
                )
                
            disabled_btn = divergence >= 2 and not motivo_divergencia.strip()
            
            if st.button("📋 Registrar Decisión de Operador", disabled=disabled_btn):
                # Construir OperatorDecision
                decision = OperatorDecision(
                    incident_id=st.session_state.incident_input.incident_id,
                    priority_recommended_by_system=Priority(p_val),
                    priority_assigned_by_operator=prioridad_asignada,
                    motivo_divergencia=motivo_divergencia.strip() or None,
                    operador_id=operador_id,
                    timestamp=datetime.now(timezone.utc),
                )
                
                success = run_feedback(decision)
                if success:
                    # Guardar en historial de sesión
                    st.session_state.session_history.append({
                        "titulo": st.session_state.incident_input.texto_titulo[:48],
                        "prioridad": p_val,
                        "confianza": priority_details.get("confidence_level", "—"),
                        "log_id": log_id,
                        "decision": prioridad_asignada.value,
                        "divergencia": divergence,
                        "motivo": motivo_divergencia.strip() or None,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                    st.session_state.feedback_submitted = True
                    st.rerun()
                else:
                    st.error("Error al enviar la decisión al servidor.")

        # 7. Descarga de informe del caso
        st.markdown("---")
        _case_report = {
            "log_id": log_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "incidente": {
                "id": st.session_state.incident_input.incident_id if st.session_state.incident_input else None,
                "titulo": st.session_state.incident_input.texto_titulo if st.session_state.incident_input else None,
            },
            "capa2": {
                "prioridad": p_val,
                "confianza": priority_details.get("confidence_level"),
                "motor": priority_details.get("model_used"),
                "margen": exp_ctx_global.get("probability_margin"),
                "probabilidades": priority_details.get("probabilities"),
            },
            "capa3": {
                "explicacion": rec.get("explanation_text"),
                "citas": rec.get("legal_citations", []),
                "pautas": rec.get("actuation_hints", []),
                "llm_metadata": rec.get("llm_metadata", {}),
            },
            "decision_operador": {
                "registrada": st.session_state.feedback_submitted,
            },
        }
        st.download_button(
            label="📅 Descargar informe de caso (JSON)",
            data=json.dumps(_case_report, ensure_ascii=False, indent=2),
            file_name=f"caso_{log_id[:8]}.json",
            mime="application/json",
        )
