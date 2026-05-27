"""Baseline experto trazable para Capa 2."""

from .expert_rules import EXPERT_RULES, apply_expert_rules, export_rules_metadata, predict_expert

__all__ = [
    "EXPERT_RULES",
    "apply_expert_rules",
    "export_rules_metadata",
    "predict_expert",
]
