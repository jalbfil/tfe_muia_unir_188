"""Wrapper de inferencia principal de la Capa 1 NLP determinista."""

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
    
    En v0.1.0 la Capa 1 es un extractor determinista de señales y variables
    operativas. No entrena ni ejecuta modelos transformer; esa línea queda reservada
    como trabajo futuro si se dispone de un checkpoint congelado y evaluado.
    """

    def __init__(self, model_path: str | None = None) -> None:
        _ = model_path  # Reservado para compatibilidad de firma; no se usa en v0.1.0.
        self.signal_extractor = SignalExtractor()
        self.model_version = "0.1.0"
        self.model = None
        self.tokenizer = None
        self.device = None
        self.dl_engine_active = False

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
        if not merged_text:
            warnings.append("Texto de incidente completamente vacío o nulo")

        # 1. Extracción determinista/semántica de señales avanzadas
        signals = self.signal_extractor.extract(merged_text)
        
        has_fatal = signals["signal_fallecido"].value
        has_injured = signals["signal_herido_grave"].value
        has_trapped = signals["signal_atrapado"].value
        has_incendio = signals["signal_incendio"].value
        has_accident = signals["signal_accidente_trafico"].value
        has_toxic = signals["signal_intoxicacion"].value

        # Variables operativas semánticas avanzadas
        poblacion_vulnerable = self.signal_extractor.extract_vulnerable_population(merged_text)
        emplazamiento_critico = self.signal_extractor.extract_critical_location(merged_text)
        
        acc_val, acc_conf = self.signal_extractor.extract_accessibility(merged_text)
        accesibilidad_recursos = acc_val

        numero_victimas_estimado = self.signal_extractor.extract_estimated_victims(
            merged_text, 
            has_fatal_or_injured=(has_fatal or has_injured)
        )

        riesgo_propagacion = self.signal_extractor.extract_propagation_risk(merged_text, has_incendio)

        # Multirriesgo: Dos o más señales principales activas
        active_signals_count = sum([has_accident, has_incendio, has_trapped, has_toxic])
        multirriesgo_val = active_signals_count >= 2
        multirriesgo = BoolWithConfidence(
            value=multirriesgo_val,
            confidence=0.90 if multirriesgo_val else 0.50,
        )

        # 2. Probabilidades auxiliares deterministas basadas en señales léxicas.
        p_vital = 0.96 if (signals["riesgo_vital_textual"].value or has_fatal or has_injured) else 0.08
        p_fallecido = 0.94 if has_fatal else 0.04
        p_herido = 0.92 if has_injured else 0.06
        p_atrapado = 0.95 if has_trapped else 0.03
        p_incendio = 0.93 if has_incendio else 0.05

        # 3. Fusión determinista: reglas de alta precisión y probabilidades auxiliares.
        # La regla léxica decide el valor; las probabilidades solo expresan confianza.
        
        def fuse_signal(regex_val: bool, neural_prob: float) -> BoolWithConfidence:
            if regex_val:
                # La regla determinista de alta fidelidad es prioritaria
                confidence = max(0.95, neural_prob)
                return BoolWithConfidence(value=True, confidence=confidence)
            else:
                confidence = max(0.90, 1.0 - neural_prob)
                return BoolWithConfidence(value=False, confidence=confidence)

        fused_signals = {
            "signal_fallecido": fuse_signal(has_fatal, p_fallecido),
            "signal_herido_grave": fuse_signal(has_injured, p_herido),
            "signal_atrapado": fuse_signal(has_trapped, p_atrapado),
            "signal_intoxicacion": signals["signal_intoxicacion"],  # Se mantiene directo
            "signal_varias_llamadas": signals["signal_varias_llamadas"],
            "signal_incendio": fuse_signal(has_incendio, p_incendio),
            "signal_accidente_trafico": signals["signal_accidente_trafico"],
            "signal_rescate": signals["signal_rescate"],
            "signal_meteo_inundacion": signals["signal_meteo_inundacion"],
            "riesgo_vital_textual": fuse_signal(signals["riesgo_vital_textual"].value, p_vital),
        }

        # V01: riesgo_vital (Fusión global de riesgo vital)
        riesgo_vital_val = (
            fused_signals["riesgo_vital_textual"].value
            or fused_signals["signal_fallecido"].value
            or fused_signals["signal_herido_grave"].value
        )
        # La confianza se deriva del promedio ponderado o del valor máximo neural de las señales de riesgo
        riesgo_vital_conf = max(p_vital, p_fallecido, p_herido) if riesgo_vital_val else (1.0 - p_vital)
        riesgo_vital = BoolWithConfidence(
            value=riesgo_vital_val,
            confidence=max(0.95 if riesgo_vital_val else 0.90, riesgo_vital_conf),
        )

        # V03: gravedad_lesiones
        if fused_signals["signal_fallecido"].value:
            gravedad_lesiones = GravedadLesiones.CRITICA
            gravedad_lesiones_confidence = fused_signals["signal_fallecido"].confidence
        elif fused_signals["signal_herido_grave"].value:
            gravedad_lesiones = GravedadLesiones.GRAVE
            gravedad_lesiones_confidence = fused_signals["signal_herido_grave"].confidence
        elif fused_signals["signal_atrapado"].value:
            gravedad_lesiones = GravedadLesiones.MODERADA
            gravedad_lesiones_confidence = fused_signals["signal_atrapado"].confidence
        elif fused_signals["signal_intoxicacion"].value:
            gravedad_lesiones = GravedadLesiones.LEVE
            gravedad_lesiones_confidence = fused_signals["signal_intoxicacion"].confidence
        elif fused_signals["signal_accidente_trafico"].value or fused_signals["signal_incendio"].value:
            gravedad_lesiones = GravedadLesiones.LEVE
            gravedad_lesiones_confidence = 0.70
        else:
            gravedad_lesiones = GravedadLesiones.DESCONOCIDA
            gravedad_lesiones_confidence = 0.50

        # V04: tipo_incidente_normalizado
        # Mapeo inteligente del tipo de incidente normalizado
        if fused_signals["signal_accidente_trafico"].value:
            tipo_incidente_normalizado = CategoriaPreliminar.ACCIDENTE_TRAFICO
        elif fused_signals["signal_incendio"].value:
            # Si el input original indicaba forestal, respetamos forestal, si no, urbano
            if incident.categoria_preliminar == CategoriaPreliminar.INCENDIO_FORESTAL:
                tipo_incidente_normalizado = CategoriaPreliminar.INCENDIO_FORESTAL
            else:
                tipo_incidente_normalizado = CategoriaPreliminar.INCENDIO_URBANO
        elif fused_signals["signal_rescate"].value:
            tipo_incidente_normalizado = CategoriaPreliminar.RESCATE
        elif fused_signals["signal_meteo_inundacion"].value:
            tipo_incidente_normalizado = CategoriaPreliminar.METEOROLOGIA
        elif fused_signals["signal_intoxicacion"].value:
            tipo_incidente_normalizado = CategoriaPreliminar.QUIMICO_NRBQ
        else:
            tipo_incidente_normalizado = incident.categoria_preliminar or CategoriaPreliminar.OTROS

        # V06: numero_llamadas
        numero_llamadas = 1
        if fused_signals["signal_varias_llamadas"].value:
            numero_llamadas = 2

        # V14: avisos_simultaneos_zona (Simulado contextualmente si hay aviso repetido)
        avisos_simultaneos_zona = 1 if fused_signals["signal_varias_llamadas"].value else 0

        # Calcular latencia de inferencia exacta
        end_time = time.perf_counter_ns()
        latency_ms = (end_time - start_time) / 1_000_000.0

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
            # Señales fusionadas
            **fused_signals,
            # Metadatos
            model_version_capa1=self.model_version,
            inference_timestamp=datetime.now(timezone.utc),
            inference_latency_ms=latency_ms,
            extractor_warnings=warnings,
        )
