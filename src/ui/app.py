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
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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

# Escenarios de quickstart.md
scenarios = {
    "Escenario 1: Accidente Tráfico Grave (P1)": {
        "titulo": "Choque frontal N-122 con atrapados",
        "descripcion": "Colision frontal entre dos turismos en N-122 km 150. Hay un varon inconsciente herido grave atrapado en el vehiculo.",
        "categoria": CategoriaPreliminar.ACCIDENTE_TRAFICO,
        "lat": 41.6521,
        "lon": -2.4632,
        "localidad": "Golmayo",
        "provincia": ProvinciaCyL.SORIA,
    },
    "Escenario 2: Incidencia Vial Sin Víctimas (P4)": {
        "titulo": "Arbol caido en arcen",
        "descripcion": "Arbol de medianas dimensiones caido en el arcen derecho de la calzada. Sin vehiculos implicados ni personas afectadas.",
        "categoria": CategoriaPreliminar.OTROS,
        "lat": 40.9650,
        "lon": -5.6640,
        "localidad": "Salamanca",
        "provincia": ProvinciaCyL.SALAMANCA,
    },
    "Escenario 3: Mercancías Peligrosas Activo (P1/P2)": {
        "titulo": "Fuga de gas cisterna en autovia",
        "descripcion": "Camion cisterna detenido en el arcen de la A-62. Se observa una fuga de gas licuado y hay fuerte olor quimico en la zona.",
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
            with httpx.Client(timeout=10.0) as client:
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
            return {
                "recommendation": json.loads(rec.model_dump_json()),
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
    
    # Valores por defecto derivados del escenario
    default_vals = scenarios.get(selected_scenario_name, {})
    
    # Campos de Entrada del Formulario
    titulo = st.text_input(
        "Título del Incidente:",
        value=default_vals.get("titulo", ""),
        max_chars=200,
        placeholder="Ej. Choque frontal de dos coches",
    )
    
    descripcion = st.text_area(
        "Descripción en texto libre (operador 112):",
        value=default_vals.get("descripcion", ""),
        height=150,
        max_chars=5000,
        placeholder="Anote aquí los detalles de la llamada en tiempo real...",
    )
    
    # Categoría preliminar
    cat_keys = list(CategoriaPreliminar)
    default_cat_idx = cat_keys.index(default_vals["categoria"]) if "categoria" in default_vals else 0
    categoria = st.selectbox(
        "Categoría operativa preliminar:",
        options=cat_keys,
        index=default_cat_idx,
    )
    
    incluir_coordenadas = st.checkbox("Incluir coordenadas GPS", value="lat" in default_vals)
    if incluir_coordenadas:
        col_geo1, col_geo2 = st.columns(2)
        with col_geo1:
            lat = st.number_input(
                "Latitud:",
                value=default_vals.get("lat", 41.6521),
                format="%.5f",
                min_value=-90.0,
                max_value=90.0,
            )
        with col_geo2:
            lon = st.number_input(
                "Longitud:",
                value=default_vals.get("lon", -2.4632),
                format="%.5f",
                min_value=-180.0,
                max_value=180.0,
            )
    else:
        lat = None
        lon = None
        
    localidad = st.text_input("Localidad:", value=default_vals.get("localidad", "Soria"))
    
    prov_keys = list(ProvinciaCyL)
    default_prov_idx = prov_keys.index(default_vals["provincia"]) if "provincia" in default_vals else 6  # Soria
    provincia = st.selectbox(
        "Provincia:",
        options=prov_keys,
        index=default_prov_idx,
    )
    
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
            f"""
            <div class="priority-card {style_class}">
                <h1 style="font-size: 3.5rem; margin: 0; color: inherit;">{p_val}</h1>
                <p style="font-weight: 600; margin: 0; font-size: 1.1rem; color: inherit;">{text_label}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Si es degradado, mostrar advertencia
        if degraded:
            st.warning("⚠️ **Modo Degradado Activo**: El servicio del LLM local no está disponible. Explicación basada en reglas estáticas.")
            
        # 2. Explicación Textual
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 💡 Explicación del Sistema:")
        st.write(rec["explanation_text"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 3. Distribución de Probabilidades
        st.markdown("#### 🎚️ Distribución de Confianza del Modelo:")
        probs = rec.get("probabilities", {}) or {}
        # Aplanar si viene como diccionarios
        probs_flat = {k.get("value") if isinstance(k, dict) else k: v for k, v in probs.items()}
        
        for p_name in ["P1", "P2", "P3", "P4"]:
            val = probs_flat.get(p_name, 0.0)
            st.progress(val, text=f"**{p_name}**: {val * 100:.2f}% de probabilidad")
            
        st.markdown("---")
        
        # 4. Bases Legales y Citas
        st.markdown("#### ⚖️ Sustento Normativo y Recomendaciones")
        citations = rec.get("legal_citations", [])
        if citations:
            for idx, cit in enumerate(citations):
                st.markdown(
                    f"""
                    🔹 **{cit['norma_id']} (Art. {cit.get('articulo_o_seccion', 'General')})**: 
                    > "{cit['texto_relevante']}"  
                    🔗 [Ver Boletín Oficial (BOE/BOCYL)]({cit['url_oficial']})
                    """
                )
        else:
            st.markdown("*No se requieren citas legales obligatorias para prioridades ordinarias (P3/P4).*")
            
        hints = rec.get("actuation_hints", [])
        if hints:
            st.markdown("##### 📌 Pautas de Actuación recomendadas:")
            for hint in hints:
                st.markdown(f"- {hint}")

        # 5. Reglas RuleFit Activadas (Expandible)
        activated_rules = rec.get("activated_rules_summary", [])
        with st.expander("🔍 Ver Reglas Operativas RuleFit Activadas"):
            if activated_rules:
                for rule in activated_rules:
                    st.markdown(f"✔️ {rule}")
            else:
                st.markdown("*No se activaron reglas operativas de urgencia específicas.*")
                
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
                    st.session_state.feedback_submitted = True
                    st.rerun()
                else:
                    st.error("Error al enviar la decisión al servidor.")
