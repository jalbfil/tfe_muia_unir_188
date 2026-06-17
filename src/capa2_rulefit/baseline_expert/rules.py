"""Adaptador de reglas expertas al contrato Pydantic de Capa 2.

La logica pura vive en `expert_rules.py` para poder evaluarse sobre CSV sin
dependencias extra. Este modulo traduce los hits a `OperationalRule`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from contracts import (
    Accesibilidad,
    IncidentFeatures,
    NormaID,
    OperationalRule,
    Priority,
    VariableSource,
)

from .expert_rules import apply_expert_rules


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


def _feature_row(features: IncidentFeatures) -> dict[str, object]:
    return {
        "riesgo_vital": features.riesgo_vital.value,
        "numero_victimas_estimado": features.numero_victimas_estimado.value,
        "tipo_incidente_normalizado": features.tipo_incidente_normalizado.value,
        "numero_llamadas": features.numero_llamadas,
        "accesibilidad_recursos": features.accesibilidad_recursos.value
        if isinstance(features.accesibilidad_recursos, Accesibilidad)
        else str(features.accesibilidad_recursos),
        "signal_fallecido": features.signal_fallecido.value,
        "signal_herido_grave": features.signal_herido_grave.value,
        "signal_atrapado": features.signal_atrapado.value,
        "signal_intoxicacion": features.signal_intoxicacion.value,
        "signal_varias_llamadas": features.signal_varias_llamadas.value,
        "signal_incendio": features.signal_incendio.value,
        "signal_accidente_trafico": features.signal_accidente_trafico.value,
        "signal_rescate": features.signal_rescate.value,
        "signal_meteo_inundacion": features.signal_meteo_inundacion.value,
        "riesgo_vital_textual": features.riesgo_vital_textual.value,
    }


def evaluate_baseline_rules(features: IncidentFeatures) -> list[RuleHit]:
    """Devuelve reglas expertas activadas a partir de features predecisionales."""

    hits: list[RuleHit] = []
    for hit in apply_expert_rules(_feature_row(features)):
        rule = _rule(
            rule_id=hit.rule_id,
            condition_expression=hit.condition_expression,
            human_text=hit.human_text,
            target_priority=Priority(hit.target_priority),
            weight=hit.weight,
            anchors=[NormaID(anchor) for anchor in hit.normative_anchors],
        )
        hits.append(RuleHit(rule=rule, contribution=hit.weight))
    return hits
