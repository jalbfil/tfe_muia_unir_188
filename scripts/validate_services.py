# -*- coding: utf-8 -*-
"""
Validacion E2E de todos los servicios del sistema 112 CyL.
Uso: uv run python scripts/validate_services.py
"""
from __future__ import annotations

import io
import json
import os
import sys
import time
import traceback
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
SEP    = "-" * 64

def ok(msg: str)   -> None: print(f"  {GREEN}[OK]   {msg}{RESET}")
def fail(msg: str) -> None: print(f"  {RED}[FAIL] {msg}{RESET}")
def warn(msg: str) -> None: print(f"  {YELLOW}[WARN] {msg}{RESET}")
def info(msg: str) -> None: print(f"         {msg}")

def section(title: str) -> None:
    print(f"\n{BOLD}{CYAN}{SEP}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{SEP}{RESET}")

RESULTS: list[tuple[str, bool, str]] = []

def check(name: str, passed: bool, detail: str = "") -> None:
    RESULTS.append((name, passed, detail))
    msg = f"{name}" + (f"  [{detail}]" if detail else "")
    (ok if passed else fail)(msg)

import httpx  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# 1. Ollama LLM
# ─────────────────────────────────────────────────────────────────────────────
section("1 · Ollama LLM (:11434)")

try:
    r = httpx.get("http://localhost:11434", timeout=5)
    check("Ollama responde", r.status_code == 200, r.text.strip()[:50])
except Exception as e:
    check("Ollama responde", False, str(e))

try:
    r = httpx.get("http://localhost:11434/api/tags", timeout=5)
    models = r.json().get("models", [])
    names  = [m["name"] for m in models]
    info(f"Modelos disponibles: {names}")
    llama_present = any("llama" in n.lower() for n in names)
    check("Modelo llama3.1 disponible", llama_present, str(names))
except Exception as e:
    check("Modelos Ollama", False, str(e))

try:
    model_name = os.environ.get("OLLAMA_MODEL", "llama3.1:8b-instruct-q4_K_M")
    t0 = time.time()
    r = httpx.post(
        "http://localhost:11434/api/generate",
        json={"model": model_name, "prompt": "Responde solo: OK", "stream": False},
        timeout=60,
    )
    elapsed = time.time() - t0
    if r.status_code == 200:
        resp_text = r.json().get("response", "")[:80]
        check(f"Inferencia LLM ({model_name})", True, f"{elapsed:.1f}s -> '{resp_text}'")
    else:
        check(f"Inferencia LLM ({model_name})", False, f"HTTP {r.status_code}")
except Exception as e:
    check("Inferencia LLM", False, str(e))

# ─────────────────────────────────────────────────────────────────────────────
# 2. FastAPI Backend
# ─────────────────────────────────────────────────────────────────────────────
section("2 · FastAPI Backend (:8000)")

try:
    r = httpx.get("http://localhost:8000/healthz", timeout=5)
    data     = r.json()
    degraded = data.get("degraded", True)
    check("GET /healthz responde", r.status_code == 200, json.dumps(data))
    check("LLM conectado (degraded=False)", not degraded, f"degraded={degraded}")
except Exception as e:
    check("GET /healthz", False, str(e))

try:
    r = httpx.get("http://localhost:8000/version", timeout=5)
    check("GET /version", r.status_code == 200, r.text.strip())
except Exception as e:
    check("GET /version", False, str(e))

try:
    r = httpx.get("http://localhost:8000/.well-known/agent.json", timeout=5)
    card  = r.json()
    tools = card.get("mcpTools", [])
    check("Agent Card + 3 MCP tools declaradas", r.status_code == 200 and len(tools) == 3,
          f"mcpTools={tools}")
except Exception as e:
    check("Agent Card", False, str(e))

# ─────────────────────────────────────────────────────────────────────────────
# 3. POST /predict — E2E Capa 1->2->3
# Provincia debe ser MAYUSCULAS (ProvinciaCyL enum)
# ─────────────────────────────────────────────────────────────────────────────
section("3 · POST /predict — E2E (Capa 1->2->3)")

