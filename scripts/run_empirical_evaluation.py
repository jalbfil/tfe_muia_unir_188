"""Script de Evaluación Empírica Exhaustiva para el DSS 112 CyL.

Ejecuta el pipeline completo Capa 1 -> Capa 2 -> Capa 3 con el LLM real
y genera reportes detallados en JSON, Markdown y gráficos en PNG.
"""
from __future__ import annotations

import sys
import time
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
    cohen_kappa_score
)

# Configurar logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_empirical_evaluation")

# Configurar rutas del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from capa1_nlp.inference.feature_extractor import FeatureExtractor
from capa2_rulefit.inference.predictor import predict
from capa3_llm_mcp.explainer import explain, QwenWrapper
from contracts import (
    IncidentInput,
    Priority,
    ProvinciaCyL,
    CategoriaPreliminar,
    ConfidenceLevel,
    ModelUsed,
)

# Directorios de salida
REPORTS_DIR = PROJECT_ROOT / "artifacts" / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ─────────── Definición de Escenarios de Evaluación ───────────

SCENARIOS = [
    # === GRUPO A: NOMINALES (11 casos) ===
    {
        "incident_id": "EVAL-NOM-01",
        "texto_titulo": "Accidente grave N-122 con atrapados",
        "texto_descripcion": "Choque frontal entre turismo y furgoneta. Conductor inconsciente y atrapado en el turismo, otro ocupante herido grave.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "latitud": 41.6235, "longitud": -4.7268,
        "localidad": "Zamora", "provincia": "ZAMORA",
        "fecha_incidente": "2026-06-16T10:00:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_accidente_trafico": True, "signal_atrapado": True, "signal_herido_grave": True}
    },
    {
        "incident_id": "EVAL-NOM-02",
        "texto_titulo": "Incendio forestal cerca de viviendas",
        "texto_descripcion": "Llamas altas devorando masa de pinar a menos de 100 metros del núcleo urbano. Gran cantidad de humo y viento fuerte.",
        "categoria_preliminar": "INCENDIO_FORESTAL",
        "latitud": 42.1500, "longitud": -3.8500,
        "localidad": "Lerma", "provincia": "BURGOS",
        "fecha_incidente": "2026-06-16T14:30:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_incendio": True, "signal_varias_llamadas": True}
    },
    {
        "incident_id": "EVAL-NOM-03",
        "texto_titulo": "Fuga química en polígono industrial",
        "texto_descripcion": "Ruptura de tubería de cloro en fábrica. Varias personas con dificultad respiratoria severa, intoxicadas e inconscientes.",
        "categoria_preliminar": "QUIMICO_NRBQ",
        "latitud": 40.9650, "longitud": -5.6640,
        "localidad": "Salamanca", "provincia": "SALAMANCA",
        "fecha_incidente": "2026-06-16T11:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_intoxicacion": True, "riesgo_vital_textual": True}
    },
    {
        "incident_id": "EVAL-NOM-04",
        "texto_titulo": "Inundación masiva de sótanos",
        "texto_descripcion": "Lluvia torrencial provoca acumulación de un metro de agua en el garaje comunitario de un edificio. Sin personas en el interior.",
        "categoria_preliminar": "METEOROLOGIA",
        "latitud": 42.5980, "longitud": -5.5670,
        "localidad": "León", "provincia": "LEON",
        "fecha_incidente": "2026-06-16T18:00:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {"signal_meteo_inundacion": True}
    },
    {
        "incident_id": "EVAL-NOM-05",
        "texto_titulo": "Rescate de senderista perdido",
        "texto_descripcion": "Senderista perdido en el cañón del río Lobos al anochecer, presenta una torcedura de tobillo dolorosa y principio de hipotermia.",
        "categoria_preliminar": "RESCATE",
        "latitud": 41.7450, "longitud": -3.0720,
        "localidad": "Soria", "provincia": "SORIA",
        "fecha_incidente": "2026-06-16T21:00:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {"signal_rescate": True}
    },
    {
        "incident_id": "EVAL-NOM-06",
        "texto_titulo": "Derrumbe parcial de fachada",
        "texto_descripcion": "Se desprende parte de la cornisa de un edificio antiguo sobre la acera. No hay heridos, pero hay escombros y riesgo de más caídas.",
        "categoria_preliminar": "SEGURIDAD_CIUDADANA",
        "latitud": 41.9020, "longitud": -4.5240,
        "localidad": "Palencia", "provincia": "PALENCIA",
        "fecha_incidente": "2026-06-16T09:20:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-NOM-07",
        "texto_titulo": "Fuego apagado en cocina",
        "texto_descripcion": "Fuego en campana extractora sofocado con extintor por el propietario. Hay bastante humo en la vivienda pero no hay llamas activas.",
        "categoria_preliminar": "INCENDIO_URBANO",
        "latitud": 40.6560, "longitud": -4.7000,
        "localidad": "Ávila", "provincia": "AVILA",
        "fecha_incidente": "2026-06-16T13:45:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {"signal_incendio": True}
    },
    {
        "incident_id": "EVAL-NOM-08",
        "texto_titulo": "Colisión leve sin heridos",
        "texto_descripcion": "Choque por alcance entre dos turismos en carretera secundaria. Solo daños chapa, vehículos en el arcén que no obstaculizan.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "latitud": 40.9480, "longitud": -4.1180,
        "localidad": "Segovia", "provincia": "SEGOVIA",
        "fecha_incidente": "2026-06-16T17:10:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {"signal_accidente_trafico": True}
    },
    {
        "incident_id": "EVAL-NOM-09",
        "texto_titulo": "Petición de ambulancia ordinaria",
        "texto_descripcion": "Médico de atención primaria solicita ambulancia de traslado para paciente anciano con cuadro clínico estable hacia hospital comarcal.",
        "categoria_preliminar": "SANITARIO",
        "latitud": 41.6520, "longitud": -4.7280,
        "localidad": "Valladolid", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T12:00:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-NOM-10",
        "texto_titulo": "Rama caída en acera peatonal",
        "texto_descripcion": "Ciudadano informa de rama gruesa caída en acera peatonal. No dificulta el paso de vehículos, solo dificulta ligeramente paso peatonal.",
        "categoria_preliminar": "INCIDENCIA_VIA",
        "latitud": 41.6250, "longitud": -4.7300,
        "localidad": "Valladolid", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T15:20:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P4",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-NOM-11",
        "texto_titulo": "Farola pública apagada",
        "texto_descripcion": "Aviso de farola parpadeando o apagada en calle residencial. No representa riesgo de accidente.",
        "categoria_preliminar": "SUMINISTROS",
        "latitud": 42.3430, "longitud": -3.6960,
        "localidad": "Burgos", "provincia": "BURGOS",
        "fecha_incidente": "2026-06-16T22:30:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P4",
        "expected_signals": {}
    },

    # === GRUPO B: POR CATEGORÍA OPERATIVA (12 casos) ===
    {
        "incident_id": "EVAL-CAT-01",
        "texto_titulo": "Golpe leve en rotonda",
        "texto_descripcion": "Colisión por raspado entre dos turismos en rotonda. Ambos conductores fuera de los vehículos rellenando el parte, sin heridos.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Aranda de Duero", "provincia": "BURGOS",
        "fecha_incidente": "2026-06-16T08:45:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P4",
        "expected_signals": {"signal_accidente_trafico": True}
    },
    {
        "incident_id": "EVAL-CAT-02",
        "texto_titulo": "Pequeño conato forestal",
        "texto_descripcion": "Fuego de pastos y rastrojos en lindero de monte bajo, extensión muy pequeña y sin propagación activa.",
        "categoria_preliminar": "INCENDIO_FORESTAL",
        "localidad": "Toro", "provincia": "ZAMORA",
        "fecha_incidente": "2026-06-16T12:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {"signal_incendio": True}
    },
    {
        "incident_id": "EVAL-CAT-03",
        "texto_titulo": "Fuego en contenedor de cartón",
        "texto_descripcion": "Arde un contenedor de cartón en vía urbana pública. Sin riesgo para viviendas ni personas cercanas.",
        "categoria_preliminar": "INCENDIO_URBANO",
        "localidad": "Miranda de Ebro", "provincia": "BURGOS",
        "fecha_incidente": "2026-06-16T16:50:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P4",
        "expected_signals": {"signal_incendio": True}
    },
    {
        "incident_id": "EVAL-CAT-04",
        "texto_titulo": "Desprendimiento de rocas en ctra",
        "texto_descripcion": "Piedras caídas sobre la calzada en carretera de montaña. Obliga a invadir el sentido contrario con peligro de colisión.",
        "categoria_preliminar": "INCIDENCIA_VIA",
        "localidad": "Riaño", "provincia": "LEON",
        "fecha_incidente": "2026-06-16T11:00:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-CAT-05",
        "texto_titulo": "Caída de tejas por ráfagas",
        "texto_descripcion": "El viento fuerte está desprendiendo tejas de un tejado de tres alturas sobre una calle comercial concurrida. Zona acordonada.",
        "categoria_preliminar": "METEOROLOGIA",
        "localidad": "Benavente", "provincia": "ZAMORA",
        "fecha_incidente": "2026-06-16T14:10:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-CAT-06",
        "texto_titulo": "Derrame en gasolinera",
        "texto_descripcion": "Vertido de unos 50 litros de gasóleo en la zona de surtidores debido a un despiste del conductor de un camión cisterna.",
        "categoria_preliminar": "QUIMICO_NRBQ",
        "localidad": "Medina del Campo", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T09:10:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-CAT-07",
        "texto_titulo": "Mascota atrapada en rejilla",
        "texto_descripcion": "Aviso de un vecino que indica que hay un perro atrapado de una pata en la rejilla de una alcantarilla pública.",
        "categoria_preliminar": "RESCATE",
        "localidad": "Guardo", "provincia": "PALENCIA",
        "fecha_incidente": "2026-06-16T17:35:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P4",
        "expected_signals": {"signal_rescate": True}
    },
    {
        "incident_id": "EVAL-CAT-08",
        "texto_titulo": "Infarto agudo de miocardio",
        "texto_descripcion": "Varón de 58 años en su domicilio con dolor opresivo en el pecho que se irradia al brazo izquierdo, sudoración fría y disnea severa.",
        "categoria_preliminar": "SANITARIO",
        "localidad": "Burgos", "provincia": "BURGOS",
        "fecha_incidente": "2026-06-16T10:45:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"riesgo_vital_textual": True}
    },
    {
        "incident_id": "EVAL-CAT-09",
        "texto_titulo": "Pelea en discoteca con herido",
        "texto_descripcion": "Riña entre varias personas con botellazos. Hay una persona sangrando de la cabeza en el suelo, aturdida.",
        "categoria_preliminar": "SEGURIDAD_CIUDADANA",
        "localidad": "Ponferrada", "provincia": "LEON",
        "fecha_incidente": "2026-06-16T04:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-CAT-10",
        "texto_titulo": "Corte de luz crítico",
        "texto_descripcion": "Fallo de suministro eléctrico general en hospital comarcal. Afecta a quirófanos y urgencias, generadores de emergencia inestables.",
        "categoria_preliminar": "SUMINISTROS",
        "localidad": "Béjar", "provincia": "SALAMANCA",
        "fecha_incidente": "2026-06-16T13:20:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-CAT-11",
        "texto_titulo": "Consulta farmacia de guardia",
        "texto_descripcion": "Llamada de información de un ciudadano preguntando por la farmacia de guardia más cercana en Salamanca.",
        "categoria_preliminar": "OTROS",
        "localidad": "Salamanca", "provincia": "SALAMANCA",
        "fecha_incidente": "2026-06-16T23:55:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P4",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-CAT-12",
        "texto_titulo": "Llamada silenciosa",
        "texto_descripcion": "Se escucha ruido de fondo y respiración, pero nadie responde. Sin indicación explícita de riesgo o incidente.",
        "categoria_preliminar": "DESCONOCIDA",
        "localidad": "Ávila", "provincia": "AVILA",
        "fecha_incidente": "2026-06-16T14:40:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P4",
        "expected_signals": {}
    },

    # === GRUPO C: SEÑALES AISLADAS (10 casos) ===
    {
        "incident_id": "EVAL-SIG-01",
        "texto_titulo": "Fallecimiento en vía pública",
        "texto_descripcion": "Aviso de peatón tirado en la acera sin pulso ni respiración. El médico de atención primaria en el lugar confirma que está fallecido.",
        "categoria_preliminar": "SANITARIO",
        "localidad": "Zamora", "provincia": "ZAMORA",
        "fecha_incidente": "2026-06-16T07:30:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_fallecido": True}
    },
    {
        "incident_id": "EVAL-SIG-02",
        "texto_titulo": "Caída de altura con herido grave",
        "texto_descripcion": "Operario cae desde una altura de 3 metros. Presenta traumatismo craneoencefálico, herido grave inconsciente con sangrado profuso.",
        "categoria_preliminar": "SANITARIO",
        "localidad": "Burgos", "provincia": "BURGOS",
        "fecha_incidente": "2026-06-16T11:45:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_herido_grave": True}
    },
    {
        "incident_id": "EVAL-SIG-03",
        "texto_titulo": "Atrapamiento en ascensor",
        "texto_descripcion": "Dos personas atrapadas en cabina de ascensor bloqueada entre plantas de edificio residencial. Sin problemas médicos, ambiente tranquilo.",
        "categoria_preliminar": "RESCATE",
        "localidad": "Palencia", "provincia": "PALENCIA",
        "fecha_incidente": "2026-06-16T19:30:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {"signal_atrapado": True, "signal_rescate": True}
    },
    {
        "incident_id": "EVAL-SIG-04",
        "texto_titulo": "Dificultad por intoxicación CO",
        "texto_descripcion": "Llaman de vivienda donde la familia se siente mareada y con dolor de cabeza debido a mala combustión de estufa de gas. Posible intoxicación.",
        "categoria_preliminar": "SANITARIO",
        "localidad": "Soria", "provincia": "SORIA",
        "fecha_incidente": "2026-06-16T20:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {"signal_intoxicacion": True}
    },
    {
        "incident_id": "EVAL-SIG-05",
        "texto_titulo": "Varias llamadas por coche parado",
        "texto_descripcion": "Múltiples llamadas (más de 12 conductores) informando de un vehículo averiado cruzado en mitad de la calzada de la autovía A-62.",
        "categoria_preliminar": "INCIDENCIA_VIA",
        "localidad": "Tordesillas", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T08:20:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {"signal_varias_llamadas": True}
    },
    {
        "incident_id": "EVAL-SIG-06",
        "texto_titulo": "Incendio de garaje subterráneo",
        "texto_descripcion": "Fuego en sótano de edificio residencial. Salen llamas y humo muy denso, peligro de propagación al edificio y viviendas superiores.",
        "categoria_preliminar": "INCENDIO_URBANO",
        "localidad": "Salamanca", "provincia": "SALAMANCA",
        "fecha_incidente": "2026-06-16T22:00:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_incendio": True}
    },
    {
        "incident_id": "EVAL-SIG-07",
        "texto_titulo": "Accidente en carretera N-VI",
        "texto_descripcion": "Aviso de colisión por alcance con tres turismos involucrados. Ocupa carril principal, tráfico condicionado.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Cacabelos", "provincia": "LEON",
        "fecha_incidente": "2026-06-16T15:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {"signal_accidente_trafico": True}
    },
    {
        "incident_id": "EVAL-SIG-08",
        "texto_titulo": "Rescate en embalse",
        "texto_descripcion": "Bañista con problemas para salir del embalse de Aguilar de Campoo. Se agarra a una boya pero está fatigado y tiene calambres.",
        "categoria_preliminar": "RESCATE",
        "localidad": "Aguilar de Campoo", "provincia": "PALENCIA",
        "fecha_incidente": "2026-06-16T16:30:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {"signal_rescate": True}
    },
    {
        "incident_id": "EVAL-SIG-09",
        "texto_titulo": "Inundación por tormenta",
        "texto_descripcion": "Precipitación intensa causa el desbordamiento del arroyo, inundando la plaza del pueblo y sótanos colindantes.",
        "categoria_preliminar": "METEOROLOGIA",
        "localidad": "El Espinar", "provincia": "SEGOVIA",
        "fecha_incidente": "2026-06-16T17:40:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {"signal_meteo_inundacion": True}
    },
    {
        "incident_id": "EVAL-SIG-10",
        "texto_titulo": "Amenaza de riesgo vital inmediato",
        "texto_descripcion": "Atraco violento en sucursal bancaria. El atracador lleva un arma blanca y amenaza con apuñalar a los rehenes si se acerca la policía, riesgo vital.",
        "categoria_preliminar": "SEGURIDAD_CIUDADANA",
        "localidad": "Segovia", "provincia": "SEGOVIA",
        "fecha_incidente": "2026-06-16T11:30:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"riesgo_vital_textual": True}
    },

    # === GRUPO D: FRONTERA/AMBIGÜEDAD (8 casos) ===
    {
        "incident_id": "EVAL-AMB-01",
        "texto_titulo": "Grave accidente broma",
        "texto_descripcion": "Llamada urgente gritando: ¡Accidente terrible, coche explotando con atrapados! Luego se escuchan risas de adolescentes confirmando broma.",
        "categoria_preliminar": "OTROS",
        "localidad": "Medina de Rioseco", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T19:50:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P4",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-AMB-02",
        "texto_titulo": "Fuego Burgos",
        "texto_descripcion": "Fuego en Burgos. (llamada muy corta que se cuelga inmediatamente)",
        "categoria_preliminar": "INCENDIO_URBANO",
        "localidad": "Burgos", "provincia": "BURGOS",
        "fecha_incidente": "2026-06-16T12:05:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {"signal_incendio": True}
    },
    {
        "incident_id": "EVAL-AMB-03",
        "texto_titulo": "Incendio en nave química con atrapados",
        "texto_descripcion": "El incendio forestal ha alcanzado una zona industrial y se ha propagado a una nave de almacenamiento químico. Hay trabajadores atrapados.",
        "categoria_preliminar": "INCENDIO_FORESTAL",
        "localidad": "Venta de Baños", "provincia": "PALENCIA",
        "fecha_incidente": "2026-06-16T15:45:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_incendio": True, "signal_atrapado": True}
    },
    {
        "incident_id": "EVAL-AMB-04",
        "texto_titulo": "Accidente cisterna multirriesgo",
        "texto_descripcion": "Colisión frontal de camión cisterna inflamable contra turismo. Hay heridos graves atrapados, el gasóleo está ardiendo y el fuego amenaza masa forestal.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Guardo", "provincia": "PALENCIA",
        "fecha_incidente": "2026-06-16T16:10:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_accidente_trafico": True, "signal_incendio": True, "signal_atrapado": True, "signal_herido_grave": True}
    },
    {
        "incident_id": "EVAL-AMB-05",
        "texto_titulo": "Humo dudoso en descampado",
        "texto_descripcion": "Parece que hay una columna de humo negro en descampado cerca de la autovía, pero podría tratarse de polvo levantado por excavadoras de obra.",
        "categoria_preliminar": "OTROS",
        "localidad": "Valladolid", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T10:30:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P4",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-AMB-06",
        "texto_titulo": "Doble negación heridos",
        "texto_descripcion": "Mire, no es que no haya heridos en el vuelco del coche, es que hay varios pasajeros atrapados que no responden y están inconscientes.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "San Pedro Manrique", "provincia": "SORIA",
        "fecha_incidente": "2026-06-16T14:40:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_accidente_trafico": True, "signal_atrapado": True, "signal_herido_grave": True}
    },
    {
        "incident_id": "EVAL-AMB-07",
        "texto_titulo": "Temporal espectacular sin daños",
        "texto_descripcion": "Está granizando y lloviendo muchísimo en Ávila, cae una cantidad de agua tremenda del cielo, pero no se ha inundado nada de momento.",
        "categoria_preliminar": "METEOROLOGIA",
        "localidad": "Ávila", "provincia": "AVILA",
        "fecha_incidente": "2026-06-16T18:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P4",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-AMB-08",
        "texto_titulo": "Colisión fuerte con discusión",
        "texto_descripcion": "Choque fuerte entre dos coches en cruce urbano. La gente ha salido de los vehículos y está discutiendo fuertemente a gritos. No parece haber lesiones.",
        "categoria_preliminar": "SEGURIDAD_CIUDADANA",
        "localidad": "Salamanca", "provincia": "SALAMANCA",
        "fecha_incidente": "2026-06-16T13:10:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {}
    },

    # === GRUPO E: ROBUSTEZ LINGÜÍSTICA (8 casos) ===
    {
        "incident_id": "EVAL-ROB-01",
        "texto_titulo": "Choke ctra c/ atrpados",
        "texto_descripcion": "Choke frontal en ctra. con atrpados y herids gravs. Varios inconsientes. Enviar rekusos rapido.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Zamora", "provincia": "ZAMORA",
        "fecha_incidente": "2026-06-16T10:05:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_accidente_trafico": True, "signal_atrapado": True, "signal_herido_grave": True}
    },
    {
        "incident_id": "EVAL-ROB-02",
        "texto_titulo": "INCENDIO CON GENTE ATRAPADA",
        "texto_descripcion": "INCENDIO EN PLANTA ALTA DE CASA HABITADA HAY GENTE ATRAPADA PIDIENDO SOCORRO POR LAS VENTANAS RAPIDO",
        "categoria_preliminar": "INCENDIO_URBANO",
        "localidad": "Burgos", "provincia": "BURGOS",
        "fecha_incidente": "2026-06-16T14:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_incendio": True, "signal_atrapado": True}
    },
    {
        "incident_id": "EVAL-ROB-03",
        "texto_titulo": "Choque nacional con atrapado",
        "texto_descripcion": "Choque en la nacional con atrapado inconsciente, sin respiracion. Riesgo de parada respiratoria y muerte.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "León", "provincia": "LEON",
        "fecha_incidente": "2026-06-16T11:50:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_accidente_trafico": True, "signal_atrapado": True, "signal_herido_grave": True}
    },
    {
        "incident_id": "EVAL-ROB-04",
        "texto_titulo": "Acc. de traf. c/ heridos graves",
        "texto_descripcion": "Acc. de traf. c/ heridos graves en p.k. 143 de la N-I. Choque de camion contra mediana.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Burgos", "provincia": "BURGOS",
        "fecha_incidente": "2026-06-16T15:30:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_accidente_trafico": True, "signal_herido_grave": True}
    },
    {
        "incident_id": "EVAL-ROB-05",
        "texto_titulo": "Car crash near Salamanca",
        "texto_descripcion": "Car crash near Salamanca, one person is trapped in the vehicle. Head-on collision.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Salamanca", "provincia": "SALAMANCA",
        "fecha_incidente": "2026-06-16T12:10:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_accidente_trafico": True, "signal_atrapado": True}
    },
    {
        "incident_id": "EVAL-ROB-06",
        "texto_titulo": "Fuego en corrala vieja",
        "texto_descripcion": "Fuego en una corrala vieja con peligro de que arda la techumbre y las vigas de madera vieja de todo el bloque.",
        "categoria_preliminar": "INCENDIO_URBANO",
        "localidad": "Medina de Pomar", "provincia": "BURGOS",
        "fecha_incidente": "2026-06-16T17:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {"signal_incendio": True}
    },
    {
        "incident_id": "EVAL-ROB-07",
        "texto_titulo": "Aviso de fuego confuso",
        "texto_descripcion": "eh hola mire que es que hay un fuego en mi casa y y no se que hacer hay mucho humo y estoy asustado no veo nada de nada por el humo.",
        "categoria_preliminar": "INCENDIO_URBANO",
        "localidad": "Soria", "provincia": "SORIA",
        "fecha_incidente": "2026-06-16T13:40:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {"signal_incendio": True}
    },
    {
        "incident_id": "EVAL-ROB-08",
        "texto_titulo": "infecio en soria",
        "texto_descripcion": "infecio en soria cahe de arbol cndusctor erido grae",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Soria", "provincia": "SORIA",
        "fecha_incidente": "2026-06-16T16:25:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {"signal_herido_grave": True}
    },

    # === GRUPO F: POBLACIÓN VULNERABLE + EMPLAZAMIENTO (6 casos) ===
    {
        "incident_id": "EVAL-VUL-01",
        "texto_titulo": "Niño inconsciente en piscina",
        "texto_descripcion": "Aviso urgente por niño de 3 años inconsciente tras ahogamiento en piscina privada. Se le practican maniobras de RCP.",
        "categoria_preliminar": "SANITARIO",
        "localidad": "Simancas", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T12:05:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"riesgo_vital_textual": True}
    },
    {
        "incident_id": "EVAL-VUL-02",
        "texto_titulo": "Anciana perdida en campo",
        "texto_descripcion": "Anciana con demencia severa perdida en zona de monte bajo al anochecer, presenta hipotermia leve por baja temperatura.",
        "categoria_preliminar": "RESCATE",
        "localidad": "San Leonardo de Yagüe", "provincia": "SORIA",
        "fecha_incidente": "2026-06-16T21:05:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {"signal_rescate": True}
    },
    {
        "incident_id": "EVAL-VUL-03",
        "texto_titulo": "Fallo eléctrico UCI",
        "texto_descripcion": "Corte de suministro eléctrico crítico en UCI de hospital general. Las máquinas de soporte vital funcionan con baterías auxiliares de corta duración.",
        "categoria_preliminar": "SUMINISTROS",
        "localidad": "Zamora", "provincia": "ZAMORA",
        "fecha_incidente": "2026-06-16T13:05:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-VUL-04",
        "texto_titulo": "Parada gestante en domicilio",
        "texto_descripcion": "Llamada indicando que una mujer embarazada de 8 meses se encuentra en parada cardiorrespiratoria aparente en su domicilio.",
        "categoria_preliminar": "SANITARIO",
        "localidad": "León", "provincia": "LEON",
        "fecha_incidente": "2026-06-16T10:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"riesgo_vital_textual": True}
    },
    {
        "incident_id": "EVAL-VUL-05",
        "texto_titulo": "Fuego en surtidor gasolinera",
        "texto_descripcion": "Se declara incendio en un surtidor de combustible en estación de servicio de autovía. Alto riesgo de explosión.",
        "categoria_preliminar": "QUIMICO_NRBQ",
        "localidad": "Tordesillas", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T16:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_incendio": True}
    },
    {
        "incident_id": "EVAL-VUL-06",
        "texto_titulo": "Choque múltiple túnel",
        "texto_descripcion": "Colisión en cadena de tres turismos con incendio declarado en el interior de un túnel de autovía, mucho humo y evacuación en curso.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Guadarrama", "provincia": "SEGOVIA",
        "fecha_incidente": "2026-06-16T18:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_accidente_trafico": True, "signal_incendio": True}
    },

    # === GRUPO G: ACCESIBILIDAD + PROPAGACIÓN (5 casos) ===
    {
        "incident_id": "EVAL-ACC-01",
        "texto_titulo": "Hipotermia ventisca montaña",
        "texto_descripcion": "Dos montañeros con hipotermia severa atrapados en ventisca a gran altitud en Picos de Europa, acceso por aire bloqueado por viento y nieve.",
        "categoria_preliminar": "RESCATE",
        "localidad": "Posada de Valdeón", "provincia": "LEON",
        "fecha_incidente": "2026-06-16T19:20:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_rescate": True, "riesgo_vital_textual": True}
    },
    {
        "incident_id": "EVAL-ACC-02",
        "texto_titulo": "Incendio centro histórico",
        "texto_descripcion": "Incendio en vivienda de construcción de entramado de madera en pleno centro histórico de Segovia. Calles estrechas dificultan paso camiones.",
        "categoria_preliminar": "INCENDIO_URBANO",
        "localidad": "Segovia", "provincia": "SEGOVIA",
        "fecha_incidente": "2026-06-16T13:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_incendio": True}
    },
    {
        "incident_id": "EVAL-ACC-03",
        "texto_titulo": "Infarto pueblo remoto aislado",
        "texto_descripcion": "Infarto en pueblo remoto de Soria con accesos cortados por temporal de nieve. Quitanieves y soporte vital básico movilizados en convoy.",
        "categoria_preliminar": "SANITARIO",
        "localidad": "San Pedro Manrique", "provincia": "SORIA",
        "fecha_incidente": "2026-06-16T09:30:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"riesgo_vital_textual": True}
    },
    {
        "incident_id": "EVAL-ACC-04",
        "texto_titulo": "Propagación rápida forestal",
        "texto_descripcion": "Incendio forestal descontrolado propagándose a gran velocidad empujado por rachas de viento de más de 60 km/h hacia zona habitada.",
        "categoria_preliminar": "INCENDIO_FORESTAL",
        "localidad": "Lerma", "provincia": "BURGOS",
        "fecha_incidente": "2026-06-16T15:20:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_incendio": True}
    },
    {
        "incident_id": "EVAL-ACC-05",
        "texto_titulo": "Incendio industrial explosiones",
        "texto_descripcion": "Incendio en fábrica de pinturas y disolventes. Se registran fuertes explosiones secundarias, zona de exclusión establecida por seguridad.",
        "categoria_preliminar": "QUIMICO_NRBQ",
        "localidad": "Burgos", "provincia": "BURGOS",
        "fecha_incidente": "2026-06-16T16:20:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_incendio": True}
    },

    # === GRUPO H: CONTEO VÍCTIMAS (6 casos) ===
    {
        "incident_id": "EVAL-CNT-01",
        "texto_titulo": "Accidente 5 heridos 2 atrapados",
        "texto_descripcion": "Choque múltiple con 5 heridos graves de diversa consideración y al menos 2 personas atrapadas entre los hierros retorcidos.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Valladolid", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T10:10:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_accidente_trafico": True, "signal_atrapado": True, "signal_herido_grave": True}
    },
    {
        "incident_id": "EVAL-CNT-02",
        "texto_titulo": "Choque tres fallecidos",
        "texto_descripcion": "Accidente de tráfico gravísimo en la autovía, colisión frontal de dos turismos con tres personas fallecidas atrapadas en su interior.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Medina del Campo", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T12:00:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_accidente_trafico": True, "signal_atrapado": True, "signal_fallecido": True}
    },
    {
        "incident_id": "EVAL-CNT-03",
        "texto_titulo": "Varios heridos derrumbe",
        "texto_descripcion": "Varios heridos de diversa consideración tras derrumbe parcial del techo de un local comercial muy concurrido en pleno centro.",
        "categoria_preliminar": "SEGURIDAD_CIUDADANA",
        "localidad": "León", "provincia": "LEON",
        "fecha_incidente": "2026-06-16T18:10:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_herido_grave": True}
    },
    {
        "incident_id": "EVAL-CNT-04",
        "texto_titulo": "Derrumbe tren decenas contusionados",
        "texto_descripcion": "Descarrilamiento de un automotor de pasajeros de media distancia. Decenas de pasajeros heridos leves y con contusiones múltiples.",
        "categoria_preliminar": "RESCATE",
        "localidad": "Ávila", "provincia": "AVILA",
        "fecha_incidente": "2026-06-16T14:40:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_rescate": True}
    },
    {
        "incident_id": "EVAL-CNT-05",
        "texto_titulo": "Incendio almacén sin víctimas",
        "texto_descripcion": "Incendio en almacén de madera industrial. Los propietarios aseguran que no hay ninguna víctima ni personas dentro del recinto afectado.",
        "categoria_preliminar": "INCENDIO_URBANO",
        "localidad": "Palencia", "provincia": "PALENCIA",
        "fecha_incidente": "2026-06-16T17:20:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {"signal_incendio": True}
    },
    {
        "incident_id": "EVAL-CNT-06",
        "texto_titulo": "Alcance sin víctimas",
        "texto_descripcion": "Colisión por alcance menor entre dos turismos en vía de servicio urbana. No hay mención de heridos, solo daños menores.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Valladolid", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T15:20:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P4",
        "expected_signals": {"signal_accidente_trafico": True}
    },

    # === GRUPO I: NEGACIONES (5 casos) ===
    {
        "incident_id": "EVAL-NEG-01",
        "texto_titulo": "Vuelco espectacular sin heridos",
        "texto_descripcion": "Accidente de tráfico espectacular, camión cargado de fruta volcado en la mediana de la A-6. Conductor ileso, sin heridos.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Benavente", "provincia": "ZAMORA",
        "fecha_incidente": "2026-06-16T09:10:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {"signal_accidente_trafico": True}
    },
    {
        "incident_id": "EVAL-NEG-02",
        "texto_titulo": "Choque contra farola sin atrapados",
        "texto_descripcion": "Choque frontal contra una farola en vía urbana. Conductor aturdido y consciente, fuera del vehículo, sin atrapados.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Zamora", "provincia": "ZAMORA",
        "fecha_incidente": "2026-06-16T14:40:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {"signal_accidente_trafico": True}
    },
    {
        "incident_id": "EVAL-NEG-03",
        "texto_titulo": "Incendio sin fallecidos",
        "texto_descripcion": "Incendio en vivienda unifamiliar extinguido por vecinos. Confirman que no hay ningún fallecido ni herido en el incidente.",
        "categoria_preliminar": "INCENDIO_URBANO",
        "localidad": "Ávila", "provincia": "AVILA",
        "fecha_incidente": "2026-06-16T17:15:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {"signal_incendio": True}
    },
    {
        "incident_id": "EVAL-NEG-04",
        "texto_titulo": "Humo en motor sin llamas",
        "texto_descripcion": "Humo saliendo de un motor eléctrico en fábrica de automoción. No hay llamas ni fuego propagado. Trabajadores evacuados.",
        "categoria_preliminar": "SUMINISTROS",
        "localidad": "Valladolid", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T13:40:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P3",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-NEG-05",
        "texto_titulo": "Sin riesgos confirmados",
        "texto_descripcion": "No hay heridos ni atrapados ni fuego en la zona del incidente del choque menor de chapa entre dos coches en el arcén.",
        "categoria_preliminar": "ACCIDENTE_TRAFICO",
        "localidad": "Segovia", "provincia": "SEGOVIA",
        "fecha_incidente": "2026-06-16T16:25:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P4",
        "expected_signals": {"signal_accidente_trafico": True}
    },

    # === GRUPO J: TEMPORALIDAD (3 casos) ===
    {
        "incident_id": "EVAL-TMP-01",
        "texto_titulo": "Rescate montaña nocturno",
        "texto_descripcion": "Incidente nocturno: rescate en montaña a las 3:00 AM con visibilidad cero y fuerte ventisca en la cota superior.",
        "categoria_preliminar": "RESCATE",
        "localidad": "Riaño", "provincia": "LEON",
        "fecha_incidente": "2026-06-16T03:00:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {"signal_rescate": True}
    },
    {
        "incident_id": "EVAL-TMP-02",
        "texto_titulo": "Retención operación salida",
        "texto_descripcion": "Accidente menor provoca retención kilométrica en la operación salida de vacaciones de verano, calor extremo y conductores nerviosos.",
        "categoria_preliminar": "INCIDENCIA_VIA",
        "localidad": "Medina del Campo", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-08-01T15:00:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P2",
        "expected_signals": {}
    },
    {
        "incident_id": "EVAL-TMP-03",
        "texto_titulo": "Atropello hora de entrada escolar",
        "texto_descripcion": "Atropello en paso de peatones frente a colegio en hora de entrada escolar. Un menor herido grave tendido en el suelo con convulsiones.",
        "categoria_preliminar": "SANITARIO",
        "localidad": "Valladolid", "provincia": "VALLADOLID",
        "fecha_incidente": "2026-06-16T08:50:00+02:00",
        "operador_id": "OP-EVAL-01",
        "expected_priority": "P1",
        "expected_signals": {"signal_herido_grave": True}
    }
]


