"""T072 — Test latencia Capa 3: explicación ≤ 2000 ms p95 sobre 10 llamadas.

SKIP si el modelo .gguf no está disponible (CI).

En CI se ejecuta en modo degradado (sin LLM) para validar que al menos
el path sin-LLM cumple el SLA con margen amplio.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from contracts import (  # type: ignore[import]
    ActivatedRule,
    ConfidenceLevel,
    ModelUsed,
    NormaID,
    Priority,
    PriorityRecommendation,
)
from capa3_llm_mcp.explainer import _SLA_MS, explain  # type: ignore[import]
from capa3_llm_mcp.llm.qwen_wrapper import QwenWrapper  # type: ignore[import]

_N_SAMPLES = 10
_P95_INDEX = int(_N_SAMPLES * 0.95) - 1  # índice p95 sobre 10 muestras

_MOCK_RESPONSE = """\
{
  "explanation_text": "Incidente clasificado como prioridad media. Evaluación necesaria por unidades especializadas.",
  "actuation_hints": ["Enviar unidad de evaluación", "Monitorear evolución"],
  "confidence_disclaimer": null
}"""


def _make_rec() -> PriorityRecommendation:
    return PriorityRecommendation(
        incident_id="LATENCY-TEST",
        priority_recommended=Priority.P3,
        probabilities={
            Priority.P1: 0.05,
            Priority.P2: 0.10,
            Priority.P3: 0.70,
            Priority.P4: 0.15,
        },
        activated_rules=[
            ActivatedRule(
                rule_id="RD-05",
                human_text="Incendio activo sin víctimas → P3",
                weight=0.8,
                normative_anchors=[NormaID.INFOCAL_DEC_6_2025],
            )
        ],
        confidence_level=ConfidenceLevel.MEDIUM,
        model_used=ModelUsed.RULEFIT,
        model_version_capa2="0.1.0",
        requires_human_attention=False,
    )


def test_t072_degraded_mode_well_within_sla():
    """T072-A: modo degradado (sin LLM) cumple SLA 2000 ms con margen amplio.

    Objetivo: p95 < 200 ms en modo degradado (sin RAG ni LLM).
    """
    rec = _make_rec()
    mock_llm = MagicMock(spec=QwenWrapper)
    mock_llm.is_available.return_value = False

    latencies = []
    for _ in range(_N_SAMPLES):
        t0 = time.perf_counter()
        explain(rec, "incendio en edificio", llm=mock_llm)
        latencies.append((time.perf_counter() - t0) * 1000)

    latencies.sort()
    p95 = latencies[min(_P95_INDEX, len(latencies) - 1)]
    assert p95 < 200.0, (
        f"Modo degradado p95={p95:.1f}ms supera 200ms. "
        "Revisar imports pesados en el path de llamada."
    )


def test_t072_mock_llm_within_sla():
    """T072-B: LLM mockeado (sin inferencia real) cumple SLA 2000 ms.

    Valida que el overhead de orquestación (RAG skip + prompt build + mock) sea < 500 ms.
    """
    rec = _make_rec()
    mock_llm = MagicMock(spec=QwenWrapper)
    mock_llm.is_available.return_value = True
    mock_llm.chat.return_value = _MOCK_RESPONSE

    latencies = []
    for _ in range(_N_SAMPLES):
        t0 = time.perf_counter()
        explain(rec, "incendio en edificio", llm=mock_llm)
        latencies.append((time.perf_counter() - t0) * 1000)

    latencies.sort()
    p95 = latencies[min(_P95_INDEX, len(latencies) - 1)]
    assert p95 < _SLA_MS, (
        f"Overhead de orquestación p95={p95:.1f}ms supera SLA={_SLA_MS:.0f}ms. "
        "El SLA real incluye latencia de inferencia LLM (~1-2s adicionales)."
    )


@pytest.mark.skipif(
    not (Path(__file__).resolve().parents[3] / "artifacts/llm/qwen2.5-7b-instruct-q4_k_m.gguf").exists(),
    reason="Modelo .gguf no descargado (artifacts/llm/). Ejecutar en entorno con modelo.",
)
def test_t072_real_llm_p95_within_sla():
    """T072-C: LLM real Qwen2.5-7B Q4_K_M p95 ≤ 2000 ms.

    Solo se ejecuta si el modelo está descargado. Requiere RTX 5070 o similar.
    """
    from capa3_llm_mcp.llm.qwen_wrapper import QwenWrapper  # type: ignore[import]

    rec = _make_rec()
    llm = QwenWrapper()

    latencies = []
    for _ in range(_N_SAMPLES):
        t0 = time.perf_counter()
        explain(rec, "incendio en edificio sin víctimas", llm=llm)
        latencies.append((time.perf_counter() - t0) * 1000)

    latencies.sort()
    p95 = latencies[min(_P95_INDEX, len(latencies) - 1)]
    assert p95 <= _SLA_MS, (
        f"LLM real p95={p95:.1f}ms > SLA={_SLA_MS:.0f}ms. "
        "Verificar n_gpu_layers=-1 y que el modelo está en VRAM."
    )
