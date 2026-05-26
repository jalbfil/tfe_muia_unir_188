"""Reglas expertas iniciales para priorizacion P1-P4.

Este modulo es el punto de partida defendible antes de entrenar RuleFit:
convierte variables estructuradas de Capa 1 en reglas trazables y pesos.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from contracts import IncidentFeatures, NormaID, OperationalRule, Priority, VariableSource


@dataclass(frozen=True)
class RuleHit:
    rule: OperationalRule
    contribution: float


def _rule(
    *,
    rule_id: str,
    condition_expression: str,
    human_text: str,
    target_priority: Priority,
    weight: float,
    anchors: list[NormaID],
) -> OperationalRule:
    now = datetime.now(timezone.utc)
    return OperationalRule(
        rule_id=rule_id,
        source=VariableSource.EXPERT_BASELINE,
        condition_expression=condition_expression,
        human_text=human_text,
        target_priority=target_priority,
        weight=weight,
        normative_anchors=anchors,
        created_at=now,
        updated_at=now,
    )


def evaluate_baseline_rules(features: IncidentFeatures) -> list[RuleHit]:
    """Devuelve reglas expertas activadas a partir de features predecisionales."""

    hits: list[RuleHit] = []

    if features.riesgo_vital.value or features.signal_fallecido.value:
        rule = _rule(
            rule_id="EXP-P1-RIESGO-VITAL",
            condition_expression="riesgo_vital or signal_fallecido",
            human_text="Riesgo vital o fallecimiento indicado en el incidente",
            target_priority=Priority.P1,
            weight=3.2,
            anchors=[NormaID.LEY_17_2015, NormaID.PLANCAL_DEC_4_2019],
        )
        hits.append(RuleHit(rule=rule, contribution=rule.weight))

    if features.signal_herido_grave.value or features.signal_atrapado.value:
        rule = _rule(
            rule_id="EXP-P2-GRAVE-ATRAPADO",
            condition_expression="signal_herido_grave or signal_atrapado",
            human_text="Heridos graves o personas atrapadas requieren respuesta prioritaria",
            target_priority=Priority.P2,
            weight=2.4,
            anchors=[NormaID.LEY_17_2015, NormaID.PLANCAL_DEC_4_2019],
        )
        hits.append(RuleHit(rule=rule, contribution=rule.weight))

    if features.signal_intoxicacion.value or features.signal_incendio.value:
        rule = _rule(
            rule_id="EXP-P2-INCENDIO-TOXICO",
            condition_expression="signal_intoxicacion or signal_incendio",
            human_text="Incendio o intoxicacion con potencial de evolucion grave",
            target_priority=Priority.P2,
            weight=1.9,
            anchors=[NormaID.PLANCAL_DEC_4_2019, NormaID.MPCYL_ACUERDO_3_2008],
        )
        hits.append(RuleHit(rule=rule, contribution=rule.weight))

    if features.signal_rescate.value or features.accesibilidad_recursos.value == "BAJA":
        rule = _rule(
            rule_id="EXP-P2-RESCATE-ACCESO",
            condition_expression="signal_rescate or accesibilidad_recursos == BAJA",
            human_text="Rescate o acceso dificil aumenta complejidad operativa",
            target_priority=Priority.P2,
            weight=1.7,
            anchors=[NormaID.PLANCAL_DEC_4_2019],
        )
        hits.append(RuleHit(rule=rule, contribution=rule.weight))

    if features.signal_accidente_trafico.value or features.signal_varias_llamadas.value:
        rule = _rule(
            rule_id="EXP-P3-TRAFICO-MULTILLAMADA",
            condition_expression="signal_accidente_trafico or signal_varias_llamadas",
            human_text="Accidente o varias llamadas justifican seguimiento operativo",
            target_priority=Priority.P3,
            weight=1.1,
            anchors=[NormaID.REGISTRO_112_CYL],
        )
        hits.append(RuleHit(rule=rule, contribution=rule.weight))

    if features.signal_meteo_inundacion.value or features.riesgo_propagacion.value:
        rule = _rule(
            rule_id="EXP-P3-METEO-PROPAGACION",
            condition_expression="signal_meteo_inundacion or riesgo_propagacion",
            human_text="Riesgo meteorologico o propagacion requiere vigilancia",
            target_priority=Priority.P3,
            weight=1.0,
            anchors=[NormaID.INUNCYL, NormaID.PLANCAL_DEC_4_2019],
        )
        hits.append(RuleHit(rule=rule, contribution=rule.weight))

    return hits
