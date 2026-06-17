"""Adaptadores para el modelo RuleFit entrenado.

La implementacion de entrenamiento entra en T054. Este paquete fija la frontera
modular para no mezclar inferencia, baseline y persistencia de modelo.
"""

from .features import FEATURE_NAMES, incident_features_to_row, row_to_feature_dict, row_to_vector
from .lite_model import RuleSetClassifierModel
from .ovr_model import RuleFitOvRModel

__all__ = [
    "FEATURE_NAMES",
    "RuleSetClassifierModel",
    "RuleFitOvRModel",
    "incident_features_to_row",
    "row_to_feature_dict",
    "row_to_vector",
]
