"""Stubs de Capa 1 (NLP) y Capa 2 (RuleFit) para v0.1.0-backend.

Estos stubs producen salidas válidas según los contratos mientras las
implementaciones reales (Fases 3 y 4) no están disponibles.

Capa 1 stub: heurístico léxico desde IncidentInput → IncidentFeatures.
Capa 2 stub: reglas deterministas desde IncidentFeatures → PriorityRecommendation.

IMPORTANTE: estos stubs NO son los modelos reales. Son placeholders que
permiten levantar el backend y ejecutar los tests de integración.
"""
from __future__ import annotations

import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from contracts import (  # type: ignore[import]
    Accesibilidad,
    ActivatedRule,
    BoolWithConfidence,
    CategoriaPreliminar,
    ConfidenceLevel,
    GravedadLesiones,
    IncidentFeatures,
    IncidentInput,
    IntWithConfidence,
    ModelUsed,
    NormaID,
    Priority,
    PriorityRecommendation,
)

_MODEL_VERSION_CAPA1 = "0.1.0"
_MODEL_VERSION_CAPA2 = "0.1.0"

# ── señales léxicas ────────────────────────────────────────────────────────────

_KW_FALLECIDO = {"fallecido", "muerto", "exánime", "cadáver", "cadaver"}
_KW_HERIDO_GRAVE = {"grave", "crítico", "critico", "inconsciente", "herido"}
_KW_ATRAPADO = {"atrapado", "atrapada", "aprisionado", "aprisionada", "encajado"}
_KW_INTOXICACION = {"intoxicado", "intoxicación", "intoxicacion", "quimico", "químico", "vapor", "gas"}
_KW_LLAMADAS = {"varios", "varias", "testigos", "llamadas", "reiterado", "múltiples", "multiples"}
_KW_INCENDIO = {"incendio", "fuego", "llamas", "humo", "ardiendo", "quema"}
_KW_ACCIDENTE = {"accidente", "choque", "colisión", "colision", "vuelco", "atropello"}
_KW_RESCATE = {"rescate", "rescatar", "salvamento", "barranquismo", "montaña"}
_KW_METEO = {"inundación", "inundacion", "crecida", "desbordamiento", "granizo", "tornado"}
_KW_VITAL = {"inconsciente", "riesgo vital", "parada", "cardiaca", "ahogando", "atrapado"}


def _detect(text: str, keywords: set[str], threshold: float = 0.85) -> BoolWithConfidence:
    """Detecta si alguna keyword aparece en el texto (case-insensitive)."""
    lower = text.lower()
    found = any(kw in lower for kw in keywords)
    return BoolWithConfidence(value=found, confidence=threshold if found else 0.5)


def _false_signal() -> BoolWithConfidence:
    return BoolWithConfidence(value=False, confidence=0.5)


# ── Capa 1 stub ───────────────────────────────────────────────────────────────

def stub_extract_features(input: IncidentInput) -> IncidentFeatures:
    """Extracción de características heurística desde IncidentInput.

    Placeholder hasta T047 (Capa 1 NLP real).
    """
    t0 = time.perf_counter()
    text = f"{input.texto_titulo} {input.texto_descripcion}"

    signal_fallecido = _detect(text, _KW_FALLECIDO)
    signal_herido_grave = _detect(text, _KW_HERIDO_GRAVE)
    signal_atrapado = _detect(text, _KW_ATRAPADO)
    signal_intoxicacion = _detect(text, _KW_INTOXICACION)
    signal_varias_llamadas = _detect(text, _KW_LLAMADAS)
    signal_incendio = _detect(text, _KW_INCENDIO)
    signal_accidente_trafico = _detect(text, _KW_ACCIDENTE)
    signal_rescate = _detect(text, _KW_RESCATE)
    signal_meteo_inundacion = _detect(text, _KW_METEO)
    riesgo_vital_textual = _detect(text, _KW_VITAL)

    # V01: riesgo vital
    riesgo_vital_val = (
        signal_fallecido.value
        or signal_herido_grave.value
        or signal_atrapado.value
        or riesgo_vital_textual.value
    )
    riesgo_vital = BoolWithConfidence(value=riesgo_vital_val, confidence=0.80)

    # V02: número víctimas estimado
    num_victimas = IntWithConfidence(value=-1, confidence=0.5)

    # V03: gravedad
    if signal_fallecido.value:
        gravedad = GravedadLesiones.CRITICA
        grav_conf = 0.90
    elif signal_herido_grave.value or signal_atrapado.value:
        gravedad = GravedadLesiones.GRAVE
        grav_conf = 0.80
    else:
        gravedad = GravedadLesiones.LEVE
        grav_conf = 0.50

    # V04: tipo incidente
    tipo = input.categoria_preliminar or CategoriaPreliminar.DESCONOCIDA

    # V05: población vulnerable
    poblacion_vulnerable = _false_signal()

    # V06: número llamadas
    num_llamadas = 3 if signal_varias_llamadas.value else 1

    # V07: emplazamiento crítico
    emplazamiento_critico = _false_signal()

    # V12: riesgo propagación
    riesgo_propagacion = BoolWithConfidence(
        value=signal_incendio.value or signal_intoxicacion.value,
        confidence=0.70,
    )
    # V13: multiriesgo
    multirriesgo = BoolWithConfidence(
        value=(signal_incendio.value and signal_atrapado.value),
        confidence=0.60,
    )
    # V14: avisos simultáneos
    avisos_simulta = 2 if signal_varias_llamadas.value else 0

    latency_ms = (time.perf_counter() - t0) * 1000

    return IncidentFeatures(
        incident_id=input.incident_id,
        riesgo_vital=riesgo_vital,
        numero_victimas_estimado=num_victimas,
        gravedad_lesiones=gravedad,
        gravedad_lesiones_confidence=grav_conf,
        tipo_incidente_normalizado=tipo,
        poblacion_vulnerable=poblacion_vulnerable,
        numero_llamadas=num_llamadas,
        emplazamiento_critico=emplazamiento_critico,
        riesgo_propagacion=riesgo_propagacion,
        multirriesgo=multirriesgo,
        avisos_simultaneos_zona=avisos_simulta,
        accesibilidad_recursos=Accesibilidad.MEDIA,
        signal_fallecido=signal_fallecido,
        signal_herido_grave=signal_herido_grave,
        signal_atrapado=signal_atrapado,
        signal_intoxicacion=signal_intoxicacion,
        signal_varias_llamadas=signal_varias_llamadas,
        signal_incendio=signal_incendio,
        signal_accidente_trafico=signal_accidente_trafico,
        signal_rescate=signal_rescate,
        signal_meteo_inundacion=signal_meteo_inundacion,
        riesgo_vital_textual=riesgo_vital_textual,
        model_version_capa1=_MODEL_VERSION_CAPA1,
        inference_timestamp=datetime.now(tz=UTC),
        inference_latency_ms=latency_ms,
    )


