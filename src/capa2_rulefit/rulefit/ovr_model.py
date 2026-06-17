"""Modelo RuleFit one-vs-rest serializable para prioridad P1-P4."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .features import row_to_vector


@dataclass
class RuleFitOvRModel:
    class_labels: list[str]
    feature_names: list[str]
    estimators: dict[str, Any]
    calibrators: dict[str, Any]
    rules_by_class: dict[str, list[dict[str, Any]]]
    model_version: str = "0.1.0"

    def predict_proba_from_row(self, row: dict[str, Any]) -> dict[str, float]:
        x = np.asarray([row_to_vector(row, self.feature_names)], dtype=float)
        raw_scores: list[float] = []
        for label in self.class_labels:
            estimator = self.estimators[label]
            proba = estimator.predict_proba(x)[:, 1]
            calibrator = self.calibrators[label]
            raw_scores.append(float(calibrator.transform(proba)[0]))
        scores = np.asarray(raw_scores, dtype=float)
        scores = np.clip(scores, 1e-9, 1.0)
        scores = scores / scores.sum()
        rounded = {label: round(float(score), 6) for label, score in zip(self.class_labels, scores)}
        winner = max(rounded, key=rounded.get)
        rounded[winner] = round(rounded[winner] + (1.0 - sum(rounded.values())), 6)
        return rounded

    def top_rules_for_label(self, label: str, limit: int = 30) -> list[dict[str, Any]]:
        rules = self.rules_by_class.get(label, [])
        return sorted(rules, key=lambda rule: abs(float(rule["coef"])), reverse=True)[:limit]
