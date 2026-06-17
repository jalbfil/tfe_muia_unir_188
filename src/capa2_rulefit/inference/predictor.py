"""Wrapper inicial de inferencia Capa 2.

T050-T052 dejan preparado el contrato estable. T054-T056 sustituiran o
complementaran este baseline con un modelo RuleFit entrenado.
"""

from __future__ import annotations

import operator
from functools import lru_cache
from pathlib import Path
from typing import Any

from contracts import (
    Accesibilidad,
    ActivatedRule,
    CategoriaPreliminar,
    ConfidenceLevel,
    IncidentFeatures,
    ModelUsed,
    NormaID,
    Priority,
    PriorityRecommendation,
)

from capa2_rulefit.baseline_expert.rules import evaluate_baseline_rules
from capa2_rulefit.rulefit import incident_features_to_row

MODEL_VERSION_CAPA2 = "0.1.0"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RULEFIT_MODEL = PROJECT_ROOT / "artifacts" / "models" / "capa2" / "v0.1.0" / "rulefit.joblib"


def _confidence_level(p_max: float) -> ConfidenceLevel:
    if p_max >= 0.80:
        return ConfidenceLevel.HIGH
    if p_max >= 0.60:
        return ConfidenceLevel.MEDIUM
    if p_max >= 0.40:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.UNKNOWN


def _priority_scores(features: IncidentFeatures) -> dict[Priority, float]:
    scores = {
        Priority.P1: 0.20,
        Priority.P2: 0.25,
        Priority.P3: 0.30,
        Priority.P4: 0.25,
    }
    hits = evaluate_baseline_rules(features)
    for hit in hits:
        scores[hit.rule.target_priority] += hit.contribution
    active_priorities = {hit.rule.target_priority for hit in hits}
    if Priority.P1 in active_priorities:
        scores[Priority.P1] = max(scores.values()) + 0.75
    elif Priority.P2 in active_priorities:
        scores[Priority.P2] = max(scores.values()) + 0.35
    has_urgent_rule = any(
        hit.rule.target_priority in (Priority.P1, Priority.P2)
        for hit in hits
    )
    if not has_urgent_rule:
        if features.numero_victimas_estimado.value <= 0 and features.numero_llamadas == 1:
            scores[Priority.P4] += 0.8
        else:
            scores[Priority.P3] += 0.5
    return scores


def _normalise(scores: dict[Priority, float]) -> dict[Priority, float]:
    total = sum(scores.values())
    raw = {priority: value / total for priority, value in scores.items()}
    rounded = {priority: round(value, 6) for priority, value in raw.items()}
    drift = round(1.0 - sum(rounded.values()), 6)
    winner = max(rounded, key=rounded.get)
    rounded[winner] = round(rounded[winner] + drift, 6)
    return rounded


# Operadores de comparación admitidos en las reglas RuleFit (orden importa: los
# de dos caracteres deben comprobarse antes que los de uno).
_RULE_OPS: list[tuple[str, Any]] = [
    ("<=", operator.le),
    (">=", operator.ge),
    ("==", operator.eq),
    ("<", operator.lt),
    (">", operator.gt),
]


def _rule_satisfied_by_row(rule_text: str, row: dict[str, Any]) -> bool:
    """True si el incidente (row) satisface TODAS las condiciones de la regla.

    Las reglas RuleFit son conjunciones tipo
    ``"signal_accidente_trafico <= 0.500 & signal_rescate > 0.500"``.
    Si alguna condición no se puede evaluar, la regla se considera no satisfecha
    (criterio conservador para no mostrar reglas no verificables como activadas).
    """
    for condition in rule_text.split("&"):
        condition = condition.strip()
        if not condition:
            continue
        for symbol, op in _RULE_OPS:
            if symbol in condition:
                feature_name, _, threshold = condition.partition(symbol)
                try:
                    threshold_value = float(threshold.strip())
                except ValueError:
                    return False
                try:
                    feature_value = float(row.get(feature_name.strip(), 0.0))
                except (TypeError, ValueError):
                    feature_value = 0.0
                if not op(feature_value, threshold_value):
                    return False
                break
        else:
            # Condición sin operador reconocible → no verificable.
            return False
    return True


def _activated_rules(features: IncidentFeatures) -> list[ActivatedRule]:
    hits = sorted(
        evaluate_baseline_rules(features),
        key=lambda hit: abs(hit.rule.weight),
        reverse=True,
    )
    return [
        ActivatedRule(
            rule_id=hit.rule.rule_id,
            human_text=hit.rule.human_text,
            weight=hit.rule.weight,
            normative_anchors=hit.rule.normative_anchors,
        )
        for hit in hits[:30]
    ]


