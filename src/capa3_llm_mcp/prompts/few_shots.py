"""T074 — Few-shots para el explicador de Capa 3 (3 ejemplos: P1, P3, P4).

Cada ejemplo incluye: contexto de incidente, reglas activadas y la respuesta
JSON esperada. Se insertan en el historial de chat como pares user/assistant
antes del incidente real.
"""
from __future__ import annotations

# Estructura: lista de tuplas (user_context, assistant_json)
# El orquestador los convierte a mensajes {"role": "user"/"assistant", "content": ...}

FEW_SHOTS: list[tuple[str, str]] = [
    # ── P1: riesgo vital inmediato ─────────────────────────────────────────────
    (
        """\
INCIDENTE: "Conductor atrapado en vehículo volcado, posibles fracturas graves, carretera N-122 km 45, Zamora."
PRIORIDAD RECOMENDADA: P1
REGLAS ACTIVADAS:
- [RD-01] Víctimas atrapadas con riesgo vital confirmado → P1 fija (Ley 17/2015 art. 1).
- [RD-09] Variable V03 = CRÍTICA → P1 fija.
FRAGMENTOS NORMATIVOS:
- Ley 17/2015 art. 1: "La ley regula el Sistema Nacional de Protección Civil para la planificación, \
prevención e intervención en emergencias."
- PLANCAL Decreto 4/2019: "Las emergencias con riesgo vital activan el nivel de respuesta máximo."
""",
        """\
{
  "explanation_text": "Emergencia de prioridad máxima: conductor atrapado con posible riesgo vital. \
Se activan protocolos de rescate inmediato conforme a Ley 17/2015 y PLANCAL. La demora puede \
comprometer la supervivencia.",
  "actuation_hints": [
    "Movilizar unidad de rescate y soporte vital avanzado de forma inmediata",
    "Notificar al CECOP Castilla y León para coordinación de recursos",
    "Establecer perímetro de seguridad en N-122 km 45 y cortar tráfico"
  ],
  "confidence_disclaimer": "Alta confianza: dos reglas de prioridad máxima activadas."
}""",
    ),
    # ── P3: emergencia seria sin riesgo vital inmediato ───────────────────────
    (
        """\
INCIDENTE: "Incendio controlado en vivienda unifamiliar, sin personas en el interior, \
humo visible desde exterior, Salamanca capital."
PRIORIDAD RECOMENDADA: P3
REGLAS ACTIVADAS:
- [RD-05] Incendio activo sin víctimas confirmadas → P3 mínima.
- [RD-07] Sin indicador de propagación → rebaja de P2 a P3.
FRAGMENTOS NORMATIVOS:
- INFOCAL Decreto 6/2025: "Los incendios en zona urbana sin víctimas se gestionan \
en nivel de alerta 2."
""",
        """\
{
  "explanation_text": "Incendio en vivienda sin ocupantes reportados. Situación bajo control \
inicial pero requiere presencia de bomberos para extinción y comprobación de ausencia de víctimas. \
Nivel de alerta 2 según INFOCAL.",
  "actuation_hints": [
    "Enviar dotación de bomberos para extinción y verificación de desalojo",
    "Confirmar ausencia de personas en el interior con vecinos",
    "Monitorear posible propagación a edificios colindantes"
  ],
  "confidence_disclaimer": null
}""",
    ),
    # ── P4: aviso informativo / preventivo ────────────────────────────────────
    (
        """\
INCIDENTE: "Ciudadano reporta árbol caído en calzada tras viento fuerte, sin heridos, \
tráfico parcialmente cortado, carretera CL-605, Segovia."
PRIORIDAD RECOMENDADA: P4
REGLAS ACTIVADAS:
- [RD-10] Incidente sin lesionados ni riesgo vital → P4.
FRAGMENTOS NORMATIVOS:
- Ley 4/2007 CyL art. 5: "La gestión de vías corresponde a la administración titular; \
el 112 coordina la información."
""",
        """\
{
  "explanation_text": "Aviso preventivo: árbol caído en calzada sin heridos. \
Requiere actuación de mantenimiento vial. El 112 coordina la notificación a la \
Diputación de Segovia como titular de la vía.",
  "actuation_hints": [
    "Notificar a la Diputación Provincial de Segovia para retirada del obstáculo",
    "Informar a Tráfico para señalización del punto afectado"
  ],
  "confidence_disclaimer": null
}""",
    ),
]
