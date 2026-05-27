"""T042: Test de latencia de Capa 1 NLP para verificar el SLA de 500 ms p95."""

from __future__ import annotations

from datetime import datetime, timezone
import numpy as np
import pytest

from contracts import CategoriaPreliminar, IncidentInput
from capa1_nlp.inference.feature_extractor import FeatureExtractor


def test_feature_extractor_latency_sla() -> None:
    """Verifica que la latencia de inferencia de la Capa 1 cumpla con el SLA de <= 500 ms p95."""
    incident = IncidentInput(
        incident_id="01AN4V07BY79KA1307SR9X4MV3",
        texto_titulo="Accidente grave con atrapados",
        texto_descripcion="Colision frontal entre dos turismos en N-122 km 150. Hay un varon inconsciente atrapado en el coche.",
        categoria_preliminar=CategoriaPreliminar.ACCIDENTE_TRAFICO,
        fecha_incidente=datetime.now(timezone.utc),
        operador_id="OP_1234",
    )

    extractor = FeatureExtractor()

    # Calentamiento (warm-up)
    for _ in range(5):
        _ = extractor.extract_features(incident)

    # Medición sobre 100 iteraciones
    latencies: list[float] = []
    for _ in range(100):
        features = extractor.extract_features(incident)
        latencies.append(features.inference_latency_ms)

    p95 = np.percentile(latencies, 95)
    mean_latency = np.mean(latencies)

    print(f"\n[LATENCIA CAPA 1] Media: {mean_latency:.4f} ms | p95: {p95:.4f} ms")

    # La restricción es estricta: <= 500 ms p95
    assert p95 <= 500.0, f"SLA de latencia violado: p95 es {p95:.2f} ms (> 500 ms)"
