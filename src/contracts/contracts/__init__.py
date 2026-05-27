"""Capa de contratos vinculante entre Capa 1 NLP, Capa 2 RuleFit y Capa 3 LLM/MCP.

Cualquier intercambio entre capas DEBE pasar por estos modelos.
"""

from __future__ import annotations

from ._version import __version__
from .enums import (
    Accesibilidad,
    AvisoAEMET,
    CategoriaPreliminar,
    ConfidenceLevel,
    GravedadLesiones,
    ModelUsed,
    NormaID,
    Priority,
    ProvinciaCyL,
    VariableSource,
)
from .errors import (
    ContractsError,
    ContractVersionMismatchError,
    DegradedModeActivated,
    LeakageFieldRejectedError,
    LowConfidenceWarning,
    SLABreachWarning,
)
from .incident_features import IncidentFeatures
from .incident_input import IncidentInput
from .inference_log import InferenceLog, compute_input_hash
from .leakage_columns import PROHIBITED_FEATURE_COLUMNS
from .operator_decision import OperatorDecision
from .operator_recommendation import (
    MCP_TOOLS_V0_1,
    LegalCitation,
    LLMMetadata,
    OperatorRecommendation,
    assert_production_temperature,
)
from .primitives import BoolWithConfidence, Confidence, IntWithConfidence
from .priority_recommendation import ActivatedRule, PriorityRecommendation
from .rule import OperationalRule
from .weak_label import WeakLabel

__all__ = [  # noqa: RUF022 — orden semántico (enums → primitivos → entidades → errores)
    "__version__",
    # enums
    "Accesibilidad",
    "AvisoAEMET",
    "CategoriaPreliminar",
    "ConfidenceLevel",
    "GravedadLesiones",
    "ModelUsed",
    "NormaID",
    "Priority",
    "ProvinciaCyL",
    "VariableSource",
    # primitives
    "BoolWithConfidence",
    "Confidence",
    "IntWithConfidence",
    # entities
    "ActivatedRule",
    "IncidentFeatures",
    "IncidentInput",
    "InferenceLog",
    "LLMMetadata",
    "LegalCitation",
    "MCP_TOOLS_V0_1",
    "OperatorDecision",
    "OperatorRecommendation",
    "OperationalRule",
    "PriorityRecommendation",
    "WeakLabel",
    "assert_production_temperature",
    "compute_input_hash",
    # errors
    "ContractVersionMismatchError",
    "ContractsError",
    "DegradedModeActivated",
    "LeakageFieldRejectedError",
    "LowConfidenceWarning",
    "SLABreachWarning",
    # leakage
    "PROHIBITED_FEATURE_COLUMNS",
]
