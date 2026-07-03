# Validacion end-to-end Capa 1 -> Capa 2 -> Capa 3 degradada v0.1.0

- Generado: `2026-07-01T16:31:00.569958+00:00`
- Casos: `5`
- Casos OK: `5`
- Capa 2 usa RuleFit: `True`
- Modelo Capa 2 observado: `['RULEFIT']`
- Latencia media Capa 1 ms: `4.58844`
- Latencia media Capa 2 ms: `52.16898`

| Caso | Prioridad | Modelo C2 | OK | Senales clave |
|---|---:|---|---:|---|
| E2E-P1-ATRAPADO-INCENDIO | P1 | RULEFIT | si | signal_atrapado, signal_varias_llamadas, signal_incendio, riesgo_vital_textual |
| E2E-P1-TRAFICO-INCONSCIENTE | P1 | RULEFIT | si | signal_herido_grave, signal_atrapado, signal_accidente_trafico |
| E2E-P1-QUIMICO-INTOXICACION | P1 | RULEFIT | si | signal_intoxicacion, riesgo_vital_textual |
| E2E-P2-INUNDACION | P2 | RULEFIT | si | signal_meteo_inundacion |
| E2E-P3-INCIDENCIA-VIA | P3 | RULEFIT | si | signal_accidente_trafico |

## Interpretación

Esta prueba no sustituye la evaluación offline de Capa 2 sobre el dataset completo. Su objetivo es comprobar que la salida real de Capa 1 alimenta correctamente el motor de priorización y que la explicación degradada de Capa 3 conserva la trazabilidad mínima sin instalar el LLM.
