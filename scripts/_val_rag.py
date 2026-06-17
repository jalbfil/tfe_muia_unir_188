"""Validación rápida del pipeline completo con RAG activo."""
import httpx

payload = {
    "incident_id": "VAL-RAG-001",
    "texto_titulo": "Incendio con atrapados en Burgos",
    "texto_descripcion": "Llamas en planta baja, persona atrapada en primer piso",
    "fecha_incidente": "2026-06-10T12:00:00+02:00",
    "operador_id": "DBG-OP",
    "provincia": "BURGOS",
    "localidad": "Burgos",
}

r = httpx.post("http://localhost:8000/predict", json=payload, timeout=180)
d = r.json()
rec = d.get("recommendation", {})
pdet = d.get("priority_details", {})
llm_meta = rec.get("llm_metadata", {})
citations = rec.get("legal_citations", [])

print("=== RESULTADO PIPELINE COMPLETO ===")
print(f"HTTP status  : {r.status_code}")
print(f"degraded     : {d.get('degraded')}")
print(f"llm_model    : {llm_meta.get('llm_model')}")
print(f"tools_invoked: {llm_meta.get('tools_invoked')}")
print(f"priority     : {rec.get('priority_recommended')}")
print(f"probs        : {pdet.get('probabilities')}")
print(f"normas_citadas: {[c.get('norma_id') for c in citations]}")
print(f"explanation  : {rec.get('explanation_text', '')[:140]}")
