# Contratos — Capa 2 → Capa 3

**Contrato**: `PriorityRecommendation`
**Versión**: 0.1.0
**Productor**: `capa2_rulefit.inference` o `capa2_rulefit.baseline_expert`
**Consumidor**: `capa3_llm_mcp.explainer`

## JSON Schema (resumen normativo)

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://tfm-188/contracts/0.1.0/PriorityRecommendation.json",
  "title": "PriorityRecommendation",
  "type": "object",
  "required": [
    "incident_id",
    "priority_recommended",
    "probabilities",
    "activated_rules",
    "confidence_level",
    "model_used",
    "model_version_capa2",
    "requires_human_attention"
  ],
  "additionalProperties": false,
  "properties": {
    "incident_id": { "type": "string" },
    "priority_recommended": { "$ref": "#/$defs/Priority" },
    "probabilities": {
      "type": "object",
      "required": ["P1", "P2", "P3", "P4"],
      "properties": {
        "P1": { "type": "number", "minimum": 0, "maximum": 1 },
        "P2": { "type": "number", "minimum": 0, "maximum": 1 },
        "P3": { "type": "number", "minimum": 0, "maximum": 1 },
        "P4": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "activated_rules": {
      "type": "array",
      "items": { "$ref": "#/$defs/ActivatedRule" }
    },
    "confidence_level": { "enum": ["HIGH", "MEDIUM", "LOW", "UNKNOWN"] },
    "model_used": { "enum": ["RULEFIT", "BASELINE_EXPERT", "FALLBACK"] },
    "model_version_capa2": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "requires_human_attention": { "type": "boolean" },
    "inference_latency_ms": { "type": "number", "minimum": 0 }
  },
  "$defs": {
    "Priority": { "enum": ["P1", "P2", "P3", "P4"] },
    "ActivatedRule": {
      "type": "object",
      "required": ["rule_id", "human_text", "weight", "normative_anchors"],
      "properties": {
        "rule_id": { "type": "string" },
        "human_text": { "type": "string", "maxLength": 200 },
        "weight": { "type": "number" },
        "normative_anchors": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  }
}
```

## Invariantes lógicas

- `sum(probabilities.values()) == 1.0 ± 1e-6`.
- `priority_recommended == argmax(probabilities)`.
- `requires_human_attention == true` SI `confidence_level ∈ {LOW, UNKNOWN}` O `priority_recommended == "P1"`.
- Si `model_used == "RULEFIT"`, `len(activated_rules) ≤ 30` (Principio III + NFR-004).
- Si `priority_recommended ∈ {P1, P2}`, `len(activated_rules) ≥ 1` (toda prioridad alta debe justificarse).

## Mapeo confidence ↔ probabilidad

| Confidence | p_max |
|---|---|
| HIGH | ≥ 0,80 |
| MEDIUM | [0,60; 0,80) |
| LOW | [0,40; 0,60) |
| UNKNOWN | < 0,40 |

## Tests obligatorios

1. Roundtrip.
2. Validación falla si probabilidades no suman 1.
3. Validación falla si `priority_recommended ≠ argmax(probabilities)`.
4. Validación falla si RuleFit produce >30 reglas.
5. Validación falla si P1 sin reglas activadas.