SCENARIOS = [
    ("Escenario P1 — incendio grave", {
        "incident_id":      "VAL-TEST-P1-001",
        "texto_titulo":     "Incendio en cocina de bar concurrido en el centro de Burgos",
        "texto_descripcion": (
            "Hay humo denso, varias personas atrapadas en la planta superior. "
            "Se ven llamas por las ventanas del primer piso."
        ),
        "localidad":        "Burgos",
        "provincia":        "BURGOS",          # ProvinciaCyL enum en MAYUSCULAS
        "fecha_incidente":  "2026-06-10T00:20:00+02:00",
        "operador_id":      "OP-TEST-001",
    }),
    ("Escenario P4 — perro extraviado", {
        "incident_id":      "VAL-TEST-P4-001",
        "texto_titulo":     "Perro extraviado en parque de Valladolid",
        "texto_descripcion": "Propietario tranquilo, perro encontrado cerca. Sin urgencia.",
        "localidad":        "Valladolid",
        "provincia":        "VALLADOLID",      # ProvinciaCyL enum en MAYUSCULAS
        "fecha_incidente":  "2026-06-10T00:20:00+02:00",
        "operador_id":      "OP-TEST-001",
    }),
]

for label, payload in SCENARIOS:
    try:
        t0  = time.time()
        r   = httpx.post("http://localhost:8000/predict", json=payload, timeout=180)
        elapsed = time.time() - t0
        if r.status_code == 200:
            data     = r.json()
            rec      = data.get("recommendation", {})
            priority = rec.get("priority_recommended") or rec.get("priority")
            expl     = rec.get("explanation_text", "")
            legal    = rec.get("legal_citations", [])
            prio_det = data.get("priority_details", {})
            rules    = prio_det.get("activated_rules", [])
            deg      = data.get("degraded", True)
            llm_meta = rec.get("llm_metadata", {})
            llm_mod  = llm_meta.get("llm_model", "?")
            tools_inv = llm_meta.get("tools_invoked", [])

            check(f"{label} — HTTP 200", True, f"{elapsed:.1f}s")
            check(f"{label} — priority devuelta", priority is not None, f"priority={priority}")
            check(f"{label} — explanation (>=20 chars)", len(expl) >= 20, f"{len(expl)} chars")
            check(f"{label} — reglas activadas (Capa 2)", len(rules) > 0, f"{len(rules)} reglas")
            is_p1p2 = priority in ("P1", "P2")
            check(f"{label} — citas legales (Capa 3)", len(legal) > 0 if is_p1p2 else True, f"{len(legal)} citas")
            check(f"{label} — LLM real (no degradado)", not deg, f"degraded={deg}  llm={llm_mod}")
            check(f"{label} — MCP tools invocadas", len(tools_inv) > 0, f"tools_invoked={tools_inv}")
            info(f"  priority={priority}  llm={llm_mod}  tools={tools_inv}")
            info(f"  explanation[:120]: {expl[:120]}")
        else:
            check(f"{label}", False, f"HTTP {r.status_code}: {r.text[:300]}")
    except Exception as e:
        check(f"{label}", False, str(e))

# ─────────────────────────────────────────────────────────────────────────────
# 4. Anti-leakage
# ─────────────────────────────────────────────────────────────────────────────
section("4 · Anti-leakage Gate (Principio V)")

try:
    payload_leak = {
        "incident_id":     "VAL-LEAK-001",
        "texto_titulo":    "Test leakage gate",
        "fecha_incidente": "2026-06-10T00:20:00+02:00",
        "operador_id":     "OP-TEST-001",
        "medios_mov":      5,       # extra="forbid" debe rechazar esto (HTTP 422)
        "pacientes_aten":  3,
    }
    r = httpx.post("http://localhost:8000/predict", json=payload_leak, timeout=15)
    check("Campos leakage rechazados (HTTP 422)", r.status_code == 422, f"HTTP {r.status_code}")
except Exception as e:
    check("Anti-leakage gate", False, str(e))

# ─────────────────────────────────────────────────────────────────────────────
# 5. RAG — via search_normative (que usa chromadb internamente)
# ─────────────────────────────────────────────────────────────────────────────
section("5 · RAG — ChromaDB via search_normative")

