"""T079 — Servidor MCP v0.1.0 con 3 tools: search_normative, get_rule_details, cite_legal_basis.

Transporte: SSE en localhost:8765 (producción) o stdio (CI/test).

Uso:
    # Modo servidor SSE (producción):
    python -m capa3_llm_mcp.mcp_server.server

    # Modo stdio (testing/integración):
    python -m capa3_llm_mcp.mcp_server.server --stdio

Dependencias:
    pip install mcp
"""
from __future__ import annotations

import argparse
import sys


# ── importación perezosa del SDK MCP ──────────────────────────────────────────
def _get_mcp():
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore[import-untyped]
        return FastMCP
    except ImportError as exc:
        raise ImportError("pip install mcp") from exc


# ── construcción del servidor ─────────────────────────────────────────────────

def build_server():
    """Construye y devuelve el servidor FastMCP con las 3 tools registradas."""
    from .tools import cite_legal_basis, get_rule_details, search_normative

    FastMCP = _get_mcp()  # noqa: N806 — FastMCP es una clase retornada dinámicamente
    server = FastMCP("normativa-cyl-v010")

    @server.tool()
    def search_normative_tool(query: str, n: int = 5) -> list[dict]:
        """Búsqueda semántica en el corpus normativo CyL (RAG).

        Devuelve los `n` fragmentos más relevantes con norma_id, articulo y texto.
        """
        return search_normative(query, n)

    @server.tool()
    def get_rule_details_tool(
        rule_id: str,
        human_text: str,
        weight: float,
        normative_anchors: list[str],
    ) -> dict:
        """Detalle enriquecido de una regla activada: normas referenciadas + URLs."""
        return get_rule_details(rule_id, human_text, weight, normative_anchors)

    @server.tool()
    def cite_legal_basis_tool(norma_id: str, articulo: str | None = None) -> dict:
        """Cita canónica para un NormaID: articulo, texto relevante, URL oficial."""
        return cite_legal_basis(norma_id, articulo)

    return server


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Servidor MCP normativa-cyl v0.1.0")
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Usar transporte stdio en lugar de SSE (para integración con LLM local).",
    )
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    server = build_server()

    if args.stdio:
        server.run(transport="stdio")
    else:
        server.run(transport="sse", host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
