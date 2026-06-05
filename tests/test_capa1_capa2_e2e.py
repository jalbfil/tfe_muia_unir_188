"""Smoke tests for the Capa 1 -> Capa 2 integration path."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "src" / "contracts"))

from scripts.validate_capa1_capa2_e2e import run_validation  # noqa: E402


def test_capa1_capa2_e2e_curated_scenarios_pass() -> None:
    payload = run_validation()

    assert payload["summary"]["cases"] >= 5
    assert payload["summary"]["failed_cases"] == 0
    assert payload["summary"]["mean_capa1_latency_ms"] < 500


def test_capa1_detects_critical_signals_for_p1_cases() -> None:
    payload = run_validation()
    p1_cases = [
        row
        for row in payload["cases"]
        if "P1" in row["acceptable_priorities"]
    ]

    assert p1_cases
    assert all(row["signals_ok"] for row in p1_cases)
    assert any(row["observed_signals"]["signal_atrapado"] for row in p1_cases)
    assert any(row["observed_signals"]["signal_herido_grave"] for row in p1_cases)
