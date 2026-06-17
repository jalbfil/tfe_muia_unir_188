"""T041: Test de cumplimiento de contrato de Capa 1 NLP (IncidentFeatures) y extractores semánticos."""

from __future__ import annotations

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from contracts import (
    Accesibilidad,
    CategoriaPreliminar,
    ProvinciaCyL,
    IncidentInput,
    IncidentFeatures,
)
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


def test_feature_extractor_multilingual_english() -> None:
    """Valida la resiliencia multilingüe (inglés) para turistas y extranjeros."""
    incident = IncidentInput(
        incident_id="01AN4V07BY79KA1307SR9X4MV5",
        texto_titulo="Emergency: car crash with wildfire threat",
        texto_descripcion="A severe car collision on highway AP-1. The driver is unconscious and trapped inside the burning vehicle.",
        categoria_preliminar=CategoriaPreliminar.ACCIDENTE_TRAFICO,
        fecha_incidente=datetime.now(timezone.utc),
        operador_id="OP_9999",
    )

    extractor = FeatureExtractor()
    features = extractor.extract_features(incident)

    assert features.signal_accidente_trafico.value is True
    assert features.signal_incendio.value is True
    assert features.signal_atrapado.value is True
    assert features.signal_herido_grave.value is True
    assert features.riesgo_vital.value is True


def test_feature_extractor_spelling_resilience() -> None:
    """Valida la resiliencia ortográfica (soporte a faltas de ortografía o falta de tildes)."""
    incident = IncidentInput(
        incident_id="01AN4V07BY79KA1307SR9X4MV6",
        texto_titulo="colision con camion en la calzada",
        texto_descripcion="fuego activo, hay peligro de explosion y fuga de gas. posible intoxicacion de personas.",
        categoria_preliminar=CategoriaPreliminar.INCENDIO_URBANO,
        fecha_incidente=datetime.now(timezone.utc),
        operador_id="OP_9999",
    )

    extractor = FeatureExtractor()
    features = extractor.extract_features(incident)

    assert features.signal_accidente_trafico.value is True
    assert features.signal_incendio.value is True
    assert features.signal_intoxicacion.value is True
    assert features.riesgo_propagacion.value is True


def test_feature_extractor_vulnerable_and_critical_spots() -> None:
    """Valida la detección de población vulnerable (niños, ancianos) y emplazamientos críticos."""
    extractor = FeatureExtractor()

    # Caso 1: Colegio Infantil (Vulnerable + Crítico)
    incident_school = IncidentInput(
        incident_id="01AN4V07BY79KA1307SR9X4MV7",
        texto_titulo="Fuego en colegio",
        texto_descripcion="Incendio estructural en un parque infantil de la escuela primaria. Hay varios ninos atrapados en el patio.",
        categoria_preliminar=CategoriaPreliminar.INCENDIO_URBANO,
        fecha_incidente=datetime.now(timezone.utc),
        operador_id="OP_1111",
    )
    features_school = extractor.extract_features(incident_school)
    assert features_school.poblacion_vulnerable.value is True
    assert features_school.emplazamiento_critico.value is True

    # Caso 2: Residencia de Ancianos (Vulnerable + Crítico)
    incident_elderly = IncidentInput(
        incident_id="01AN4V07BY79KA1307SR9X4MV8",
        texto_titulo="Urgencia geriátrico",
        texto_descripcion="Un anciano se ha desplomado en la residencia de mayores con sintomas de infarto de miocardio.",
        categoria_preliminar=CategoriaPreliminar.SANITARIO,
        fecha_incidente=datetime.now(timezone.utc),
        operador_id="OP_1111",
    )
    features_elderly = extractor.extract_features(incident_elderly)
    assert features_elderly.poblacion_vulnerable.value is True
    assert features_elderly.emplazamiento_critico.value is True


def test_feature_extractor_accessibility_mapping() -> None:
    """Valida la inferencia de barreras de accesibilidad meteorológicas y geográficas."""
    extractor = FeatureExtractor()

    # Caso 1: Nevado e inaccesible (Accesibilidad BAJA)
    incident_snow = IncidentInput(
        incident_id="01AN4V07BY79KA1307SR9X4MV9",
        texto_titulo="Accidente montaña",
        texto_descripcion="Un senderista herido en un barranco del pico de montaña. Hay una ventisca de nieve densa y mucho hielo.",
        categoria_preliminar=CategoriaPreliminar.RESCATE,
        fecha_incidente=datetime.now(timezone.utc),
        operador_id="OP_2222",
    )
    features_snow = extractor.extract_features(incident_snow)
    assert features_snow.accesibilidad_recursos == Accesibilidad.BAJA

    # Caso 2: Carretera rural con niebla (Accesibilidad MEDIA)
    incident_fog = IncidentInput(
        incident_id="01AN4V07BY79KA1307SR9X4MVA",
        texto_titulo="Incidencia vial",
        texto_descripcion="Carretera secundaria en zona rural con niebla espesa y lluvia fuerte.",
        categoria_preliminar=CategoriaPreliminar.INCIDENCIA_VIA,
        fecha_incidente=datetime.now(timezone.utc),
        operador_id="OP_2222",
    )
    features_fog = extractor.extract_features(incident_fog)
    assert features_fog.accesibilidad_recursos == Accesibilidad.MEDIA


def test_feature_extractor_victim_counts() -> None:
    """Valida la estimación numérica inteligente del número de víctimas en el texto."""
    extractor = FeatureExtractor()

    # Caso 1: Número escrito "tres"
    incident_three = IncidentInput(
        incident_id="01AN4V07BY79KA1307SR9X4MVB",
        texto_titulo="Accidente AP-62",
        texto_descripcion="Choque frontal severo entre dos coches. Se confirman tres personas heridas graves.",
        categoria_preliminar=CategoriaPreliminar.ACCIDENTE_TRAFICO,
        fecha_incidente=datetime.now(timezone.utc),
        operador_id="OP_3333",
    )
    features_three = extractor.extract_features(incident_three)
    assert features_three.numero_victimas_estimado.value == 3

    # Caso 2: Dígito "4"
    incident_four = IncidentInput(
        incident_id="01AN4V07BY79KA1307SR9X4MVC",
        texto_titulo="Fuga de gas bar",
        texto_descripcion="Intoxicacion en restaurante céntrico con 4 personas afectadas por inhalacion de humo.",
        categoria_preliminar=CategoriaPreliminar.QUIMICO_NRBQ,
        fecha_incidente=datetime.now(timezone.utc),
        operador_id="OP_3333",
    )
    features_four = extractor.extract_features(incident_four)
    assert features_four.numero_victimas_estimado.value == 4

    # Caso 3: Cuantificador vago "varias"
    incident_several = IncidentInput(
        incident_id="01AN4V07BY79KA1307SR9X4MVD",
        texto_titulo="Incendio forestal Burgos",
        texto_descripcion="Hay varias personas atrapadas en el monte debido al fuego.",
        categoria_preliminar=CategoriaPreliminar.INCENDIO_FORESTAL,
        fecha_incidente=datetime.now(timezone.utc),
        operador_id="OP_3333",
    )
    features_several = extractor.extract_features(incident_several)
    assert features_several.numero_victimas_estimado.value == 3
