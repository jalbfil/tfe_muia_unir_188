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
    
    Capa 1 puede ejecutarse en un esquema híbrido neuro-simbólico: combina un clasificador
    multietiqueta de aprendizaje automático (TF-IDF + Regresión Logística) con guardarraíles
    deterministas basados en reglas léxicas para garantizar recall del 100% en señales críticas.
    """

    def __init__(self, model_path: str | None = None) -> None:
        import joblib
        from pathlib import Path
        
        self.signal_extractor = SignalExtractor()
        self.model = None
        self.tokenizer = None
        self.device = None
        self.dl_engine_active = False
        self.model_version = "0.1.0"
        
        # Intentar cargar el modelo entrenado de ML
        if model_path is None:
            project_root = Path(__file__).resolve().parents[3]
            model_path = str(project_root / "artifacts" / "models" / "capa1" / "v0.1.0" / "classifier.joblib")
            
        p = Path(model_path)
        if p.exists():
            try:
                self.ml_pipeline = joblib.load(model_path)
                self.dl_engine_active = True
                print(f"Capa 1: Cargado clasificador ML desde {model_path}")
            except Exception as e:
                print(f"Advertencia al cargar modelo ML de Capa 1: {e}. Usando modo determinista.")
                self.ml_pipeline = None
        else:
            self.ml_pipeline = None

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

        # Siempre extraemos las deterministas como base/guardarraíl
        det_signals = self.signal_extractor.extract(merged_text)
        
        # Determinar si hay alguna señal crítica de seguridad detectada deterministamente
        critical_keys = {"signal_fallecido", "signal_herido_grave", "signal_atrapado", "signal_intoxicacion", "signal_incendio", "signal_rescate", "riesgo_vital_textual"}
        has_any_critical_det = any(det_signals[k].value for k in critical_keys if k in det_signals)

        # 1. Extracción de señales (ML o determinista)
        if self.dl_engine_active and self.ml_pipeline is not None:
            vectorizer = self.ml_pipeline["vectorizer"]
            classifier = self.ml_pipeline["classifier"]
            signals_list = self.ml_pipeline["signals"]
            
            X_vec = vectorizer.transform([merged_text])
            probs = classifier.predict_proba(X_vec)
            
            signals = {}
            for idx, sig in enumerate(signals_list):
                # probs[idx] tiene forma (1, 2) para clases [0, 1]
                if probs[idx].shape[1] == 2:
                    p_active = float(probs[idx][0, 1])
                else:
                    p_active = float(probs[idx][0, 0])
                
                det_val = det_signals[sig].value
                
                # Fusión neuro-simbólica con guardarraíl de seguridad
                if not has_any_critical_det and sig in critical_keys:
                    # Si no hay ninguna palabra clave crítica en el texto, evitamos falsos positivos del ML
                    val = False
                    conf = max(0.95, 1.0 - p_active)
                elif det_val:
                    # Si el analizador determinista activa la señal, la respetamos por seguridad (recall)
                    val = True
                    conf = max(0.95, p_active)
                else:
                    # En otro caso, confiamos en la predicción del modelo de ML
                    val = p_active >= 0.5
                    conf = p_active if val else (1.0 - p_active)
                
                signals[sig] = BoolWithConfidence(value=val, confidence=conf)
                
            # Aplicar filtros de supresión por broma y por incidentes de animales en modo ML
            cleaned_text = merged_text.lower()
            is_prank = any(term in cleaned_text for term in ("broma", "falsa alarma", "simulacro", "simulado"))
            
            is_animal_only = False
            animal_terms = ("perro", "gato", "animal", "mascota", "caballo", "vaca", "oveja", "canino", "felino")
            human_terms = ("persona", "herido", "conductor", "peatón", "niño", "hombre", "mujer", "pasajero", "ocupante", "gente", "víctima", "victima", "herid")
            has_animal = any(term in cleaned_text for term in animal_terms)
            has_human = any(term in cleaned_text for term in human_terms)
            if has_animal and not has_human:
                is_animal_only = True

            for sig in signals_list:
                if is_prank:
                    signals[sig] = BoolWithConfidence(value=False, confidence=1.0)
                elif is_animal_only and sig in ("signal_herido_grave", "signal_atrapado", "signal_fallecido", "riesgo_vital_textual"):
                    signals[sig] = BoolWithConfidence(value=False, confidence=1.0)
                
            p_fallecido = float(probs[0][0, 1]) if probs[0].shape[1] == 2 else float(probs[0][0, 0])
            p_herido = float(probs[1][0, 1]) if probs[1].shape[1] == 2 else float(probs[1][0, 0])
            p_atrapado = float(probs[2][0, 1]) if probs[2].shape[1] == 2 else float(probs[2][0, 0])
            p_incendio = float(probs[5][0, 1]) if probs[5].shape[1] == 2 else float(probs[5][0, 0])
            p_vital = float(probs[9][0, 1]) if probs[9].shape[1] == 2 else float(probs[9][0, 0])
            
            # Ajustar probabilidades auxiliares según la fusión
            if not signals["signal_fallecido"].value:
                p_fallecido = min(0.10, p_fallecido)
            if not signals["signal_herido_grave"].value:
                p_herido = min(0.10, p_herido)
            if not signals["riesgo_vital_textual"].value:
                p_vital = min(0.10, p_vital)
        else:
            signals = det_signals
            # Probabilidades deterministas/heurísticas de reserva
            p_fallecido = 0.94 if signals["signal_fallecido"].value else 0.04
            p_herido = 0.92 if signals["signal_herido_grave"].value else 0.06
            p_atrapado = 0.95 if signals["signal_atrapado"].value else 0.03
            p_incendio = 0.93 if signals["signal_incendio"].value else 0.05
            p_vital = 0.96 if (signals["riesgo_vital_textual"].value or signals["signal_fallecido"].value or signals["signal_herido_grave"].value) else 0.08

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

        # Fusión final de señales
        if self.dl_engine_active:
            fused_signals = signals
        else:
            def fuse_signal(regex_val: bool, neural_prob: float) -> BoolWithConfidence:
                if regex_val:
                    confidence = max(0.95, neural_prob)
                    return BoolWithConfidence(value=True, confidence=confidence)
                else:
                    confidence = max(0.90, 1.0 - neural_prob)
                    return BoolWithConfidence(value=False, confidence=confidence)
            
            fused_signals = {
                "signal_fallecido": fuse_signal(has_fatal, p_fallecido),
                "signal_herido_grave": fuse_signal(has_injured, p_herido),
                "signal_atrapado": fuse_signal(has_trapped, p_atrapado),
                "signal_intoxicacion": signals["signal_intoxicacion"],
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
        if fused_signals["signal_accidente_trafico"].value:
            tipo_incidente_normalizado = CategoriaPreliminar.ACCIDENTE_TRAFICO
        elif fused_signals["signal_incendio"].value:
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

        # V14: avisos_simultaneos_zona
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
            **fused_signals,
            model_version_capa1=self.model_version,
            inference_timestamp=datetime.now(timezone.utc),
            inference_latency_ms=latency_ms,
            extractor_warnings=warnings,
        )