def execute_evaluation() -> dict:
    """Ejecuta los escenarios de evaluación a través del pipeline de 3 capas."""
    logger.info("Cargando componentes del pipeline...")
    extractor = FeatureExtractor()
    llm = QwenWrapper()
    
    # Verificar disponibilidad del LLM
    llm_online = llm.is_available()
    logger.info("Ollama LLM disponible: %s (Modelo: %s)", "SÍ" if llm_online else "NO (Degradado)", llm.model_name)
    
    # Cargar cache de ejecuciones previas para acelerar ejecuciones sucesivas
    cache_path = REPORTS_DIR / "empirical_evaluation_v0.1.0.json"
    cache_data = {}
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            logger.info("Caché de evaluaciones previas cargada desde %s", cache_path)
        except Exception as exc:
            logger.warning("No se pudo cargar la caché de evaluaciones previas: %s", exc)
            
    results = []
    
    for idx, s in enumerate(SCENARIOS, 1):
        # Intentar hit en caché primero
        cached_case = None
        if "cases" in cache_data:
            for c in cache_data["cases"]:
                if c.get("incident_id") == s["incident_id"] and c.get("predicted_priority") != "ERROR" and c.get("explanation") != "":
                    cached_case = c
                    break
        if cached_case:
            logger.info("[%d/%d] [Caché Hit] Reutilizando resultado de: %s", idx, len(SCENARIOS), s["incident_id"])
            results.append(cached_case)
            continue

        logger.info("[%d/%d] Ejecutando: %s (%s)", idx, len(SCENARIOS), s["incident_id"], s["texto_titulo"])
        
        # 1. Crear entrada
        lat = s.get("latitud")
        lon = s.get("longitud")
        
        # Forzar lat/lon emparejados si uno existe
        if lat is not None and lon is None:
            lon = -4.0
        elif lon is not None and lat is None:
            lat = 41.0
            
        incident = IncidentInput(
            incident_id=s["incident_id"],
            texto_titulo=s["texto_titulo"],
            texto_descripcion=s["texto_descripcion"],
            categoria_preliminar=CategoriaPreliminar(s["categoria_preliminar"]) if s["categoria_preliminar"] else None,
            latitud=lat,
            longitud=lon,
            localidad=s.get("localidad", "Valladolid"),
            provincia=ProvinciaCyL(s["provincia"]) if s.get("provincia") else ProvinciaCyL.VALLADOLID,
            fecha_incidente=datetime.fromisoformat(s["fecha_incidente"]),
            operador_id=s["operador_id"]
        )
        
        # 2. Capa 1 NLP
        t1_start = time.perf_counter()
        try:
            features = extractor.extract_features(incident)
            t1_err = None
        except Exception as exc:
            features = None
            t1_err = str(exc)
            logger.error("Error en Capa 1: %s", exc)
        t1_elapsed = (time.perf_counter() - t1_start) * 1000.0
        
        # 3. Capa 2 RuleFit
        t2_start = time.perf_counter()
        try:
            if features:
                priority_rec = predict(features)
                t2_err = None
            else:
                priority_rec = None
                t2_err = "No features extracted"
        except Exception as exc:
            priority_rec = None
            t2_err = str(exc)
            logger.error("Error en Capa 2: %s", exc)
        t2_elapsed = (time.perf_counter() - t2_start) * 1000.0
        
        # 4. Capa 3 LLM
        t3_start = time.perf_counter()
        try:
            if priority_rec:
                operator_rec = explain(priority_rec, incident.texto_descripcion or incident.texto_titulo, llm=llm)
                t3_err = None
            else:
                operator_rec = None
                t3_err = "No priority recommendation"
        except Exception as exc:
            operator_rec = None
            t3_err = str(exc)
            logger.error("Error en Capa 3: %s", exc)
        t3_elapsed = (time.perf_counter() - t3_start) * 1000.0
        
        total_elapsed = t1_elapsed + t2_elapsed + t3_elapsed
        
        # Comprobaciones contractuales
        contracts_ok = True
        contract_failures = []
        
        if features and priority_rec:
            # Suma de probabilidades aprox 1.0
            sum_probs = sum(priority_rec.probabilities.values())
            if not np.isclose(sum_probs, 1.0, atol=1e-4):
                contracts_ok = False
                contract_failures.append(f"Probabilidades no suman 1.0: {sum_probs}")
                
            # Coherencia argmax
            argmax_priority = max(priority_rec.probabilities, key=priority_rec.probabilities.get)
            if argmax_priority != priority_rec.priority_recommended:
                contracts_ok = False
                contract_failures.append(f"Recomendada ({priority_rec.priority_recommended}) no coincide con argmax ({argmax_priority})")
                
        if operator_rec:
            # Límites de longitud de explicación
            expl_len = len(operator_rec.explanation_text)
            if not (20 <= expl_len <= 1200):
                contracts_ok = False
                contract_failures.append(f"Explicación fuera de rango: {expl_len} caracteres")
                
            # Citas legales para P1/P2
            if operator_rec.priority_recommended in (Priority.P1, Priority.P2):
                if not operator_rec.legal_citations:
                    contracts_ok = False
                    contract_failures.append(f"Prioridad {operator_rec.priority_recommended} requiere citas legales")
                    
            # Temperatura en producción
            if operator_rec.llm_metadata.temperature != 0.0:
                contracts_ok = False
                contract_failures.append(f"Temperatura no es 0.0: {operator_rec.llm_metadata.temperature}")
        else:
            contracts_ok = False
            contract_failures.append("Fallo crítico en generación de OperatorRecommendation")
            
        results.append({
            "incident_id": s["incident_id"],
            "expected_priority": s["expected_priority"],
            "predicted_priority": priority_rec.priority_recommended.value if priority_rec else "ERROR",
            "probabilities": {p.value: float(v) for p, v in priority_rec.probabilities.items()} if priority_rec else {},
            "signals_detected": {
                name: bool(getattr(features, name).value)
                for name in s.get("expected_signals", {})
                if hasattr(features, name)
            } if features else {},
            "expected_signals": s.get("expected_signals", {}),
            "explanation": operator_rec.explanation_text if operator_rec else "",
            "confidence_disclaimer": operator_rec.confidence_disclaimer if operator_rec else "",
            "hints_count": len(operator_rec.actuation_hints) if operator_rec else 0,
            "citations_count": len(operator_rec.legal_citations) if operator_rec else 0,
            "llm_used": operator_rec.llm_metadata.llm_model if operator_rec else "None",
            "is_degraded": "degraded" in (operator_rec.llm_metadata.llm_model if operator_rec else "degraded"),
            "latency_capa1_ms": t1_elapsed,
            "latency_capa2_ms": t2_elapsed,
            "latency_capa3_ms": t3_elapsed,
            "latency_total_ms": total_elapsed,
            "contracts_ok": contracts_ok,
            "contract_failures": contract_failures,
            "capa1_err": t1_err,
            "capa2_err": t2_err,
            "capa3_err": t3_err,
        })
        
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "llm_online": llm_online,
        "model_name": llm.model_name,
        "cases": results
    }


