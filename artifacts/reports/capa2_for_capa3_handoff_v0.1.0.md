# Handoff Capa 2 -> Capa 3 v0.1.0

## Objetivo

Este documento congela la salida de Capa 2 para que Capa 3 pueda generar
explicaciones sin reinterpretar la decision de prioridad. Capa 2 decide y Capa 3
verbaliza, justifica y cita evidencias.

## Estado de Capa 2

- Version: `0.1.0`.
- Motor principal: `RuleFit-lite` cuando el artefacto `rulefit.joblib` esta
  disponible.
- Fallback interpretable: `BASELINE_EXPERT`, basado en reglas operativas
  auditables.
- Entrada oficial: `IncidentFeatures`, generado por Capa 1 determinista.
- Salida oficial: `PriorityRecommendation`.
- Endpoint integrado: `POST /predict`.

## Payload disponible para Capa 3

El endpoint `POST /predict` expone ahora dos bloques utiles:

### `priority_details`

Uso recomendado: UI, depuracion, metricas y trazabilidad tecnica.

Campos:

- `priority_recommended`: prioridad P1-P4.
- `probabilities`: distribucion completa P1-P4, siempre suma 1.
- `confidence_level`: `HIGH`, `MEDIUM`, `LOW` o `UNKNOWN`.
- `model_used`: `RULEFIT`, `BASELINE_EXPERT` o `FALLBACK`.
- `model_version_capa2`: version del motor de Capa 2.
- `requires_human_attention`: marca de supervision humana.
- `activated_rules`: reglas activadas con texto, peso y anclajes normativos.

### `explanation_context`

Uso recomendado: entrada directa para Brian/Capa 3.

Campos:

- `incident_id`: identificador trazable.
- `decision_source`: `capa2_rulefit_lite_v0.1.0`.
- `priority_recommended`: decision final de Capa 2.
- `probability_margin`: distancia entre la primera y la segunda prioridad.
- `probabilities`: distribucion completa P1-P4.
- `confidence_level`: nivel contractual de confianza.
- `activated_rules_summary`: resumen legible de las cinco reglas principales.
- `evidence`: evidencias completas hasta 30 reglas.
- `anti_leakage_status`: confirmacion de que el contrato runtime no usa columnas
  prohibidas por leakage.
- `warnings`: avisos como `requires_human_attention`,
  `low_probability_margin` o `no_activated_rules`.

## Regla de uso para Capa 3

Capa 3 no debe recalcular la prioridad. Debe tomar `priority_recommended` como
decision congelada de Capa 2 y construir la explicacion solo con:

- reglas activadas;
- probabilidades P1-P4;
- margen de probabilidad;
- evidencias de Capa 1 ya contenidas en `features`;
- normativa recuperada por RAG o herramientas MCP.

Si faltan evidencias o el margen es bajo, Capa 3 debe explicitar la incertidumbre
y recomendar revision humana, no inventar causas.

## Casos de referencia para Brian

Los casos reproducibles estan en
`artifacts/reports/capa1_capa2_e2e_v0.1.0.json` y
`artifacts/reports/capa1_capa2_e2e_v0.1.0.md`.

Casos base:

- `E2E-P1-ATRAPADO-INCENDIO`: incendio urbano con atrapados; prioridad esperada P1.
- `E2E-P1-TRAFICO-INCONSCIENTE`: trafico grave con inconsciencia y atrapamiento;
  prioridad aceptable P1/P2.
- `E2E-P1-QUIMICO-INTOXICACION`: fuga quimica con intoxicacion; prioridad
  aceptable P1/P2.
- `E2E-P2-INUNDACION`: inundacion sin victimas; prioridad no P1.
- `E2E-P3-INCIDENCIA-VIA`: incidencia vial sin victimas; prioridad P3/P4.

## Criterios de aceptacion

- `priority_details.probabilities` contiene exactamente P1, P2, P3 y P4.
- La prioridad recomendada coincide con el maximo de probabilidades.
- Los casos P1/P2 incluyen al menos una regla activada o cita minima posterior en
  Capa 3.
- `explanation_context` esta presente en todas las respuestas de `/predict`.
- Capa 3 conserva la prioridad de Capa 2 y no la sustituye por criterio LLM.
- Las columnas prohibidas por leakage no aparecen en el contrato runtime.

## Limitaciones

- El handoff no sustituye la evaluacion offline de Capa 2 sobre el dataset CyL.
- `RuleFit-lite` se mantiene como modelo seleccionado por equilibrio entre
  rendimiento, interpretabilidad y reproducibilidad.
- La validacion externa con personal 112 sigue pendiente.
- La calibracion fina ECE y variables AEMET/SNCZI/Seveso quedan como trabajo
  futuro.