@lru_cache(maxsize=1)
def _load_rulefit_model() -> Any | None:
    if not DEFAULT_RULEFIT_MODEL.exists():
        return None
    try:
        import joblib
    except ImportError:
        return None
    try:
        return joblib.load(DEFAULT_RULEFIT_MODEL)
    except Exception:
        return None


def _rulefit_recommendation(features: IncidentFeatures) -> PriorityRecommendation | None:
    model = _load_rulefit_model()
    if model is None:
        return None
    row = incident_features_to_row(features)
    try:
        probabilities_raw = model.predict_proba_from_row(row)
    except Exception:
        # If persisted RuleFit artifacts are incompatible with the active
        # runtime, degrade gracefully to the interpretable baseline.
        return None
    probabilities = {Priority(label): value for label, value in probabilities_raw.items()}
    recommended = max(probabilities, key=probabilities.get)
    p_max = probabilities[recommended]
    top_rules = model.top_rules_for_label(recommended.value, limit=30)
    # Solo se reportan como "activadas" las reglas que el incidente realmente
    # satisface (coherencia con el path baseline). Mostrar reglas no satisfechas
    # como activadas es engañoso para el operador y rompe la trazabilidad.
    activated_rules = [
        ActivatedRule(
            rule_id=str(rule["rule_id"]),
            human_text=str(rule["rule"])[:200],
            weight=float(rule["coef"]),
            normative_anchors=[],
        )
        for rule in top_rules
        if _rule_satisfied_by_row(str(rule["rule"]), row)
    ]
    # Si ninguna regla estadística RuleFit se satisface, recurrir a las reglas
    # expertas baseline que el incidente SÍ satisface: aportan trazabilidad real
    # y anclas normativas para el operador.
    if not activated_rules:
        activated_rules = _activated_rules(features)
    return PriorityRecommendation(
        incident_id=features.incident_id,
        priority_recommended=recommended,
        probabilities=probabilities,
        activated_rules=activated_rules,
        confidence_level=_confidence_level(p_max),
        model_used=ModelUsed.RULEFIT,
        model_version_capa2=MODEL_VERSION_CAPA2,
        requires_human_attention=recommended in (Priority.P1, Priority.P2) or p_max < 0.60,
    )