try:
    from capa3_llm_mcp.mcp_server.tools.search_normative import search_normative  # type: ignore

    r63 = search_normative("atrapado herido grave", n=3)
    rag_ok = len(r63) > 0
    check("RAG indexado y accesible (chromadb + sentence-transformers)", rag_ok,
          f"{len(r63)} chunks" if rag_ok else "0 chunks -> chromadb no instalado en .venv")

    if rag_ok:
        top1      = r63[0]
        norma_id  = top1.get("norma_id", "")
        score     = top1.get("score", 0)
        info(f"  T063 top-1: norma_id={norma_id}  score={score:.4f}  text[:80]={top1.get('text','')[:80]}")
        check("T063 — 'atrapado herido grave' -> norma relevante", bool(norma_id),
              f"norma_id={norma_id}  score={score:.4f}")

        r64 = search_normative("fuga quimica camion cisterna", n=1)
        if r64:
            top1q = r64[0]
            norma_q = top1q.get("norma_id", "")
            text_q  = top1q.get("text", "").lower()
            score_q = top1q.get("score", 0)
            info(f"  T064 top-1: norma_id={norma_q}  score={score_q:.4f}  text[:80]={top1q.get('text','')[:80]}")
            expected_q = any(kw in (norma_q.lower() + text_q)
                             for kw in ["plancal", "infocal", "mpcyl", "quimic", "peligros", "transporte"])
            check("T064 — 'fuga quimica cisterna' -> norma relevante", expected_q,
                  f"norma_id={norma_q}  score={score_q:.4f}")

        # Cuenta total de chunks
        try:
            from capa3_llm_mcp.mcp_server.tools.search_normative import _load_rag  # type: ignore
            col, _ = _load_rag()
            count   = col.count()
            check("ChromaDB: >1000 chunks indexados", count > 1000, f"{count} chunks")
        except Exception as e2:
            warn(f"No se pudo contar chunks: {e2}")
    else:
        warn("RAG inaccesible -> el backend usa search_normative con lista vacia silenciosa")
        warn("Esto significa que /predict funciona pero sin contexto normativo real (RAG desactivado)")

except ImportError as e:
    check("search_normative importable", False, str(e))
except Exception as e:
    check("RAG retrieval", False, traceback.format_exc()[-300:])

# ─────────────────────────────────────────────────────────────────────────────
# 6. MCP Tools — firmas correctas
# ─────────────────────────────────────────────────────────────────────────────
section("6 · MCP Tools (importacion directa)")

try:
    from capa3_llm_mcp.mcp_server.tools.search_normative import search_normative  # type: ignore
    result = search_normative("personas atrapadas incendio", n=3)
    rag_ok2 = len(result) > 0
    check("search_normative disponible", True,
          f"{len(result)} chunks" if rag_ok2 else "0 chunks (chromadb no instalado)")
    if not rag_ok2:
        warn("search_normative retorna [] silencioso — RAG no operativo en este entorno")
except Exception as e:
    check("search_normative tool", False, str(e))

try:
    from capa3_llm_mcp.mcp_server.tools.cite_legal_basis import cite_legal_basis  # type: ignore
    r1 = cite_legal_basis("LEY_17_2015")
    r2 = cite_legal_basis("PLANCAL_DEC_4_2019")
    r3 = cite_legal_basis("INFOCAL_DEC_6_2025")
    check("cite_legal_basis('LEY_17_2015')",         bool(r1.get("texto_relevante")), r1.get("articulo_o_seccion"))
    check("cite_legal_basis('PLANCAL_DEC_4_2019')",  bool(r2.get("texto_relevante")), r2.get("articulo_o_seccion"))
    check("cite_legal_basis('INFOCAL_DEC_6_2025')",  bool(r3.get("texto_relevante")), r3.get("articulo_o_seccion"))
except Exception as e:
    check("cite_legal_basis tool", False, str(e))

try:
    from capa3_llm_mcp.mcp_server.tools.get_rule_details import get_rule_details  # type: ignore
    result = get_rule_details(
        rule_id="RD-TEST-01",
        human_text="Incendio con personas atrapadas -> P1",
        weight=0.92,
        normative_anchors=["LEY_17_2015", "PLANCAL_DEC_4_2019"],
    )
    check(
        "get_rule_details(rule_id, human_text, weight, anchors)",
        result.get("evidence_level") == "normative" and len(result.get("normative_anchors", [])) == 2,
        f"evidence_level={result.get('evidence_level')}  urls={[a['url'][:30] for a in result.get('normative_anchors',[])]}",
    )
