# Quickstart — Escenario E2E ejecutable como integration test

**Feature**: `001-priorizacion-112-cyl` · **Updated**: 2026-05-24

Este documento describe el escenario E2E mínimo que valida que las tres capas funcionan integradas. Se ejecutará como `tests/integration/test_quickstart.py` y debe pasar antes de considerar el sistema "Phase 4 complete".

---

## Pre-requisitos

- Modelos entrenados disponibles en `artifacts/models/{capa1,capa2,capa3}/v0.1.0/`
- Índice RAG construido en `artifacts/rag/chroma/`
- LLM cuantizado en `artifacts/llm/qwen2.5-7b-q4_k_m.gguf`
- Backend FastAPI levantado en `localhost:8000`
- MCP server escuchando en `localhost:8765`

---

## Escenario 1 — Incidente P1 crítico

### Input

```json
{
  "incident_id": "01J5Y8KQ3FXQH4PVDXY9N7B0AQ",
  "texto_titulo": "Accidente grave N-122",
  "texto_descripcion": "Varón inconsciente tras choque frontal en N-122 km 245, herido grave atrapado en el habitáculo, otro pasajero camina aturdido. Han llamado varios testigos.",
  "categoria_preliminar": "ACCIDENTE_TRAFICO",
  "latitud": 41.6235,
  "longitud": -4.7268,
  "localidad": "Aldealuenga de Santa María",
  "provincia": "SORIA",
  "fecha_incidente": "2026-05-24T18:42:00+02:00",
  "operador_id": "OP-CYL-007"
}
```

### Pasos

1. **POST** `/predict` con el JSON anterior.
2. Backend invoca **Capa 1 NLP** → produce `IncidentFeatures` con `V01.value=true`, `V02.value≥2`, `V03.value="GRAVE"`, `signal_atrapado.value=true`, `signal_herido_grave.value=true`, `signal_varias_llamadas.value=true`.
3. Backend invoca **Capa 2 RuleFit** → produce `PriorityRecommendation` con `priority_recommended="P1"`, `probabilities.P1 ≥ 0.80`, `model_used="RULEFIT"`, ≥2 reglas activadas.
4. Backend invoca **Capa 3 LLM+MCP** → produce `OperatorRecommendation` con `explanation_text` mencionando atrapamiento y herido grave, `legal_citations` con ≥1 entrada (`LEY_17_2015`), `tools_invoked` incluye `cite_legal_basis`.
5. Backend devuelve `OperatorRecommendation` al cliente.
6. Log de inferencia escrito en SQLite + JSONL.

### Asserts

- `response.status_code == 200`
- `response.priority_recommended == "P1"`
- `response.probabilities["P1"] >= 0.80`
- `len(response.activated_rules_summary) >= 2`
- `len(response.legal_citations) >= 1`
- `any(c.norma_id == "LEY_17_2015" for c in response.legal_citations)`
- `response.confidence_level in ("HIGH", "MEDIUM")`
- Latencia Capa 1+2 ≤ 500 ms (p95 sobre 100 runs)
- Latencia total ≤ 2 000 ms (p95 sobre 100 runs)

---

## Escenario 2 — Incidente P4 banal

### Input

```json
{
  "incident_id": "01J5Y8M3KX8MAFG3VKVK7DQX02",
  "texto_titulo": "Árbol caído en arcén",
  "texto_descripcion": "Árbol de tamaño medio caído en el arcén derecho, no obstaculiza la circulación, sin heridos.",
  "categoria_preliminar": "INFRAESTRUCTURA",
  "latitud": 42.8125,
  "longitud": -1.6458,
  "localidad": "Cervera de Pisuerga",
  "provincia": "PALENCIA",
  "fecha_incidente": "2026-05-24T11:15:00+02:00",
  "operador_id": "OP-CYL-007"
}
```

### Asserts

