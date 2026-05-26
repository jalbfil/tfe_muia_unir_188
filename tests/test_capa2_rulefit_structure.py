from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "src" / "contracts"))

from capa2_rulefit.inference import predict
from contracts import (
    Accesibilidad,
    BoolWithConfidence,
    CategoriaPreliminar,
    ConfidenceLevel,
    GravedadLesiones,
    IncidentFeatures,
    IntWithConfidence,
    ModelUsed,
    Priority,
    PriorityRecommendation,
)


def _b(value: bool, confidence: float = 0.9) -> BoolWithConfidence:
    return BoolWithConfidence(value=value, confidence=confidence)


def _features_p1() -> IncidentFeatures:
    return IncidentFeatures(
        incident_id="INC-T050-P1",
        riesgo_vital=_b(True),
        numero_victimas_estimado=IntWithConfidence(value=2, confidence=0.8),
        gravedad_lesiones=GravedadLesiones.CRITICA,
        gravedad_lesiones_confidence=0.9,
        tipo_incidente_normalizado=CategoriaPreliminar.ACCIDENTE_TRAFICO,
        poblacion_vulnerable=_b(False),
        numero_llamadas=3,
        emplazamiento_critico=_b(False),
        riesgo_propagacion=_b(False),
        multirriesgo=_b(False),
        avisos_simultaneos_zona=0,
        accesibilidad_recursos=Accesibilidad.MEDIA,
        signal_fallecido=_b(True),
        signal_herido_grave=_b(True),
        signal_atrapado=_b(True),
        signal_intoxicacion=_b(False),
        signal_varias_llamadas=_b(True),
        signal_incendio=_b(False),
        signal_accidente_trafico=_b(True),
        signal_rescate=_b(False),
        signal_meteo_inundacion=_b(False),
        riesgo_vital_textual=_b(True),
        model_version_capa1="0.1.0",
        inference_timestamp=datetime.now(timezone.utc),
        inference_latency_ms=12.0,
    )


def test_t051_predict_returns_valid_priority_recommendation() -> None:
    recommendation = predict(_features_p1())

    assert isinstance(recommendation, PriorityRecommendation)
    assert recommendation.incident_id == "INC-T050-P1"
    assert recommendation.model_used is ModelUsed.BASELINE_EXPERT


def test_t052_probability_and_rule_invariants() -> None:
    recommendation = predict(_features_p1())

    assert abs(sum(recommendation.probabilities.values()) - 1.0) <= 1e-6
    assert recommendation.priority_recommended == max(
        recommendation.probabilities, key=recommendation.probabilities.get
    )
    assert len(recommendation.activated_rules) <= 30
    assert recommendation.priority_recommended is Priority.P1
    assert recommendation.activated_rules
    assert recommendation.confidence_level in {
        ConfidenceLevel.HIGH,
        ConfidenceLevel.MEDIUM,
        ConfidenceLevel.LOW,
    }
