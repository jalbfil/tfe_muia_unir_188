"""RuleFit-lite: reglas de arbol + modelo lineal calibrado."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .features import row_to_vector


@dataclass
class RuleSetClassifierModel:
    class_labels: list[str]
    feature_names: list[str]
    trees: dict[str, Any]
    leaf_values: dict[str, list[int]]
    classifier: Any
    calibrators: dict[str, Any]
    rules_by_class: dict[str, list[dict[str, Any]]]
    model_version: str = "0.1.0"

    def _ensure_classifier_compatibility(self) -> None:
        """Patch known attribute gaps when loading persisted sklearn artifacts."""

        # sklearn>=1.7 expects this attribute in LogisticRegression; some
        # persisted artifacts created elsewhere may not carry it.
        if not hasattr(self.classifier, "multi_class"):
            setattr(self.classifier, "multi_class", "auto")

    def transform(self, x: np.ndarray) -> np.ndarray:
        parts = [x]
        for label in self.class_labels:
            leaf_ids = self.trees[label].apply(x)
            leaves = self.leaf_values[label]
            parts.append(np.asarray([[1.0 if leaf_id == leaf else 0.0 for leaf in leaves] for leaf_id in leaf_ids]))
        return np.hstack(parts)

    def predict_proba_from_row(self, row: dict[str, Any]) -> dict[str, float]:
        x = np.asarray([row_to_vector(row, self.feature_names)], dtype=float)
        self._ensure_classifier_compatibility()
        raw = self.classifier.predict_proba(self.transform(x))[0]
        calibrated = []
        for idx, label in enumerate(self.class_labels):
            calibrator = self.calibrators.get(label)
            if calibrator is None:
                calibrated.append(float(raw[idx]))
            else:
                calibrated.append(float(calibrator.transform([raw[idx]])[0]))
        scores = np.clip(np.asarray(calibrated, dtype=float), 1e-9, 1.0)
        scores = scores / scores.sum()
        rounded = {label: round(float(score), 6) for label, score in zip(self.class_labels, scores)}
        winner = max(rounded, key=rounded.get)
        rounded[winner] = round(rounded[winner] + (1.0 - sum(rounded.values())), 6)
        return rounded

    def top_rules_for_label(self, label: str, limit: int = 30) -> list[dict[str, Any]]:
        rules = self.rules_by_class.get(label, [])
        return sorted(rules, key=lambda rule: abs(float(rule["coef"])), reverse=True)[:limit]