- `response.priority_recommended in ("P3", "P4")`
- `response.probabilities["P4"] >= 0.60` o `probabilities["P3"] >= 0.60`
- `len(response.legal_citations) >= 0` (no obligatorio para P3/P4)
- `response.requires_human_attention == False` (si confidence HIGH)

---

## Escenario 3 — Incidente con química peligrosa (MPCyL)

### Input

```json
{
  "incident_id": "01J5Y8MWX4QQTPN8H82FM6R5F0",
  "texto_titulo": "Fuga química en autovía",
  "texto_descripcion": "Camión cisterna con olor fuerte a producto químico desconocido en A-62 km 130, varios conductores reportan irritación ocular, nube blanquecina visible.",
  "categoria_preliminar": "MERCANCIAS_PELIGROSAS",
  "latitud": 41.9876,
  "longitud": -5.2341,
  "fecha_incidente": "2026-05-24T14:00:00+02:00",
  "operador_id": "OP-CYL-007"
}
```

### Asserts

- `response.priority_recommended in ("P1", "P2")`
- `any("intoxicacion" in r.lower() or "mercancia" in r.lower() for r in response.activated_rules_summary)`
- `any(c.norma_id == "MPCYL_ACUERDO_3_2008" for c in response.legal_citations)`

---

## Escenario 4 — Decisión del operador divergente

### Pasos

1. Ejecutar Escenario 2 (sistema recomienda P4).
2. **POST** `/feedback` con:
   ```json
   {
     "incident_id": "01J5Y8M3KX8MAFG3VKVK7DQX02",
     "priority_assigned_by_operator": "P2",
     "motivo_divergencia": "Cercanía a colegio no detectada por el sistema, alto tráfico"
   }
   ```
3. Backend almacena `OperatorDecision` y emite evento `DIVERGENCE_HIGH` (divergencia ≥2 niveles).

### Asserts

- Registro persistido en `inference_log`.
- Evento auditoría generado.
- Métrica `divergence_rate` incrementada en dashboard.

---

## Escenario 5 — Entrada inválida (variable prohibida)

### Input

```json
{
  "incident_id": "01J5Y8N2K7FRRGV3CTPJP4M8H8",
  "texto_titulo": "Test leakage",
  "texto_descripcion": "Test",
  "fecha_incidente": "2026-05-24T12:00:00+02:00",
  "operador_id": "OP-CYL-007",
  "medios_movilizados": ["UME", "GUARDIA_CIVIL"]
}
```

### Asserts

- `response.status_code == 400`
- `response.error_code == "LEAKAGE_FIELD_REJECTED"`
- Error menciona `medios_movilizados` y referencia al Principio V.

---

## Escenario 6 — Modo degradado (LLM no disponible)

### Pasos

1. Detener LLM (simular caída).
2. Ejecutar Escenario 1.

### Asserts

- `response.status_code == 200`
- `response.priority_recommended == "P1"` (Capa 1+2 siguen funcionando)
- `response.explanation_text` contiene fallback estático (ej. "Explicación detallada no disponible; revise reglas activadas")
- `response.llm_metadata.llm_model == "FALLBACK_NONE"`
- Header `X-Degraded-Mode: true`

---

## Ejecución

```bash
pytest tests/integration/test_quickstart.py -v --benchmark-only
```

Salida esperada: 6/6 escenarios pasan, latencia p95 dentro de SLA.

---

## Checklist de validación (Phase 5)

- [ ] Escenario 1 (P1 crítico) pasa
- [ ] Escenario 2 (P4 banal) pasa
- [ ] Escenario 3 (MPCyL química) pasa
- [ ] Escenario 4 (divergencia operador) pasa
- [ ] Escenario 5 (rechazo leakage) pasa
- [ ] Escenario 6 (modo degradado) pasa
- [ ] Latencia Capa 1+2 p95 ≤ 500 ms
- [ ] Latencia total p95 ≤ 2 000 ms
- [ ] Log auditable generado en todos los escenarios