# ── Capa 2 stub ───────────────────────────────────────────────────────────────

def _make_probs(priority: Priority, p_high: float) -> dict[Priority, float]:
    """Distribuye la probabilidad restante entre las otras clases."""
    rem = (1.0 - p_high) / 3.0
    probs = {p: rem for p in Priority}
    probs[priority] = p_high
    # Asegurar que suma exactamente 1.0
    total = sum(probs.values())
    probs[priority] += 1.0 - total  # absorbe error de punto flotante
    return probs


def _confidence_from_pmax(p_max: float) -> ConfidenceLevel:
    if p_max >= 0.80:
        return ConfidenceLevel.HIGH
    if p_max >= 0.60:
        return ConfidenceLevel.MEDIUM
    if p_max >= 0.40:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.UNKNOWN


def stub_predict_priority(features: IncidentFeatures) -> PriorityRecommendation:
    """Clasificación heurística de prioridad desde IncidentFeatures.

    Placeholder hasta T056 (Capa 2 RuleFit real).
    Reglas en orden de prioridad decreciente:
      P1: riesgo vital + atrapado/fallecido
      P2: riesgo vital sin atrapado, o intoxicación masiva
      P3: incendio sin víctimas, rescate sin riesgo vital
      P4: sin señales de riesgo significativo
    """
    rv = features.riesgo_vital.value
    atrapado = features.signal_atrapado.value
    fallecido = features.signal_fallecido.value
    herido_grave = features.signal_herido_grave.value
    intoxicacion = features.signal_intoxicacion.value
    incendio = features.signal_incendio.value
    rescate = features.signal_rescate.value

    if rv and (atrapado or fallecido):
        priority = Priority.P1
        p_max = 0.88
        rules = [
            ActivatedRule(
                rule_id="SR-01",
                human_text="Riesgo vital con atrapamiento o fallecido confirmado → P1 inmediata",
                weight=1.0,
                normative_anchors=[NormaID.LEY_17_2015, NormaID.PLANCAL_DEC_4_2019],
            )
        ]
    elif rv and herido_grave:
        priority = Priority.P1
        p_max = 0.84
        rules = [
            ActivatedRule(
                rule_id="SR-02",
                human_text="Riesgo vital con herido grave documentado → P1",
                weight=0.95,
                normative_anchors=[NormaID.LEY_17_2015],
            )
        ]
    elif rv or intoxicacion:
        priority = Priority.P2
        p_max = 0.75
        rules = [
            ActivatedRule(
                rule_id="SR-03",
                human_text="Riesgo vital presente o intoxicación activa → P2",
                weight=0.80,
                normative_anchors=[NormaID.PLANCAL_DEC_4_2019],
            )
        ]
    elif incendio or rescate:
        priority = Priority.P3
        p_max = 0.72
        rules = [
            ActivatedRule(
                rule_id="SR-04",
                human_text="Incendio activo o rescate sin riesgo vital → P3",
                weight=0.70,
                normative_anchors=[NormaID.PLANCAL_DEC_4_2019],
            )
        ]
    else:
        priority = Priority.P4
        p_max = 0.82
        rules = []

    probs = _make_probs(priority, p_max)
    confidence = _confidence_from_pmax(p_max)
    requires_attention = priority in (Priority.P1, Priority.P2)

    return PriorityRecommendation(
        incident_id=features.incident_id,
        priority_recommended=priority,
        probabilities=probs,
        activated_rules=rules,
        confidence_level=confidence,
        model_used=ModelUsed.BASELINE_EXPERT,
        model_version_capa2=_MODEL_VERSION_CAPA2,
        requires_human_attention=requires_attention,
    )
