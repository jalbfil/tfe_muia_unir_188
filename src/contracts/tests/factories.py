"""Factories deterministas polyfactory para todos los modelos de `contracts`.

Usadas por la suite local y por tests cross-capa para construir payloads válidos
sin acoplarse a fixtures concretas. Cada factory respeta TODAS las invariantes
declarativas y semánticas del modelo correspondiente.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use

from contracts import (
    ActivatedRule,
    BoolWithConfidence,
    ConfidenceLevel,
    GravedadLesiones,
    IncidentFeatures,
    IncidentInput,
    InferenceLog,
    IntWithConfidence,
    LegalCitation,
    LLMMetadata,
    ModelUsed,
    NormaID,
    OperationalRule,
    OperatorDecision,
    OperatorRecommendation,
    Priority,
    PriorityRecommendation,
    VariableSource,
    WeakLabel,
    compute_input_hash,
)

_MADRID = timezone(timedelta(hours=2))  # CEST aproximada para fixtures


# ── Primitivos ───────────────────────────────────────────────────────────


class BoolWithConfidenceFactory(ModelFactory[BoolWithConfidence]):
    __model__ = BoolWithConfidence
    confidence = Use(lambda: 0.85)


class IntWithConfidenceFactory(ModelFactory[IntWithConfidence]):
    __model__ = IntWithConfidence
    value = Use(lambda: 2)
    confidence = Use(lambda: 0.80)


# ── E-01 ────────────────────────────────────────────────────────────────


class IncidentInputFactory(ModelFactory[IncidentInput]):
    __model__ = IncidentInput

    incident_id = Use(lambda: "INC-2024-000001")
    texto_titulo = Use(lambda: "Accidente con varios heridos en N-VI")
    texto_descripcion = Use(lambda: "Colisión frontal, dos atrapados, salida de combustible.")
    latitud = Use(lambda: 41.6523)
    longitud = Use(lambda: -4.7245)
    localidad = Use(lambda: "Valladolid")
    fecha_incidente = Use(lambda: datetime(2024, 5, 14, 18, 32, tzinfo=_MADRID))
    operador_id = Use(lambda: "OP-042")


# ── E-02 ────────────────────────────────────────────────────────────────


def _bool_wc(value: bool, conf: float = 0.85) -> BoolWithConfidence:
    return BoolWithConfidence(value=value, confidence=conf)


def _build_features(**overrides: Any) -> IncidentFeatures:
    base: dict[str, Any] = {
        "incident_id": "INC-2024-000001",
        "riesgo_vital": _bool_wc(True, 0.90),
        "numero_victimas_estimado": IntWithConfidence(value=2, confidence=0.80),
        "gravedad_lesiones": GravedadLesiones.GRAVE,
        "gravedad_lesiones_confidence": 0.82,
        "tipo_incidente_normalizado": "ACCIDENTE_TRAFICO",
        "poblacion_vulnerable": _bool_wc(False, 0.70),
        "numero_llamadas": 3,
        "emplazamiento_critico": _bool_wc(False, 0.65),
        "riesgo_propagacion": _bool_wc(False, 0.75),
        "multirriesgo": _bool_wc(False, 0.70),
        "avisos_simultaneos_zona": 0,
        "accesibilidad_recursos": "ALTA",
        "signal_fallecido": _bool_wc(False, 0.95),
        "signal_herido_grave": _bool_wc(True, 0.92),
        "signal_atrapado": _bool_wc(True, 0.88),
        "signal_intoxicacion": _bool_wc(False, 0.95),
        "signal_varias_llamadas": _bool_wc(True, 0.90),
        "signal_incendio": _bool_wc(False, 0.95),
        "signal_accidente_trafico": _bool_wc(True, 0.97),
        "signal_rescate": _bool_wc(True, 0.85),
        "signal_meteo_inundacion": _bool_wc(False, 0.95),
        "riesgo_vital_textual": _bool_wc(True, 0.90),
        "model_version_capa1": "0.1.0",
        "inference_timestamp": datetime(2024, 5, 14, 18, 32, 15, tzinfo=_MADRID),
        "inference_latency_ms": 320.0,
    }
    base.update(overrides)
    return IncidentFeatures(**base)


class IncidentFeaturesFactory:
    """Wrapper no-polyfactory: el modelo tiene demasiados campos con invariantes."""

    @staticmethod
    def build(**overrides: Any) -> IncidentFeatures:
        return _build_features(**overrides)


# ── E-03 ────────────────────────────────────────────────────────────────


def _build_recommendation(
    *,
    priority: Priority = Priority.P1,
    probs: dict[Priority, float] | None = None,
    rules: list[ActivatedRule] | None = None,
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH,
) -> PriorityRecommendation:
    if probs is None:
        probs = {Priority.P1: 0.85, Priority.P2: 0.10, Priority.P3: 0.04, Priority.P4: 0.01}
    if rules is None:
        rules = [
            ActivatedRule(
                rule_id="R-EXPERT-007",
                human_text="Atrapado con herido grave ⇒ P1",
                weight=0.45,
                normative_anchors=[NormaID.LEY_17_2015, NormaID.PLANCAL_DEC_4_2019],
            )
        ]
    return PriorityRecommendation(
        incident_id="INC-2024-000001",
        priority_recommended=priority,
        probabilities=probs,
        activated_rules=rules,
        confidence_level=confidence,
        model_used=ModelUsed.RULEFIT,
        model_version_capa2="0.1.0",
        requires_human_attention=False,
    )


class PriorityRecommendationFactory:
    @staticmethod
    def build(**overrides: Any) -> PriorityRecommendation:
        return _build_recommendation(**overrides)


# ── E-04 ────────────────────────────────────────────────────────────────


def _build_operator_recommendation(
    *,
    priority: Priority = Priority.P1,
    tools: list[str] | None = None,
    citations: list[LegalCitation] | None = None,
) -> OperatorRecommendation:
    if tools is None:
        tools = ["search_normative", "cite_legal_basis"]
    if citations is None:
        citations = [
            LegalCitation(
                norma_id=NormaID.LEY_17_2015,
                articulo_o_seccion="Art. 1",
                texto_relevante="Protección de personas y bienes ante emergencias graves.",
            )
        ]
    return OperatorRecommendation(
        incident_id="INC-2024-000001",
        priority_recommended=priority,
        explanation_text=(
            "Se recomienda P1 por presencia simultánea de atrapamiento y herido "
            "grave, factores que la regla R-EXPERT-007 vincula a una respuesta inmediata."
        ),
        legal_citations=citations,
        actuation_hints=["Movilizar SAMU y bomberos", "Cortar tráfico"],
        activated_rules_summary=["Atrapado con herido grave ⇒ P1"],
        confidence_disclaimer=None,
        model_version_capa3="0.1.0",
        llm_metadata=LLMMetadata(
            llm_model="qwen2.5-7b-instruct-q4_k_m",
            temperature=0.0,
            tools_invoked=tools,
            tokens_input=512,
            tokens_output=180,
        ),
    )


class OperatorRecommendationFactory:
    @staticmethod
    def build(**overrides: Any) -> OperatorRecommendation:
        return _build_operator_recommendation(**overrides)


# ── E-05 ────────────────────────────────────────────────────────────────


class OperatorDecisionFactory(ModelFactory[OperatorDecision]):
    __model__ = OperatorDecision

    incident_id = Use(lambda: "INC-2024-000001")
    priority_recommended_by_system = Use(lambda: Priority.P1)
    priority_assigned_by_operator = Use(lambda: Priority.P1)
    motivo_divergencia = Use(lambda: None)
    operador_id = Use(lambda: "OP-042")
    timestamp = Use(lambda: datetime(2024, 5, 14, 18, 33, tzinfo=_MADRID))


# ── E-06 ────────────────────────────────────────────────────────────────


class OperationalRuleFactory(ModelFactory[OperationalRule]):
    __model__ = OperationalRule

    rule_id = Use(lambda: "R-EXPERT-007")
    source = Use(lambda: VariableSource.EXPERT_BASELINE)
    condition_expression = Use(
        lambda: "signal_atrapado.value AND signal_herido_grave.value"
    )
    human_text = Use(lambda: "Atrapado con herido grave ⇒ P1")
    target_priority = Use(lambda: Priority.P1)
    weight = Use(lambda: 0.45)
    normative_anchors = Use(lambda: [NormaID.LEY_17_2015, NormaID.PLANCAL_DEC_4_2019])
    usage_count = Use(lambda: 0)
    precision_observed = Use(lambda: None)
    recall_observed = Use(lambda: None)
    created_at = Use(lambda: datetime(2024, 1, 1, tzinfo=_MADRID))
    updated_at = Use(lambda: datetime(2024, 5, 14, tzinfo=_MADRID))


# ── E-07 ────────────────────────────────────────────────────────────────


class WeakLabelFactory:
    @staticmethod
    def build(**overrides: Any) -> WeakLabel:
        base: dict[str, Any] = {
            "incident_id": "INC-2024-000001",
            "annotator_votes": {
                "llm_annotator": Priority.P1,
                "ner_annotator": Priority.P1,
                "cluster_annotator": Priority.P2,
                "heuristic_annotator": Priority.P1,
            },
            "final_label": Priority.P1,
            "label_model_confidence": 0.78,
            "agreement_score": 0.72,
            "was_used_in_training": True,
        }
        base.update(overrides)
        return WeakLabel(**base)


# ── E-08 ────────────────────────────────────────────────────────────────


def _build_inference_log(**overrides: Any) -> InferenceLog:
    features = _build_features()
    recommendation = _build_recommendation()
    op_rec = _build_operator_recommendation()
    base: dict[str, Any] = {
        "log_id": "01HXY9ABCDEFGHJKMNPQRSTVWX",
        "incident_id": "INC-2024-000001",
        "input_hash": compute_input_hash("INC-2024-000001", "Accidente con varios heridos"),
        "capa1_output": features,
        "capa2_output": recommendation,
        "capa3_output": op_rec,
        "operator_decision": None,
        "latencias_ms": {"capa1": 320.0, "capa2": 45.0, "capa3": 1850.0, "total": 2215.0},
        "model_versions": {"capa1": "0.1.0", "capa2": "0.1.0", "capa3": "0.1.0"},
        "tools_invoked": ["search_normative", "cite_legal_basis"],
        "timestamp_start": datetime(2024, 5, 14, 18, 32, 15, tzinfo=_MADRID),
        "timestamp_end": datetime(2024, 5, 14, 18, 32, 17, tzinfo=_MADRID),
    }
    base.update(overrides)
    return InferenceLog(**base)


class InferenceLogFactory:
    @staticmethod
    def build(**overrides: Any) -> InferenceLog:
        return _build_inference_log(**overrides)
