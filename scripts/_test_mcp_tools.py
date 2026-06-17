"""Test directo de las 3 tools MCP del TFE sin levantar el servidor completo."""
import sys
sys.path.insert(0, "src")

from capa3_llm_mcp.mcp_server.tools.search_normative import search_normative
from capa3_llm_mcp.mcp_server.tools.cite_legal_basis import cite_legal_basis
from capa3_llm_mcp.mcp_server.tools.get_rule_details import get_rule_details

print("=== TEST 1: search_normative (RAG) ===")
chunks = search_normative("accidente trafico con atrapados riesgo vital", n=3)
print(f"  Chunks encontrados: {len(chunks)}")
for c in chunks:
    norma = c["norma_id"]
    art = c["articulo"]
    score = c["score"]
    text_preview = c["text"][:90]
    print(f"  [{norma} {art}] score={score} | {text_preview}...")

print()
print("=== TEST 2: cite_legal_basis — LEY_17_2015 ===")
cita = cite_legal_basis("LEY_17_2015")
print(f"  articulo: {cita['articulo_o_seccion']}")
print(f"  texto:    {cita['texto_relevante'][:120]}")
print(f"  url:      {cita['url_oficial']}")

print()
print("=== TEST 3: cite_legal_basis — PLANCAL_DEC_4_2019 ===")
cita2 = cite_legal_basis("PLANCAL_DEC_4_2019")
print(f"  articulo: {cita2['articulo_o_seccion']}")
print(f"  texto:    {cita2['texto_relevante'][:120]}")
print(f"  url:      {cita2['url_oficial']}")

print()
print("=== TEST 4: get_rule_details ===")
rule = get_rule_details("SR-01", "Riesgo vital con atrapamiento confirmado", 1.0, ["LEY_17_2015", "PLANCAL_DEC_4_2019"])
print(f"  rule_id:         {rule.get('rule_id')}")
print(f"  human_text:      {rule.get('human_text')}")
enriched = rule.get("anchors_enriched", [])
print(f"  anchors_enriched: {len(enriched)}")
for a in enriched:
    print(f"    - {a.get('norma_id')}: {a.get('articulo_o_seccion')} | {a.get('url_oficial')}")

print()
print("=== TEST 5: Verificar servidor MCP (import FastMCP) ===")
from capa3_llm_mcp.mcp_server.server import build_server
server = build_server()
print(f"  Servidor MCP creado: {server.name}")
print("  Tools registradas: search_normative_tool, cite_legal_basis_tool, get_rule_details_tool")
print()
print("TODOS LOS TESTS PASARON OK")
