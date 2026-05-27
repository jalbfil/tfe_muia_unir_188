"""Baseline experto P1-P4 basado en seniales predecisionales.

No depende de Pydantic para poder evaluarse sobre CSV en entornos minimos. El
adaptador de `rules.py` convierte estos resultados al contrato oficial.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable

PriorityLabel = str
FeatureRow = dict[str, object]


@dataclass(frozen=True)
class ExpertRule:
    rule_id: str
    target_priority: PriorityLabel
    weight: float
    condition_expression: str
    human_text: str
    normative_anchors: tuple[str, ...]
    predicate: Callable[[FeatureRow], bool]

    def to_metadata(self) -> dict[str, object]:
        data = asdict(self)
        data.pop("predicate")
        data["normative_anchors"] = list(self.normative_anchors)
        return data


@dataclass(frozen=True)
class ExpertRuleHit:
    rule_id: str
    target_priority: PriorityLabel
    weight: float
    condition_expression: str
    human_text: str
    normative_anchors: tuple[str, ...]

    @classmethod
    def from_rule(cls, rule: ExpertRule) -> ExpertRuleHit:
        return cls(
            rule_id=rule.rule_id,
            target_priority=rule.target_priority,
            weight=rule.weight,
            condition_expression=rule.condition_expression,
            human_text=rule.human_text,
            normative_anchors=rule.normative_anchors,
        )


def _bool(row: FeatureRow, key: str) -> bool:
    value = row.get(key)
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() == "true"


def _int(row: FeatureRow, key: str, default: int = 0) -> int:
    value = row.get(key)
    if hasattr(value, "value"):
        value = getattr(value, "value")
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _text(row: FeatureRow) -> str:
    return " ".join(
        str(row.get(key, "") or "")
        for key in (
            "texto_operativo_norm",
            "titulo_limpio",
            "descripcion_limpia",
            "tipo_incidente_normalizado",
            "categoria_operativa_preliminar",
        )
    ).lower()


def _category(row: FeatureRow, expected: str) -> bool:
    expected_norm = expected.lower()
    incident_type = str(row.get("tipo_incidente_normalizado", "")).lower()
    preliminary = str(row.get("categoria_operativa_preliminar", "")).lower()
    return expected_norm in incident_type or expected_norm in preliminary


EXPERT_RULES: tuple[ExpertRule, ...] = (
    ExpertRule(
        "EXP-P1-FALLECIDO",
        "P1",
        3.8,
        "signal_fallecido",
        "Fallecimiento indicado en el texto o seniales lexicas",
        ("LEY_17_2015", "PLANCAL_DEC_4_2019"),
        lambda row: _bool(row, "signal_fallecido") or "fallece" in _text(row),
    ),
    ExpertRule(
        "EXP-P1-RIESGO-VITAL",
        "P1",
        3.4,
        "riesgo_vital or riesgo_vital_textual",
        "Riesgo vital explicito requiere maxima prioridad academica",
        ("LEY_17_2015", "PLANCAL_DEC_4_2019"),
        lambda row: _bool(row, "riesgo_vital") or _bool(row, "riesgo_vital_textual"),
    ),
    ExpertRule(
        "EXP-P1-CRITICO-ATRAPADO",
        "P1",
        2.7,
        "signal_herido_grave and signal_atrapado",
        "Herido grave atrapado combina dano personal y rescate urgente",
        ("LEY_17_2015", "PLANCAL_DEC_4_2019"),
        lambda row: _bool(row, "signal_herido_grave") and _bool(row, "signal_atrapado"),
    ),
    ExpertRule(
        "EXP-P1-MULTIVICTIMA",
        "P1",
        2.5,
        "numero_victimas_estimado >= 3 and riesgo_vital",
        "Multiples victimas con riesgo vital elevan el incidente a P1",
        ("LEY_17_2015", "PLANCAL_DEC_4_2019"),
        lambda row: _int(row, "numero_victimas_estimado") >= 3 and _bool(row, "riesgo_vital"),
    ),
    ExpertRule(
        "EXP-P2-HERIDO-GRAVE",
        "P2",
        2.1,
        "signal_herido_grave",
        "Herido grave sin fallecimiento mantiene prioridad alta",
        ("LEY_17_2015", "PLANCAL_DEC_4_2019"),
        lambda row: _bool(row, "signal_herido_grave"),
    ),
    ExpertRule(
        "EXP-P2-ATRAPADO",
        "P2",
        2.0,
        "signal_atrapado",
        "Persona atrapada exige coordinacion operativa prioritaria",
        ("PLANCAL_DEC_4_2019",),
        lambda row: _bool(row, "signal_atrapado"),
    ),
    ExpertRule(
        "EXP-P2-INTOXICACION",
        "P2",
        1.9,
        "signal_intoxicacion",
        "Intoxicacion o riesgo NRBQ requiere escalado preventivo",
        ("MPCYL_ACUERDO_3_2008", "PLANCAL_DEC_4_2019"),
        lambda row: _bool(row, "signal_intoxicacion") or "intoxic" in _text(row),
    ),
    ExpertRule(
        "EXP-P2-INCENDIO-VIVIENDA",
        "P2",
        1.8,
        "signal_incendio and (sanitario or urbano or vivienda)",
        "Incendio en entorno habitado puede evolucionar rapidamente",
        ("PLANCAL_DEC_4_2019", "LEY_4_2007_CYL"),
        lambda row: _bool(row, "signal_incendio") and any(
            term in _text(row) for term in ("vivienda", "urbano", "sanitario", "edificio")
        ),
    ),
    ExpertRule(
        "EXP-P2-RESCATE",
        "P2",
        1.7,
        "signal_rescate",
        "Rescate implica complejidad tecnica y coordinacion de recursos",
        ("PLANCAL_DEC_4_2019",),
        lambda row: _bool(row, "signal_rescate"),
    ),
    ExpertRule(
        "EXP-P2-TRAFICO-GRAVE",
        "P2",
        1.6,
        "signal_accidente_trafico and signal_herido_grave",
        "Accidente de trafico con heridos graves requiere respuesta prioritaria",
        ("LEY_17_2015", "REGISTRO_112_CYL"),
        lambda row: _bool(row, "signal_accidente_trafico") and _bool(row, "signal_herido_grave"),
    ),
    ExpertRule(
        "EXP-P2-METEORO-ALTO-IMPACTO",
        "P2",
        1.4,
        "signal_meteo_inundacion and signal_varias_llamadas",
        "Inundacion o meteorologia adversa con varias llamadas sugiere impacto zonal",
        ("INUNCYL", "PLANCAL_DEC_4_2019"),
        lambda row: _bool(row, "signal_meteo_inundacion") and _bool(row, "signal_varias_llamadas"),
    ),
    ExpertRule(
        "EXP-P3-ACCIDENTE-TRAFICO",
        "P3",
        1.0,
        "signal_accidente_trafico",
        "Accidente de trafico sin senial critica conserva prioridad de seguimiento",
        ("REGISTRO_112_CYL",),
        lambda row: _bool(row, "signal_accidente_trafico"),
    ),
    ExpertRule(
        "EXP-P3-VARIAS-LLAMADAS",
        "P3",
        0.9,
        "signal_varias_llamadas",
        "Varias llamadas aumentan plausibilidad e impacto operativo",
        ("REGISTRO_112_CYL",),
        lambda row: _bool(row, "signal_varias_llamadas"),
    ),
    ExpertRule(
        "EXP-P3-INCENDIO-SIN-VICTIMAS",
        "P3",
        0.9,
        "signal_incendio",
        "Incendio sin victimas explicitas requiere vigilancia y recursos",
        ("LEY_4_2007_CYL", "PLANCAL_DEC_4_2019"),
        lambda row: _bool(row, "signal_incendio"),
    ),
    ExpertRule(
        "EXP-P3-METEO-INUNDACION",
        "P3",
        0.8,
        "signal_meteo_inundacion",
        "Incidente meteorologico o inundacion requiere seguimiento territorial",
        ("INUNCYL",),
        lambda row: _bool(row, "signal_meteo_inundacion"),
    ),
    ExpertRule(
        "EXP-P4-SIN-SENALES-CRITICAS",
        "P4",
        0.8,
        "no critical signals and numero_llamadas == 1",
        "Ausencia de seniales criticas y llamada unica sugiere prioridad baja",
        ("REGISTRO_112_CYL",),
        lambda row: not any(
            _bool(row, key)
            for key in (
                "signal_fallecido",
                "signal_herido_grave",
                "signal_atrapado",
                "signal_intoxicacion",
                "signal_incendio",
                "signal_accidente_trafico",
                "signal_rescate",
                "signal_meteo_inundacion",
            )
        )
        and _int(row, "numero_llamadas", 1) <= 1,
    ),
)


def apply_expert_rules(row: FeatureRow) -> list[ExpertRuleHit]:
    return [ExpertRuleHit.from_rule(rule) for rule in EXPERT_RULES if rule.predicate(row)]


def predict_expert(row: FeatureRow) -> dict[str, object]:
    hits = apply_expert_rules(row)
    scores = {"P1": 0.15, "P2": 0.25, "P3": 0.35, "P4": 0.25}
    for hit in hits:
        scores[hit.target_priority] += hit.weight
    active_priorities = {hit.target_priority for hit in hits}
    if "P1" in active_priorities:
        scores["P1"] = max(scores.values()) + 0.75
    elif "P2" in active_priorities:
        scores["P2"] = max(scores.values()) + 0.35
    total = sum(scores.values())
    probabilities = {label: round(value / total, 6) for label, value in scores.items()}
    winner = max(probabilities, key=probabilities.get)
    probabilities[winner] = round(probabilities[winner] + (1.0 - sum(probabilities.values())), 6)
    return {
        "priority_recommended": winner,
        "probabilities": probabilities,
        "activated_rules": [hit.__dict__ for hit in hits],
    }


def export_rules_metadata() -> list[dict[str, object]]:
    return [rule.to_metadata() for rule in EXPERT_RULES]
