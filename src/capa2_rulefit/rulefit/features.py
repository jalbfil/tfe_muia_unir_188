"""Feature engineering comun para RuleFit Capa 2."""

from __future__ import annotations

from typing import Any

SIGNAL_FEATURES: tuple[str, ...] = (
    "signal_fallecido",
    "signal_herido_grave",
    "signal_atrapado",
    "signal_intoxicacion",
    "signal_varias_llamadas",
    "signal_incendio",
    "signal_accidente_trafico",
    "signal_rescate",
    "signal_meteo_inundacion",
    "riesgo_vital_textual",
)

CATEGORY_FEATURES: tuple[str, ...] = (
    "cat_trafico",
    "cat_incendio",
    "cat_rescate",
    "cat_sanitario",
    "cat_meteorologico",
    "cat_seguridad",
    "cat_otros",
)

FEATURE_NAMES: tuple[str, ...] = SIGNAL_FEATURES + CATEGORY_FEATURES


def _truthy(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return 1.0 if float(value) > 0 else 0.0
    return 1.0 if str(value or "").strip().lower() == "true" else 0.0


def _category_text(row: dict[str, Any]) -> str:
    return " ".join(
        str(row.get(key, "") or "")
        for key in ("categoria_operativa_preliminar", "tipo_incidente_normalizado")
    ).lower()


def row_to_feature_dict(row: dict[str, Any]) -> dict[str, float]:
    values = {feature: _truthy(row.get(feature)) for feature in SIGNAL_FEATURES}
    category = _category_text(row)
    values.update(
        {
            "cat_trafico": 1.0 if "trafico" in category or "tráfico" in category else 0.0,
            "cat_incendio": 1.0 if "incendio" in category else 0.0,
            "cat_rescate": 1.0 if "rescate" in category else 0.0,
            "cat_sanitario": 1.0 if "sanitario" in category else 0.0,
            "cat_meteorologico": 1.0 if "meteor" in category else 0.0,
            "cat_seguridad": 1.0 if "seguridad" in category else 0.0,
            "cat_otros": 1.0 if not category or "otros" in category else 0.0,
        }
    )
    return values


def row_to_vector(row: dict[str, Any], feature_names: list[str] | tuple[str, ...]) -> list[float]:
    values = row_to_feature_dict(row)
    return [float(values.get(feature, 0.0)) for feature in feature_names]


def incident_features_to_row(features: Any) -> dict[str, Any]:
    return {
        "categoria_operativa_preliminar": getattr(features.tipo_incidente_normalizado, "value", ""),
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
