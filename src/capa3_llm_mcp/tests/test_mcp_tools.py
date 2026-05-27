"""T080 — Test integración MCP: cada tool devuelve el schema esperado.

No requiere servidor MCP en ejecución: las tools se invocan como funciones Python.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from capa3_llm_mcp.mcp_server.tools import (  # type: ignore[import]
    cite_legal_basis,
    get_rule_details,
    search_normative,
)

# ── T080-A: search_normative ──────────────────────────────────────────────────

def test_t080_search_normative_returns_list():
    """search_normative siempre devuelve lista (vacía si índice no disponible)."""
    result = search_normative("atrapado herido grave", n=3)
    assert isinstance(result, list)


def test_t080_search_normative_schema_when_available():
    """Si el índice RAG existe, cada chunk tiene las keys esperadas."""
    result = search_normative("protección civil emergencia", n=2)
    for chunk in result:
        assert "norma_id" in chunk
        assert "articulo" in chunk
        assert "text" in chunk
        assert "score" in chunk
        assert isinstance(chunk["score"], float)
        assert 0.0 <= chunk["score"] <= 1.0


def test_t080_search_normative_n_clamped():
    """n se acota entre 1 y 20 sin lanzar excepción."""
    r1 = search_normative("emergencia", n=0)   # clamp a 1
    r2 = search_normative("emergencia", n=100)  # clamp a 20
    assert isinstance(r1, list)
    assert isinstance(r2, list)


# ── T080-B: get_rule_details ──────────────────────────────────────────────────

def test_t080_get_rule_details_schema():
    """get_rule_details devuelve las keys del schema esperado."""
    result = get_rule_details(
        rule_id="RD-01",
        human_text="Víctimas atrapadas con riesgo vital → P1 fija",
        weight=1.0,
        normative_anchors=["LEY_17_2015", "PLANCAL_DEC_4_2019"],
    )
    assert result["rule_id"] == "RD-01"
    assert result["weight"] == 1.0
    assert isinstance(result["normative_anchors"], list)
    assert result["evidence_level"] == "normative"
    for anchor in result["normative_anchors"]:
        assert "norma_id" in anchor
        assert "url" in anchor


def test_t080_get_rule_details_no_anchors_heuristic():
    """Sin anchors → evidence_level == 'heuristic'."""
    result = get_rule_details(
        rule_id="RD-99",
        human_text="Regla heurística sin anclaje normativo",
        weight=0.3,
        normative_anchors=[],
    )
    assert result["evidence_level"] == "heuristic"
    assert result["normative_anchors"] == []


# ── T080-C: cite_legal_basis ──────────────────────────────────────────────────

@pytest.mark.parametrize("norma_id", [
    "LEY_17_2015",
    "PLANCAL_DEC_4_2019",
    "RGPD",
    "REG_UE_2024_1689",
])
def test_t080_cite_legal_basis_known_normas(norma_id: str):
    """cite_legal_basis devuelve cita canónica para normas conocidas."""
    result = cite_legal_basis(norma_id)
    assert result["norma_id"] == norma_id
    assert result["texto_relevante"]
    assert len(result["texto_relevante"]) >= 20
    assert result["url_oficial"] is not None


def test_t080_cite_legal_basis_custom_articulo():
    """Si se pasa articulo, se usa en lugar del predeterminado."""
    result = cite_legal_basis("LEY_17_2015", articulo="art. 5")
    assert result["articulo_o_seccion"] == "art. 5"


def test_t080_cite_legal_basis_unknown_norma():
    """Para NormaID desconocido devuelve fallback sin lanzar excepción."""
    result = cite_legal_basis("NORMA_INEXISTENTE_XYZ")
    assert result["norma_id"] == "NORMA_INEXISTENTE_XYZ"
    assert result["texto_relevante"]
    assert result["url_oficial"] is None