def _apply_safety_gate(rec: PriorityRecommendation, features: IncidentFeatures) -> PriorityRecommendation:
    """Aplica controles de seguridad deterministas según la normativa PLANCAL y Ley 17/2015."""
    priority = rec.priority_recommended
    rules = list(rec.activated_rules)
    
    force_p1 = False
    force_p2 = False
    rule_id = ""
    human_text = ""
    anchors = []

    # 1. Force P1 criteria (Nivel 2/3 PLANCAL)
    if features.signal_fallecido.value or features.riesgo_vital_textual.value or features.riesgo_vital.value:
        force_p1 = True
        rule_id = "SAFE-GATE-P1-RIESGO-VITAL"
        human_text = "Puerta de seguridad: Presencia de fallecido, riesgo vital inminente o soporte vital detectado."
        anchors = [NormaID.LEY_17_2015, NormaID.PLANCAL_DEC_4_2019]
    elif features.multirriesgo.value and features.emplazamiento_critico.value:
        force_p1 = True
        rule_id = "SAFE-GATE-P1-MULTIRRIESGO-CRITICO"
        human_text = "Puerta de seguridad: Incidente multirriesgo en emplazamiento crítico (infraestructura o afluencia masiva)."
        anchors = [NormaID.PLANCAL_DEC_4_2019]
    elif features.tipo_incidente_normalizado == CategoriaPreliminar.INCENDIO_FORESTAL and features.riesgo_propagacion.value:
        force_p1 = True
        rule_id = "SAFE-GATE-P1-INCENDIO-FORESTAL-PROPAGACION"
        human_text = "Puerta de seguridad: Incendio forestal de rápida propagación con amenaza potencial."
        anchors = [NormaID.PLANCAL_DEC_4_2019]
    elif features.signal_incendio.value and features.riesgo_propagacion.value and features.emplazamiento_critico.value:
        force_p1 = True
        rule_id = "SAFE-GATE-P1-INCENDIO-CRITICO-PROPAGACION"
        human_text = "Puerta de seguridad: Incendio con riesgo de propagación en emplazamiento crítico o industrial."
        anchors = [NormaID.PLANCAL_DEC_4_2019]
    elif features.signal_intoxicacion.value and features.signal_herido_grave.value:
        force_p1 = True
        rule_id = "SAFE-GATE-P1-INTOXICACION-GRAVE"
        human_text = "Puerta de seguridad: Intoxicación severa o fuga química con víctimas graves o inconscientes."
        anchors = [NormaID.PLANCAL_DEC_4_2019]
    elif features.signal_rescate.value and features.accesibilidad_recursos == Accesibilidad.BAJA and features.signal_herido_grave.value:
        force_p1 = True
        rule_id = "SAFE-GATE-P1-RESCATE-COMPLEJO-GRAVE"
        human_text = "Puerta de seguridad: Rescate en condiciones de baja accesibilidad con víctimas en estado grave."
        anchors = [NormaID.PLANCAL_DEC_4_2019]
    elif features.numero_victimas_estimado.value >= 3 and (features.signal_herido_grave.value or features.signal_rescate.value or features.signal_accidente_trafico.value):
        force_p1 = True
        rule_id = "SAFE-GATE-P1-MULTIPLE-VICTIMAS"
        human_text = f"Puerta de seguridad: Accidente o incidente grave con múltiples víctimas estimadas ({features.numero_victimas_estimado.value})."
        anchors = [NormaID.PLANCAL_DEC_4_2019]

    # 2. Force P2 criteria (Nivel 1 PLANCAL, only if not forced to P1)
    if not force_p1:
        if (features.signal_herido_grave.value or 
            features.signal_atrapado.value or 
            features.signal_intoxicacion.value or 
            features.signal_rescate.value):
            force_p2 = True
            rule_id = "SAFE-GATE-P2-OPERATIVO"
            human_text = "Puerta de seguridad: Herido grave, atrapamiento, intoxicación o rescate activo. Respuesta coordinada obligatoria."
            anchors = [NormaID.PLANCAL_DEC_4_2019]
        elif features.signal_meteo_inundacion.value and features.emplazamiento_critico.value:
            force_p2 = True
            rule_id = "SAFE-GATE-P2-METEO-CRITICO"
            human_text = "Puerta de seguridad: Inundación o temporal afectando a edificaciones o emplazamiento crítico."
            anchors = [NormaID.PLANCAL_DEC_4_2019]

    if force_p1:
        if priority != Priority.P1:
            priority = Priority.P1
            rules.insert(0, ActivatedRule(
                rule_id=rule_id,
                human_text=human_text,
                weight=10.0,
                normative_anchors=anchors
            ))
    elif force_p2:
        if priority in (Priority.P3, Priority.P4):
            priority = Priority.P2
            rules.insert(0, ActivatedRule(
                rule_id=rule_id,
                human_text=human_text,
                weight=8.0,
                normative_anchors=anchors
            ))

    if priority == rec.priority_recommended:
        return rec

    # Recalcular probabilidades para reflejar la prioridad forzada (darle probabilidad dominante)
    new_probs = {p: 0.01 for p in Priority}
    new_probs[priority] = 0.97
    total = sum(new_probs.values())
    normalized_probs = {p: round(v / total, 6) for p, v in new_probs.items()}
    winner = max(normalized_probs, key=normalized_probs.get)
    normalized_probs[winner] = round(normalized_probs[winner] + (1.0 - sum(normalized_probs.values())), 6)

    return PriorityRecommendation(
        incident_id=rec.incident_id,
        priority_recommended=priority,
        probabilities=normalized_probs,
        activated_rules=rules,
        confidence_level=ConfidenceLevel.HIGH,
        model_used=rec.model_used,
        model_version_capa2=rec.model_version_capa2,
        requires_human_attention=True,
    )


def predict(features: IncidentFeatures) -> PriorityRecommendation:
    """Predice prioridad P1-P4 cumpliendo el contrato de Capa 2."""

    rulefit_prediction = _rulefit_recommendation(features)
    if rulefit_prediction is not None:
        return _apply_safety_gate(rulefit_prediction, features)

    probabilities = _normalise(_priority_scores(features))
    recommended = max(probabilities, key=probabilities.get)
    p_max = probabilities[recommended]
    rec = PriorityRecommendation(
        incident_id=features.incident_id,
        priority_recommended=recommended,
        probabilities=probabilities,
        activated_rules=_activated_rules(features),
        confidence_level=_confidence_level(p_max),
        model_used=ModelUsed.BASELINE_EXPERT,
        model_version_capa2=MODEL_VERSION_CAPA2,
        requires_human_attention=recommended in (Priority.P1, Priority.P2) or p_max < 0.60,
    )
    return _apply_safety_gate(rec, features)