def analyze_and_plot(payload: dict):
    """Calcula las métricas y genera gráficos."""
    df = pd.DataFrame(payload["cases"])
    
    # 1. Métricas de Clasificación
    y_true = df["expected_priority"].tolist()
    y_pred = df["predicted_priority"].tolist()
    
    accuracy = accuracy_score(y_true, y_pred)
    qwk = cohen_kappa_score(y_true, y_pred, weights="quadratic")
    
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=["P1", "P2", "P3", "P4"], zero_division=0
    )
    
    classes = ["P1", "P2", "P3", "P4"]
    per_class_metrics = {}
    for idx, c in enumerate(classes):
        per_class_metrics[c] = {
            "precision": float(precision[idx]),
            "recall": float(recall[idx]),
            "f1": float(f1[idx]),
            "support": int(support[idx])
        }
        
    # 2. Métricas de Seguridad 112 (Under/Over-triage)
    # Under-triage: Esperado P1, Predicho P3/P4
    p1_total = sum(1 for y in y_true if y == "P1")
    under_triage_p1_to_p3p4 = sum(
        1 for yt, yp in zip(y_true, y_pred) if yt == "P1" and yp in ("P3", "P4")
    )
    under_triage_rate = under_triage_p1_to_p3p4 / p1_total if p1_total > 0 else 0.0
    
    # Over-triage: Esperado P3/P4, Predicho P1
    p3p4_total = sum(1 for y in y_true if y in ("P3", "P4"))
    over_triage_p3p4_to_p1 = sum(
        1 for yt, yp in zip(y_true, y_pred) if yt in ("P3", "P4") and yp == "P1"
    )
    over_triage_rate = over_triage_p3p4_to_p1 / p3p4_total if p3p4_total > 0 else 0.0
    
    sensitivity_p1 = per_class_metrics["P1"]["recall"]
    
    # Specificity P4 (P4 predicho como P4 / total esperado P4)
    p4_total = sum(1 for y in y_true if y == "P4")
    specificity_p4 = sum(
        1 for yt, yp in zip(y_true, y_pred) if yt == "P4" and yp == "P4"
    ) / p4_total if p4_total > 0 else 0.0
    
    # 3. Métricas de Señales de Capa 1
    # Evaluar precisión de señales esperadas vs detectadas
    signal_results = []
    for r in payload["cases"]:
        for sig_name, sig_exp in r["expected_signals"].items():
            sig_obs = r["signals_detected"].get(sig_name, False)
            signal_results.append({"signal": sig_name, "expected": sig_exp, "observed": sig_obs})
    
    if signal_results:
        df_sig = pd.DataFrame(signal_results)
        sig_y_true = df_sig["expected"].tolist()
        sig_y_pred = df_sig["observed"].tolist()
        sig_prec, sig_rec, sig_f1, _ = precision_recall_fscore_support(
            sig_y_true, sig_y_pred, average="binary", zero_division=0
        )
    else:
        sig_prec, sig_rec, sig_f1 = 1.0, 1.0, 1.0
        
    # 4. Latencias
    latency_c1 = df["latency_capa1_ms"]
    latency_c2 = df["latency_capa2_ms"]
    latency_c3 = df["latency_capa3_ms"]
    latency_tot = df["latency_total_ms"]
    
    # 5. Explicaciones
    valid_exps = df[df["explanation"] != ""]
    avg_exp_len = valid_exps["explanation"].str.len().mean() if len(valid_exps) > 0 else 0.0
    avg_hints = df["hints_count"].mean()
    avg_citations = df["citations_count"].mean()
    
    # Calcular fidelidad: ¿La explicación contiene palabras clave de las señales activadas?
    fidelity_scores = []
    keywords_mapping = {
        "signal_fallecido": ["fallecido", "muerto", "óbito", "difunto", "cadáver"],
        "signal_herido_grave": ["herido grave", "inconsciente", "grave", "lesiones graves"],
        "signal_atrapado": ["atrapado", "atrapamiento", "excarcelación", "bloqueado"],
        "signal_intoxicacion": ["intoxicación", "intoxicado", "monóxido", "humo", "gas"],
        "signal_incendio": ["incendio", "fuego", "llamas", "quema"],
        "signal_accidente_trafico": ["accidente", "choque", "colisión", "vuelco"],
        "signal_rescate": ["rescate", "salvamento", "auxilio"],
        "signal_meteo_inundacion": ["inundación", "agua", "lluvia", "anegado"],
    }
    
    for r in payload["cases"]:
        expl = r["explanation"].lower()
        active_sigs = [k for k, v in r["expected_signals"].items() if v]
        if not active_sigs:
            continue
        hits = 0
        for sig in active_sigs:
            kws = keywords_mapping.get(sig, [])
            if any(kw in expl for kw in kws):
                hits += 1
        fidelity_scores.append(hits / len(active_sigs))
    avg_fidelity = np.mean(fidelity_scores) if fidelity_scores else 1.0
    
    # Guardar métricas en el payload
    payload["metrics"] = {
        "accuracy": float(accuracy),
        "qwk": float(qwk),
        "under_triage_rate": float(under_triage_rate),
        "over_triage_rate": float(over_triage_rate),
        "sensitivity_p1": float(sensitivity_p1),
        "specificity_p4": float(specificity_p4),
        "contracts_compliance_rate": float(df["contracts_ok"].mean()),
        "capa1_signals_precision": float(sig_prec),
        "capa1_signals_recall": float(sig_rec),
        "capa1_signals_f1": float(sig_f1),
        "capa3_avg_explanation_len": float(avg_exp_len),
        "capa3_avg_hints": float(avg_hints),
        "capa3_avg_citations": float(avg_citations),
        "capa3_explanation_fidelity": float(avg_fidelity),
        "latencies": {
            "capa1": {"mean": float(latency_c1.mean()), "p50": float(latency_c1.median()), "p95": float(latency_c1.quantile(0.95))},
            "capa2": {"mean": float(latency_c2.mean()), "p50": float(latency_c2.median()), "p95": float(latency_c2.quantile(0.95))},
            "capa3": {"mean": float(latency_c3.mean()), "p50": float(latency_c3.median()), "p95": float(latency_c3.quantile(0.95))},
            "total": {"mean": float(latency_tot.mean()), "p50": float(latency_tot.median()), "p95": float(latency_tot.quantile(0.95))},
        },
        "per_class": per_class_metrics
    }
    
    # ── GENERAR PLOTS ──
    logger.info("Generando gráficos de visualización...")
    sns.set_theme(style="whitegrid")
    
    # Plot 1: Confusion Matrix
    plt.figure(figsize=(7, 6))
    cm = confusion_matrix(y_true, y_pred, labels=["P1", "P2", "P3", "P4"])
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["P1", "P2", "P3", "P4"], yticklabels=["P1", "P2", "P3", "P4"])
    plt.title("Matriz de Confusión DSS 112 CyL", fontsize=14, fontweight="bold")
    plt.ylabel("Prioridad Esperada (Referencia)")
    plt.xlabel("Prioridad Predicha (Sistema)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "confusion_matrix.png", dpi=150)
    plt.close()
    
    # Plot 2: Distribución de Latencias por Capa
    plt.figure(figsize=(8, 5))
    latency_data = pd.DataFrame({
        "Capa 1 (NLP)": latency_c1,
        "Capa 2 (RuleFit)": latency_c2,
        "Capa 3 (LLM)": latency_c3
    })
    sns.boxplot(data=latency_data, palette="Set2")
    plt.yscale("log")
    plt.title("Distribución de Latencias por Capa (Escala Logarítmica)", fontsize=14, fontweight="bold")
    plt.ylabel("Tiempo de Ejecución (ms)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "latency_boxplot.png", dpi=150)
    plt.close()

    # Plot 3: Latencia Promedio (Bar Chart)
    plt.figure(figsize=(7, 5))
    means = [latency_c1.mean(), latency_c2.mean(), latency_c3.mean()]
    p95s = [latency_c1.quantile(0.95), latency_c2.quantile(0.95), latency_c3.quantile(0.95)]
    labels = ["Capa 1\n(NLP)", "Capa 2\n(RuleFit)", "Capa 3\n(LLM/MCP)"]
    x = np.arange(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, means, width, label="Media", color="#4f46e5")
    ax.bar(x + width/2, p95s, width, label="Percentil 95 (SLA)", color="#f59e0b")
    ax.set_ylabel("Milisegundos (ms)")
    ax.set_title("Latencias del Sistema: Media vs p95", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "latency_comparison.png", dpi=150)
    plt.close()
    
    # Plot 4: Distribución de Confianza/Probabilidades de la clase ganadora
    plt.figure(figsize=(8, 5))
    max_probs = [max(r["probabilities"].values()) for r in payload["cases"] if r["probabilities"]]
    sns.histplot(max_probs, kde=True, bins=15, color="#10b981")
    plt.title("Distribución de la Probabilidad Máxima Asignada", fontsize=14, fontweight="bold")
    plt.xlabel("Confianza (Probabilidad de la Clase Ganadora)")
    plt.ylabel("Cantidad de Casos")
    plt.xlim(0.25, 1.05)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "probability_confidence.png", dpi=150)
    plt.close()
    
    logger.info("Gráficos generados en: %s", FIGURES_DIR)


def write_reports(payload: dict):
    """Escribe los reportes en JSON y Markdown."""
    df = pd.DataFrame(payload["cases"])
    # Guardar JSON
    json_path = REPORTS_DIR / "empirical_evaluation_v0.1.0.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info("Reporte JSON escrito en: %s", json_path)
    
    # Crear Markdown
    md_path = REPORTS_DIR / "empirical_evaluation_v0.1.0.md"
    m = payload["metrics"]
    
    md_content = f"""# Reporte de Evaluación Empírica Exhaustiva del DSS 112 CyL

Generado: `{payload["generated_at"]}`
Modo LLM: `{"ONLINE" if payload["llm_online"] else "DEGRADADO"}`
Modelo LLM local: `{payload["model_name"]}`

---

## 1. Resumen Ejecutivo de Métricas

| Métrica | Valor obtenido | Umbral de Seguridad / Objetivo | Estado |
| :--- | :---: | :---: | :---: |
| **Accuracy (Exactitud)** | {m["accuracy"]:.4f} | >= 0.8500 | {"🟢 OK" if m["accuracy"] >= 0.85 else "🔴 Desviación"} |
| **Quadratic Weighted Kappa (QWK)** | {m["qwk"]:.4f} | >= 0.7000 (Acuerdo Ordinal) | {"🟢 Excelente" if m["qwk"] >= 0.7 else "🟡 Aceptable" if m["qwk"] >= 0.5 else "🔴 Pobre"} |
| **Under-triage Rate (P1 -> P3/P4)** | {m["under_triage_rate"]:.4%} | **0.00%** (Crítico para vidas) | {"🟢 0% Fallos Vidas" if m["under_triage_rate"] == 0.0 else "🔴 RIESGO DE SEGURIDAD"} |
| **Sensitivity P1 (Recall Vital)** | {m["sensitivity_p1"]:.4%} | >= 95.00% (Normativa CyL) | {"🟢 OK" if m["sensitivity_p1"] >= 0.95 else "🔴 Insuficiente"} |
| **Specificity P4 (No Saturación)** | {m["specificity_p4"]:.4%} | >= 85.00% | {"🟢 OK" if m["specificity_p4"] >= 0.85 else "🔴 Saturación de recursos"} |
| **Over-triage Rate (P3/P4 -> P1)** | {m["over_triage_rate"]:.4%} | <= 15.00% | {"🟢 OK" if m["over_triage_rate"] <= 0.15 else "🔴 Sobreasignación"} |
| **Fidelidad Explicación XAI** | {m["capa3_explanation_fidelity"]:.4%} | >= 80.00% (Consistencia textual) | {"🟢 Consistente" if m["capa3_explanation_fidelity"] >= 0.80 else "🔴 Inconsistencias"} |
| **Cumplimiento de Contratos Pydantic** | {m["contracts_compliance_rate"]:.4%} | **100.00%** (Robustez operacional) | {"🟢 100% Sólido" if m["contracts_compliance_rate"] == 1.0 else "🔴 Errores de Contrato"} |

---

## 2. Rendimiento por Clase (Prioridad)

| Prioridad | Precision | Recall (Sensibilidad) | F1-Score | Casos evaluados |
| :---: | :---: | :---: | :---: | :---: |
| **P1** (Riesgo Vital) | {m["per_class"]["P1"]["precision"]:.4f} | {m["per_class"]["P1"]["recall"]:.4f} | {m["per_class"]["P1"]["f1"]:.4f} | {m["per_class"]["P1"]["support"]} |
| **P2** (Grave) | {m["per_class"]["P2"]["precision"]:.4f} | {m["per_class"]["P2"]["recall"]:.4f} | {m["per_class"]["P2"]["f1"]:.4f} | {m["per_class"]["P2"]["support"]} |
| **P3** (Moderado) | {m["per_class"]["P3"]["precision"]:.4f} | {m["per_class"]["P3"]["recall"]:.4f} | {m["per_class"]["P3"]["f1"]:.4f} | {m["per_class"]["P3"]["support"]} |
| **P4** (Ordinario) | {m["per_class"]["P4"]["precision"]:.4f} | {m["per_class"]["P4"]["recall"]:.4f} | {m["per_class"]["P4"]["f1"]:.4f} | {m["per_class"]["P4"]["support"]} |

---

## 3. Matriz de Confusión

![Matriz de Confusión](figures/confusion_matrix.png)

---

## 4. Análisis de Latencias por Capa

| Capa / Componente | Media (ms) | Percentil 50 (p50) | Percentil 95 (p95) | SLA / Objetivo | Estado |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Capa 1 (NLP)** | {m["latencies"]["capa1"]["mean"]:.2f} ms | {m["latencies"]["capa1"]["p50"]:.2f} ms | {m["latencies"]["capa1"]["p95"]:.2f} ms | < 500 ms | {"🟢 OK" if m["latencies"]["capa1"]["p95"] < 500 else "🔴 Lento"} |
| **Capa 2 (RuleFit)** | {m["latencies"]["capa2"]["mean"]:.2f} ms | {m["latencies"]["capa2"]["p50"]:.2f} ms | {m["latencies"]["capa2"]["p95"]:.2f} ms | < 200 ms | {"🟢 OK" if m["latencies"]["capa2"]["p95"] < 200 else "🔴 Lento"} |
| **Capa 3 (LLM/MCP)** | {m["latencies"]["capa3"]["mean"]:.2f} ms | {m["latencies"]["capa3"]["p50"]:.2f} ms | {m["latencies"]["capa3"]["p95"]:.2f} ms | < 2000 ms | {"🟢 OK" if m["latencies"]["capa3"]["p95"] < 2000 else "🔴 Lento"} |
| **Total Sistema (E2E)** | {m["latencies"]["total"]["mean"]:.2f} ms | {m["latencies"]["total"]["p50"]:.2f} ms | {m["latencies"]["total"]["p95"]:.2f} ms | < 2700 ms | {"🟢 OK" if m["latencies"]["total"]["p95"] < 2700 else "🔴 Lento"} |

---

## 5. Alineación Normativa PLANCAL (Castilla y León)

El sistema mapea las prioridades de triage del 112 con los niveles oficiales de activación definidos en el Plan de Protección Civil de Castilla y León (**PLANCAL**, Decreto 4/2019):
- **P1** → Activa el **Nivel 2/3** del PLANCAL (movilización total de recursos autonómicos/nacionales y aviso a CECOP).
- **P2** → Activa el **Nivel 1** del PLANCAL (movilización de recursos especializados de la zona y alerta al jefe de guardia).
- **P3** → Activa el **Nivel 0** del PLANCAL (seguimiento operativo por recursos locales, sin despliegue coordinado global).
- **P4** → Sin activación oficial. Derivación a servicios ordinarios.

### Análisis de consistencia de explicaciones (Fidelidad XAI)
La fidelidad del explicador en la Capa 3 obtuvo un **{m["capa3_explanation_fidelity"]:.2%}**, lo que indica que en la inmensa mayoría de los casos las señales de la Capa 1 que decidieron la prioridad fueron explícitamente citadas y razonadas de forma correcta por el modelo.

---

## 6. Historial de Casos con Errores / Desviaciones

"""
    # Agregar casos de error
    errors = df[df["expected_priority"] != df["predicted_priority"]]
    if len(errors) > 0:
        md_content += "\n### Casos con discrepancia de clasificación:\n\n"
        md_content += "| ID | Texto Incidente | Esperado | Predicho | Razón / Explicación |\n"
        md_content += "| :---: | :--- | :---: | :---: | :--- |\n"
        for _, r in errors.iterrows():
            desc = r["explanation"][:200] + "..." if len(r["explanation"]) > 200 else r["explanation"]
            md_content += f"| `{r['incident_id']}` | {r['incident_id']} | **{r['expected_priority']}** | `{r['predicted_priority']}` | {desc} |\n"
    else:
        md_content += "\n### 🎉 ¡Cero discrepancias de clasificación en todos los casos evaluados!\n"

    # Agregar fallos contractuales
    contract_errs = df[df["contracts_ok"] == False]
    if len(contract_errs) > 0:
        md_content += "\n### Casos con fallos de contrato:\n\n"
        md_content += "| ID | Fallos reportados |\n"
        md_content += "| :---: | :--- |\n"
        for _, r in contract_errs.iterrows():
            failures_str = "; ".join(r["contract_failures"])
            md_content += f"| `{r['incident_id']}` | {failures_str} |\n"
            
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    logger.info("Reporte Markdown escrito en: %s", md_path)


def main():
    logger.info("Iniciando evaluación empírica exhaustiva del DSS 112 CyL...")
    t_start = time.time()
    
    payload = execute_evaluation()
    
    analyze_and_plot(payload)
    write_reports(payload)
    
    elapsed = time.time() - t_start
    logger.info("Evaluación completada con éxito en %.2f segundos.", elapsed)
    
    # Imprimir un resumen rápido en consola
    cases_df = pd.DataFrame(payload["cases"])
    total = len(cases_df)
    correct = (cases_df["expected_priority"] == cases_df["predicted_priority"]).sum()
    failed_contracts = (cases_df["contracts_ok"] == False).sum()
    p1_fn = sum(1 for c in payload["cases"] if c["expected_priority"] == "P1" and c["predicted_priority"] in ("P3", "P4"))
    
    print("\n" + "="*50)
    print("RESUMEN RÁPIDO DE LA EVALUACIÓN:")
    print(f"Total escenarios ejecutados: {total}")
    print(f"Clasificación correcta: {correct}/{total} ({correct/total:.2%})")
    print(f"Bajo-triage crítico P1: {p1_fn} casos")
    print(f"Casos con fallos contractuales: {failed_contracts}")
    print(f"Reporte MD guardado en: {REPORTS_DIR / 'empirical_evaluation_v0.1.0.md'}")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
