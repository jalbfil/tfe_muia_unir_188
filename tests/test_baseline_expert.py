from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from capa2_rulefit.baseline_expert import EXPERT_RULES, apply_expert_rules, predict_expert


def test_t053_expert_baseline_has_minimum_rule_set_and_anchors() -> None:
    assert len(EXPERT_RULES) >= 15
    assert all(rule.normative_anchors for rule in EXPERT_RULES)
    assert all(rule.rule_id.startswith("EXP-") for rule in EXPERT_RULES)


def test_t053_expert_baseline_predicts_p1_for_fatal_incident() -> None:
    row = {
        "signal_fallecido": "True",
        "signal_herido_grave": "True",
        "signal_atrapado": "False",
        "signal_intoxicacion": "False",
        "signal_incendio": "False",
        "signal_accidente_trafico": "True",
        "signal_rescate": "False",
        "signal_meteo_inundacion": "False",
        "signal_varias_llamadas": "True",
        "riesgo_vital_textual": "True",
        "texto_operativo_norm": "fallece motorista tras accidente",
    }

    prediction = predict_expert(row)

    assert prediction["priority_recommended"] == "P1"
    assert apply_expert_rules(row)
    assert abs(sum(prediction["probabilities"].values()) - 1.0) <= 1e-6
