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

__all__ = [
    "__version__",
    # enums
    "Priority",
    "ConfidenceLevel",
    "ModelUsed",
    "VariableSource",
    "ProvinciaCyL",
    "CategoriaPreliminar",
    "GravedadLesiones",
    "AvisoAEMET",
    "Accesibilidad",
    "NormaID",
    # primitives
    "BoolWithConfidence",
    "IntWithConfidence",
    "Confidence",
    # entities
    "IncidentInput",
    "IncidentFeatures",
    "PriorityRecommendation",
    "ActivatedRule",
    "OperatorRecommendation",
    "LegalCitation",
    "LLMMetadata",
    "MCP_TOOLS_V0_1",
    "assert_production_temperature",
    "OperatorDecision",
    "OperationalRule",
    "WeakLabel",
    "InferenceLog",
    "compute_input_hash",
    # errors
    "ContractsError",
    "LeakageFieldRejectedError",
    "LowConfidenceWarning",
    "SLABreachWarning",
    "DegradedModeActivated",
    "ContractVersionMismatchError",
    # leakage
    "PROHIBITED_FEATURE_COLUMNS",
]
