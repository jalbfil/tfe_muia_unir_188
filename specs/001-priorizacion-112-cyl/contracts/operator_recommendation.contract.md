# Contratos — Capa 3 → UI / cliente externo

**Contrato**: `OperatorRecommendation`
**Versión**: 0.1.0
**Productor**: `capa3_llm_mcp.explainer`
**Consumidor**: UI operador 112 / cliente MCP externo

## JSON Schema (resumen normativo)

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://tfm-188/contracts/0.1.0/OperatorRecommendation.json",
  "title": "OperatorRecommendation",
  "type": "object",
  "required": [
    "incident_id",
    "priority_recommended",
    "explanation_text",
    "legal_citations",
    "activated_rules_summary",
    "model_version_capa3",
    "llm_metadata"
  ],
  "additionalProperties": false,
  "properties": {
    "incident_id": { "type": "string" },
    "priority_recommended": { "enum": ["P1", "P2", "P3", "P4"] },
    "explanation_text": { "type": "string", "minLength": 20, "maxLength": 1200 },
    "legal_citations": {
      "type": "array",
      "items": { "$ref": "#/$defs/LegalCitation" }
    },
    "actuation_hints": {
      "type": "array",
      "items": { "type": "string", "maxLength": 200 }
    },
    "activated_rules_summary": {
      "type": "array",
      "items": { "type": "string", "maxLength": 200 }
    },
    "confidence_disclaimer": { "type": "string", "maxLength": 300 },
    "model_version_capa3": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "llm_metadata": {
      "type": "object",
      "required": ["llm_model", "temperature", "tools_invoked"],
      "properties": {
        "llm_model": { "type": "string" },
        "temperature": { "type": "number", "minimum": 0, "maximum": 1 },
        "tools_invoked": {
          "type": "array",
          "items": {
            "enum": ["search_normative", "get_rule_details",
                     "cite_legal_basis"]
          }
        },
        "tokens_input": { "type": "integer" },
        "tokens_output": { "type": "integer" }
      }
    }
  },
  "$defs": {
    "LegalCitation": {
      "type": "object",
      "required": ["norma_id", "texto_relevante"],
      "properties": {
        "norma_id": {
          "enum": [
            "LEY_17_2015", "RD_524_2023", "PLEGEM",
            "LEY_4_2007_CYL", "PLANCAL_DEC_4_2019",
            "LEY_11_2022", "REGISTRO_112_CYL",
            "RGPD", "LOPDGDD", "REG_UE_2024_1689",
            "INFOCAL_DEC_6_2025", "INUNCYL", "MPCYL_ACUERDO_3_2008", "RD_840_2015"
          ]
        },
        "articulo_o_seccion": { "type": "string" },
        "texto_relevante": { "type": "string", "maxLength": 300 },
        "url_oficial": { "type": "string", "format": "uri" }
      }
    }
  }
}
```

## Reglas semánticas

- Si `priority_recommended ∈ {P1, P2}`, `legal_citations` DEBE contener ≥1 entrada.
- Si `confidence_disclaimer` está presente, la UI DEBE mostrarlo con estilo destacado.
- `explanation_text` DEBE ser ≤ 120 palabras (límite blando: ≤ 1200 chars).
- `temperature` DEBE ser 0.0 para reproducibilidad (NFR-009).
- `tools_invoked` lista las tools MCP realmente llamadas durante la generación.

## Especificación de las 3 tools MCP (v0.1.0)

### `search_normative(query: str, top_k: int = 5) -> list[NormativeSnippet]`
Búsqueda semántica sobre el corpus normativo CyL vía ChromaDB.

### `get_rule_details(rule_id: str) -> RuleDetail`
Devuelve regla operativa completa con texto humano, sustento normativo y métricas históricas.

### `cite_legal_basis(priority: Priority, variables: list[str]) -> list[LegalCitation]`
Dado una prioridad y las variables que la activaron, devuelve las citas legales aplicables consultando la tabla de trazabilidad.

### `get_aemet_context(lat: float, lon: float, fecha: str) -> AemetContext` — **RESERVADA v0.2.0**
No implementada en v0.1.0 (decisión R-13). Reincorpora en v0.2.0 con AEMET histórico precargado offline.

## Tests obligatorios

1. Roundtrip.
2. Validación falla si P1 sin citas legales.
3. Validación falla si `temperature > 0` en modo producción.
4. Validación falla si `tools_invoked` contiene tool desconocida.
5. Validación falla si `explanation_text` < 20 chars o > 1200 chars.
