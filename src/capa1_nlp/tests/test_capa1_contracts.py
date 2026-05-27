"""T041: Test de cumplimiento de contrato de Capa 1 NLP (IncidentFeatures)."""

from __future__ import annotations

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from contracts import CategoriaPreliminar, ProvinciaCyL, IncidentInput, IncidentFeatures
from capa1_nlp.inference.feature_extractor import FeatureExtractor


def test_feature_extractor_returns_valid_incident_features() -> None:
    """Verifica que el extractor produzca un IncidentFeatures estructurado y válido."""
    incident = IncidentInput(
        incident_id="01AN4V07BY79KA1307SR9X4MV3",
        texto_titulo="Accidente grave con atrapados",
        texto_descripcion="Colision frontal entre dos turismos en N-122 km 150. Hay un varon inconsciente atrapado en el coche.",
        categoria_preliminar=CategoriaPreliminar.ACCIDENTE_TRAFICO,
        latitud=41.65,
        longitud=-2.46,
        localidad="Soria",
        provincia=ProvinciaCyL.SORIA,
        fecha_incidente=datetime.now(timezone.utc),
        operador_id="OP_1234",
    )

    extractor = FeatureExtractor()
    features = extractor.extract_features(incident)

    # Validar tipo de salida
    assert isinstance(features, IncidentFeatures)
    assert features.incident_id == incident.incident_id

    # Validar que los valores de señales extraídos sean consistentes
    assert features.signal_accidente_trafico.value is True
    assert features.signal_atrapado.value is True
    assert features.signal_herido_grave.value is True
    assert features.riesgo_vital.value is True

    # Validar que las confianzas estén en el rango [0.0, 1.0]
    assert 0.0 <= features.signal_accidente_trafico.confidence <= 1.0
    assert 0.0 <= features.riesgo_vital.confidence <= 1.0

    # Validar metadatos
    assert features.model_version_capa1 == "0.1.0"
    assert features.inference_latency_ms >= 0.0
    assert isinstance(features.inference_timestamp, datetime)


def test_feature_extractor_handles_no_signals() -> None:
    """Verifica el comportamiento cuando no hay señales identificadas."""
    incident = IncidentInput(
        incident_id="01AN4V07BY79KA1307SR9X4MV4",
        texto_titulo="Consulta general",
        texto_descripcion="Llamada informativa preguntando por el estado de las carreteras sin afectaciones.",
        categoria_preliminar=CategoriaPreliminar.OTROS,
        fecha_incidente=datetime.now(timezone.utc),
        operador_id="OP_5678",
    )

    extractor = FeatureExtractor()
    features = extractor.extract_features(incident)

    assert isinstance(features, IncidentFeatures)
    # Ninguna señal crítica debería activarse
    assert features.signal_fallecido.value is False
    assert features.signal_atrapado.value is False
    assert features.signal_herido_grave.value is False
    assert features.signal_incendio.value is False
    assert features.riesgo_vital.value is False
