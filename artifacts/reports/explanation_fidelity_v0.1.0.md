# T113 - Evaluación de fidelidad de explicaciones

Generado: `2026-06-17T15:32:01.046211+00:00`

## Resultado global

- Casos evaluados: 119
- Pass rate: 1.0
- Fidelidad media: 0.957367
- Fidelidad mínima: 0.933333

## Por tipo de muestra

| Tipo | Casos | Pass rate | Fidelidad media |
|---|---:|---:|---:|
| balanced_p1 | 15 | 1.0 | 0.964286 |
| balanced_p2 | 15 | 1.0 | 0.956032 |
| balanced_p3 | 15 | 1.0 | 0.956889 |
| balanced_p4 | 15 | 1.0 | 0.971429 |
| critical_p1_false_negative | 59 | 1.0 | 0.952494 |

## Checks

- priority_alignment: la explicación menciona la prioridad recomendada por Capa 2.
- rule_traceability: incluye resumen de reglas cuando procede.
- signal_coverage: cubre las señales textuales principales.
- legal_traceability: P1/P2 incluyen citas legales.
- no_contradiction: no menciona otra prioridad incompatible.
- confidence_disclaimer: comunica cautela o modo degradado.

## Artefactos

- json: `artifacts\reports\explanation_fidelity_v0.1.0.json`
- markdown: `artifacts\reports\explanation_fidelity_v0.1.0.md`
- cases_csv: `artifacts\reports\explanation_fidelity_cases_v0.1.0.csv`
