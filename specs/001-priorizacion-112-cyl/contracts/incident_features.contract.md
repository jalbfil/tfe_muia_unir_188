# Contratos — Capa 1 → Capa 2

**Contrato**: `IncidentFeatures`
**Versión**: 0.1.0
**Productor**: `capa1_nlp.inference`
**Consumidor**: `capa2_rulefit.inference` (y baseline experto)

## JSON Schema (resumen normativo)

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://tfm-188/contracts/0.1.0/IncidentFeatures.json",
  "title": "IncidentFeatures",
  "type": "object",
  "required": [
    "incident_id",
    "variables_operativas",
    "signals",
    "model_version_capa1",
    "inference_timestamp",
    "inference_latency_ms"
  ],
  "additionalProperties": false,
  "properties": {
    "incident_id": { "type": "string", "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$" },

    "variables_operativas": {
      "type": "object",
      "required": ["V01", "V02", "V03", "V04", "V05", "V06", "V07", "V08", "V09",
                   "V10", "V11", "V12", "V13", "V14", "V15"],
      "additionalProperties": false,
      "properties": {
        "V01": { "$ref": "#/$defs/BoolWithConfidence" },
        "V02": { "$ref": "#/$defs/IntWithConfidence" },
        "V03": { "$ref": "#/$defs/EnumLesiones" },
        "V04": { "$ref": "#/$defs/EnumTipoIncidente" },
        "V05": { "$ref": "#/$defs/BoolWithConfidence" },
        "V06": { "type": "integer", "minimum": 1 },
        "V07": { "$ref": "#/$defs/BoolWithConfidence" },
        "V08": { "$ref": "#/$defs/EnumAemet" },
        "V09": { "$ref": "#/$defs/BoolWithConfidence" },
        "V10": { "type": "boolean" },
        "V11": { "type": "number", "minimum": 0 },
        "V12": { "$ref": "#/$defs/BoolWithConfidence" },
        "V13": { "$ref": "#/$defs/BoolWithConfidence" },
        "V14": { "type": "integer", "minimum": 0 },
        "V15": { "$ref": "#/$defs/EnumAccesibilidad" }
      }
    },

    "signals": {
      "type": "object",
      "required": [
        "signal_fallecido", "signal_herido_grave", "signal_atrapado",
        "signal_intoxicacion", "signal_varias_llamadas", "signal_incendio",
        "signal_accidente_trafico", "signal_rescate", "signal_meteo_inundacion",
        "riesgo_vital_textual"
      ],
      "additionalProperties": false,
      "patternProperties": {
        "^signal_[a-z_]+$": { "$ref": "#/$defs/BoolWithConfidence" },
        "^riesgo_vital_textual$": { "$ref": "#/$defs/BoolWithConfidence" }
      }
    },

    "model_version_capa1": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "inference_timestamp": { "type": "string", "format": "date-time" },
    "inference_latency_ms": { "type": "number", "minimum": 0 },
    "extractor_warnings": { "type": "array", "items": { "type": "string" } }
  },

  "$defs": {
    "BoolWithConfidence": {
      "type": "object",
      "required": ["value", "confidence"],
      "properties": {
        "value": { "type": "boolean" },
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "IntWithConfidence": {
      "type": "object",
      "required": ["value", "confidence"],
      "properties": {
        "value": { "type": "integer", "minimum": -1, "maximum": 50 },
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "EnumLesiones": {
      "type": "object",
      "required": ["value", "confidence"],
      "properties": {
        "value": { "enum": ["NINGUNA", "LEVE", "MODERADA", "GRAVE", "CRITICA", "DESCONOCIDA"] },
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "EnumTipoIncidente": {
      "type": "string",
      "enum": [
        "ACCIDENTE_TRAFICO", "INCENDIO_URBANO", "INCENDIO_FORESTAL",
        "SANITARIO", "RESCATE", "MERCANCIAS_PELIGROSAS", "METEOROLOGIA",
        "INFRAESTRUCTURA", "SEGURIDAD_CIUDADANA", "OTROS"
      ]
    },
    "EnumAemet": {
      "type": "string",
      "enum": ["VERDE", "AMARILLO", "NARANJA", "ROJO", "NO_DISPONIBLE"]
    },
    "EnumAccesibilidad": {
      "type": "string",
      "enum": ["ALTA", "MEDIA", "BAJA", "DESCONOCIDA"]
    }
  }
}
```

## Reglas de validación adicionales

- Si `V01.value == true` y `V03.value == "NINGUNA"`, emitir `extractor_warnings: ["inconsistency_v01_v03"]` (no rechazar; permitir auditoría).
- Si `inference_latency_ms > 500`, registrar evento `SLA_BREACH_CAPA1` (no rechazar).

## Compatibilidad

- Cambios MINOR: añadir señales nuevas detrás de pattern `signal_*` (consumidores deben ignorar desconocidas).
- Cambios MAJOR: modificación o eliminación de V01–V15, cambio de enum existente.

## Tests obligatorios (TDD)

1. Roundtrip JSON ↔ Pydantic instancia idéntica.
2. Validación falla con `V06 = 0`.
3. Validación falla con `confidence > 1`.
4. Ejemplo golden P1 (accidente con atrapado + herido grave) carga sin errores.
5. Ejemplo golden P4 (árbol caído sin afectados) carga sin errores.