except Exception as e:
    check("get_rule_details tool", False, str(e))

# ─────────────────────────────────────────────────────────────────────────────
# 7. Capa 3 — explain() directo
# ActivatedRule esta en contracts.priority_recommendation (no en contracts.rule)
# ─────────────────────────────────────────────────────────────────────────────
section("7 · Capa 3 — explain() directo")

try:
    from capa3_llm_mcp.llm.qwen_wrapper import QwenWrapper  # type: ignore
    wrapper = QwenWrapper()
    avail   = wrapper.is_available()
    check("QwenWrapper.is_available()", avail, "LLM online" if avail else "LLM offline")
except Exception as e:
    check("QwenWrapper importable", False, str(e))

try:
    from capa3_llm_mcp.explainer import explain  # type: ignore
    from contracts.priority_recommendation import PriorityRecommendation, ActivatedRule  # type: ignore
    from contracts.enums import Priority, ConfidenceLevel, ModelUsed, NormaID  # type: ignore

    rule = ActivatedRule(
        rule_id="R-TEST-01",
        human_text="Incendio con personas atrapadas implica P1",
        weight=0.92,
        normative_anchors=[NormaID.LEY_17_2015, NormaID.PLANCAL_DEC_4_2019],
    )
    rec = PriorityRecommendation(
        incident_id="VAL-DIRECT-001",
        priority_recommended=Priority.P1,
        confidence_level=ConfidenceLevel.HIGH,
        probabilities={
            Priority.P1: 0.85,
            Priority.P2: 0.10,
            Priority.P3: 0.03,
            Priority.P4: 0.02,
        },
        activated_rules=[rule],
        model_used=ModelUsed.RULEFIT,
        model_version_capa2="0.1.0",
        requires_human_attention=True,
    )

    t0  = time.time()
    op  = explain(rec, "Incendio con personas atrapadas en Burgos")
    elapsed = time.time() - t0

    check("explain() completa sin error", op is not None, f"{elapsed:.1f}s")
    if op:
        expl_text  = getattr(op, "explanation_text", "")
        legal      = getattr(op, "legal_citations", [])
        llm_meta   = getattr(op, "llm_metadata", None)
        tools_inv  = getattr(llm_meta, "tools_invoked", []) if llm_meta else []
        llm_mod    = getattr(llm_meta, "llm_model", "?") if llm_meta else "?"
        hints      = getattr(op, "actuation_hints", [])
        acts_summ  = getattr(op, "activated_rules_summary", [])

        check("explanation_text >= 20 chars", len(expl_text) >= 20, f"{len(expl_text)} chars")
        check("legal_citations >= 1 (garantia P1)", len(legal) >= 1, f"{len(legal)} citas")
        check("MCP tools invocadas en llm_metadata", len(tools_inv) > 0, f"tools={tools_inv}")
        check("LLM real en metadata (no degradado)", "degraded" not in llm_mod.lower(),
              f"llm_model={llm_mod}")
        check("actuation_hints presentes", len(hints) > 0, f"{len(hints)} hints")
        check("activated_rules_summary presente", len(acts_summ) > 0, f"{len(acts_summ)} items")

        info(f"  llm_model={llm_mod}")
        info(f"  tools_invoked={tools_inv}")
        info(f"  legal_citations={[getattr(c,'norma_id','?') for c in legal]}")
        info(f"  explanation[:150]: {expl_text[:150]}")

except Exception as e:
    check("explain() directo", False, traceback.format_exc()[-500:])

# ─────────────────────────────────────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────────────────────────────────────
section("RESUMEN FINAL")

total  = len(RESULTS)
passed = sum(1 for _, p, _ in RESULTS if p)
failed = total - passed

print(f"\n  Total checks : {total}")
print(f"  {GREEN}Passed       : {passed}{RESET}")
print(f"  {RED}Failed       : {failed}{RESET}")
print()

if failed > 0:
    print(f"  {RED}Checks fallidos:{RESET}")
    for name, p, detail in RESULTS:
        if not p:
            print(f"    {RED}[X] {name}{RESET}")
            if detail:
                print(f"        {detail[:250]}")

sys.exit(0 if failed == 0 else 1)
