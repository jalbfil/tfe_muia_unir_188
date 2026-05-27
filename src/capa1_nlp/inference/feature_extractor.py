"""Wrapper de inferencia principal de la Capa 1 NLP."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from contracts import (
    Accesibilidad,
    CategoriaPreliminar,
    GravedadLesiones,
    IncidentFeatures,
    IncidentInput,
    BoolWithConfidence,
    IntWithConfidence,
)
from capa1_nlp.extraction.signal_extractor import SignalExtractor


class FeatureExtractor:
    """Orquestador de inferencia de la Capa 1.
    
    Analiza IncidentInput, ejecuta la extracción léxica/regex y el modelo
    de aprendizaje profundo (cuando esté entrenado y disponible), y produce
    IncidentFeatures cumpliendo estrictamente el contrato Pydantic.
    """

    def __init__(self, model_path: str | None = None) -> None:
        self.signal_extractor = SignalExtractor()
        self.model_version = "0.1.0"
        self.model = None
        if model_path:
            # Reservado para cargar el transformer entrenado en PyTorch
            pass

    def extract_features(self, incident: IncidentInput) -> IncidentFeatures:
        """Analiza un incidente y extrae las variables operativas de la Capa 1.
        
        Args:
            incident: Objeto IncidentInput de entrada.
            
        Returns:
            Instancia validada de IncidentFeatures.
        """
        start_time = time.perf_counter_ns()
        warnings: list[str] = []

        # Combinar título y descripción
        merged_text = f"{incident.texto_titulo}\n{incident.texto_descripcion}".strip()

        # 1. Extracción determinista de señales léxicas
        signals = self.signal_extractor.extract(merged_text)

        # 2. Extracción de variables operativas (aquí se acoplaría el Transformer)
        # En esta versión v0.1.0 base, calculamos proxies consistentes con las señales léxicas:
        
        # V01: riesgo_vital
        riesgo_vital_val = (
            signals["riesgo_vital_textual"].value
            or signals["signal_fallecido"].value
            or signals["signal_herido_grave"].value
        )
        riesgo_vital = BoolWithConfidence(
            value=riesgo_vital_val,
            confidence=0.95 if riesgo_vital_val else 0.50,
        )

        # V02: numero_victimas_estimado
        if signals["signal_fallecido"].value or signals["signal_herido_grave"].value:
            num_victimas_val = 1
            num_victimas_conf = 0.80
        else:
            num_victimas_val = -1  # Desconocido
            num_victimas_conf = 0.50
            
        numero_victimas_estimado = IntWithConfidence(
            value=num_victimas_val,
            confidence=num_victimas_conf,
        )

        # V03: gravedad_lesiones
        if signals["signal_fallecido"].value:
            gravedad_lesiones = GravedadLesiones.CRITICA
            gravedad_lesiones_confidence = 0.95
        elif signals["signal_herido_grave"].value:
            gravedad_lesiones = GravedadLesiones.GRAVE
            gravedad_lesiones_confidence = 0.90
        elif signals["signal_atrapado"].value:
            gravedad_lesiones = GravedadLesiones.MODERADA
            gravedad_lesiones_confidence = 0.70
        else:
            gravedad_lesiones = GravedadLesiones.DESCONOCIDA
            gravedad_lesiones_confidence = 0.50

        # V04: tipo_incidente_normalizado
        tipo_incidente_normalizado = incident.categoria_preliminar or CategoriaPreliminar.ACCIDENTE_TRAFICO

        # V05: poblacion_vulnerable
        poblacion_vulnerable = BoolWithConfidence(
            value=False,
            confidence=0.50,
        )

        # V06: numero_llamadas
        numero_llamadas = 1
        if signals["signal_varias_llamadas"].value:
            numero_llamadas = 2

        # V07: emplazamiento_critico
        emplazamiento_critico = BoolWithConfidence(
            value=False,
            confidence=0.50,
        )

        # V12: riesgo_propagacion
        riesgo_propagacion = BoolWithConfidence(
            value=signals["signal_incendio"].value,
            confidence=0.90 if signals["signal_incendio"].value else 0.50,
        )

        # V13: multirriesgo
        # Si hay choque de tráfico más incendio, es un multirriesgo
        multirriesgo_val = signals["signal_accidente_trafico"].value and signals["signal_incendio"].value
        multirriesgo = BoolWithConfidence(
            value=multirriesgo_val,
            confidence=0.85 if multirriesgo_val else 0.50,
        )

        # V14: avisos_simultaneos_zona
        avisos_simultaneos_zona = 0

        # V15: accesibilidad_recursos
        accesibilidad_recursos = Accesibilidad.DESCONOCIDA

        # Calcular latencia de inferencia
        end_time = time.perf_counter_ns()
        latency_ms = (end_time - start_time) / 1_000_000.0

        if not merged_text.strip():
            warnings.append("Texto de incidente completamente vacío o nulo")

        return IncidentFeatures(
            incident_id=incident.incident_id,
            riesgo_vital=riesgo_vital,
            numero_victimas_estimado=numero_victimas_estimado,
            gravedad_lesiones=gravedad_lesiones,
            gravedad_lesiones_confidence=gravedad_lesiones_confidence,
            tipo_incidente_normalizado=tipo_incidente_normalizado,
            poblacion_vulnerable=poblacion_vulnerable,
            numero_llamadas=numero_llamadas,
            emplazamiento_critico=emplazamiento_critico,
            riesgo_propagacion=riesgo_propagacion,
            multirriesgo=multirriesgo,
            avisos_simultaneos_zona=avisos_simultaneos_zona,
            accesibilidad_recursos=accesibilidad_recursos,
            # Señales
            **signals,
            # Metadatos
            model_version_capa1=self.model_version,
            inference_timestamp=datetime.now(timezone.utc),
            inference_latency_ms=latency_ms,
            extractor_warnings=warnings,
        )
