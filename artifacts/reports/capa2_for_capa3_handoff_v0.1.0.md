# Handoff Capa 2 -> Capa 3 v0.1.0

Actualiza la rama `juancarlos` antes de empezar con Capa 3. Esta
rama contiene la integracion actualizada de Capa 1 y Capa 2, los reportes E2E y el endpoint `POST /predict` con el contexto preparado para explicaciones.

Este archivo resume lo que debes tener claro para avanzar:

- Capa 1 ya entrega variables operativas estructuradas en el contrato
  `IncidentFeatures`.
- Capa 2 ya decide la prioridad P1-P4 y devuelve probabilidades, reglas y
  evidencias.
- Capa 3 no debe recalcular la prioridad: debe explicar la decision de Capa 2,
  apoyarse en normativa/RAG/MCP y presentar el resultado al operador.

La idea central es: Capa 1 lee el incidente, Capa 2 prioriza y Capa 3
explica. El LLM ayuda a redactar y justificar, pero no sustituye al motor de priorizacion.

## Objetivo

Este documento congela la salida de Capa 2 para que Capa 3 pueda generar
explicaciones sin reinterpretar la decision de prioridad. Capa 2 decide y Capa 3
verbaliza, justifica y cita evidencias.

## Contexto de Capa 1

Capa 1 v0.1.0 se ha cerrado como extractor determinista. No se esta validando un
transformer ni un modelo neuronal en esta version. Su responsabilidad es tomar el
texto del incidente y convertirlo en variables operativas auditables:

- variables V01-V15 activas o diferidas segun alcance v0.1.0;
- senales textuales criticas: fallecido, herido grave, atrapado, intoxicacion,
  incendio, accidente de trafico, rescate, varias llamadas, inundacion y riesgo
  vital textual;
- control de negaciones para evitar falsos positivos como "no hay heridos" o "no
  hay atrapados";
- salida oficial `IncidentFeatures`.

Para Capa 3, `features` puede usarse como evidencia operativa adicional, pero no
como fuente para cambiar la prioridad.

## Estado de Capa 2

- Version: `0.1.0`.
- Motor principal: `RuleFit-lite` cuando el artefacto `rulefit.joblib` esta
  disponible.
- Fallback interpretable: `BASELINE_EXPERT`, basado en reglas operativas
  auditables.
- Entrada oficial: `IncidentFeatures`, generado por Capa 1 determinista.
- Salida oficial: `PriorityRecommendation`.
- Endpoint integrado: `POST /predict`.

## Que hace Capa 2

Capa 2 es el motor de priorizacion interpretable. Recibe las variables de Capa 1
y devuelve:

- prioridad recomendada P1-P4;
- probabilidades para P1, P2, P3 y P4;
- nivel de confianza;
- reglas o patrones activados;
- advertencia de supervision humana cuando procede;
- confirmacion de que no se usan columnas prohibidas por leakage.

La evaluacion de Capa 2 se ha planteado con rigor experimental:

- baseline experto como referencia interpretable minima;
- RuleFit-lite como modelo seleccionado por equilibrio entre rendimiento,
  trazabilidad y reproducibilidad;
- ejecucion diagnostica RuleFit/imodels para comparativa;
- evaluacion offline sobre weak labels P1-P4;
- validacion integrada Capa 1 -> Capa 2 -> Capa 3 degradada.

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

Ejemplo conceptual:

```json
{
  "explanation_context": {
    "priority_recommended": "P1",
    "probabilities": {"P1": 0.82, "P2": 0.14, "P3": 0.03, "P4": 0.01},
    "probability_margin": 0.68,
    "confidence_level": "HIGH",
    "activated_rules_summary": [
      "Riesgo vital textual detectado",
      "Persona atrapada o no accesible"
    ],
    "warnings": ["requires_human_attention"]
  }
}
```

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

## Como debe actuar Capa 3

Buenas practicas para Brian:

- Usar `explanation_context.priority_recommended` como prioridad final.
- Usar `explanation_context.probabilities` para explicar el grado de apoyo del
  modelo.
- Usar `explanation_context.probability_margin` para detectar casos frontera.
- Usar `explanation_context.evidence` y `activated_rules_summary` para justificar
  con reglas concretas.
- Usar `features` para mencionar senales operativas detectadas por Capa 1.
- Usar RAG/MCP para buscar soporte normativo y citas, no para cambiar la
  decision.

Comportamientos que se deben evitar:

- No recalcular P1-P4 con el LLM.
- No cambiar la prioridad si la explicacion "parece" sugerir otra cosa.
- No inventar reglas si `evidence` viene vacio.
- No ocultar incertidumbre cuando aparezca `low_probability_margin`.
- No presentar como validada una Capa 1 neuronal; en v0.1.0 Capa 1 es
  determinista.

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

## Validacion actual

- E2E Capa 1 -> Capa 2 -> Capa 3 degradada: `5/5`.
- Tests backend, Capa 2, baseline y E2E: `22 passed`.
- Modelo observado en la validacion integrada: `RULEFIT`.
- Ultimo commit de exposicion del contexto Capa 2 -> Capa 3:
  `d192f43 feat: expone contexto capa2 para capa3`.

## Criterios de aceptacion

- `priority_details.probabilities` contiene exactamente P1, P2, P3 y P4.
- La prioridad recomendada coincide con el maximo de probabilidades.
- Los casos P1/P2 incluyen al menos una regla activada o cita minima posterior en
  Capa 3.
- `explanation_context` esta presente en todas las respuestas de `/predict`.
- Capa 3 conserva la prioridad de Capa 2 y no la sustituye por criterio LLM.
- Las columnas prohibidas por leakage no aparecen en el contrato runtime.

## Checklist para empezar Capa 3

Antes de implementar nuevos prompts o flujos LLM:

- Confirmar que se esta trabajando sobre la rama `juancarlos` actualizada.
- Ejecutar `POST /predict` con al menos un caso P1 y revisar
  `explanation_context`.
- Verificar que Capa 3 lee `priority_recommended` desde `explanation_context`.
- Verificar que la explicacion incluye reglas/evidencias cuando existen.
- Verificar que P1/P2 incluye cita legal o fallback normativo.
- Verificar que el LLM no modifica la prioridad recomendada.
- Mantener `temperature=0.0` en modo productivo o demostracion controlada.

## Limitaciones

- El handoff no sustituye la evaluacion offline de Capa 2 sobre el dataset CyL.
- `RuleFit-lite` se mantiene como modelo seleccionado por equilibrio entre
  rendimiento, interpretabilidad y reproducibilidad.
- La validacion externa con personal 112 sigue pendiente.
- La calibracion fina ECE y variables AEMET/SNCZI/Seveso quedan como trabajo
  futuro.
