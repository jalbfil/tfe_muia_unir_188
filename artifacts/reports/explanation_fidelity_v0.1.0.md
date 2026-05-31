# T113 - Evaluacion de fidelidad de explicaciones

Generado: `2026-05-26T18:46:54.631816+00:00`

## Resultado global

- Casos evaluados: 111
- Pass rate: 1.0
- Fidelidad media: 0.958747
- Fidelidad minima: 0.925

## Por tipo de muestra

| Tipo | Casos | Pass rate | Fidelidad media |
|---|---:|---:|---:|
| balanced_p1 | 15 | 1.0 | 0.97381 |
| balanced_p2 | 15 | 1.0 | 0.956191 |
| balanced_p3 | 15 | 1.0 | 0.959302 |
| balanced_p4 | 15 | 1.0 | 0.971429 |
| critical_p1_false_negative | 51 | 1.0 | 0.951176 |

## Checks

- priority_alignment: la explicacion menciona la prioridad recomendada por Capa 2.
- rule_traceability: incluye resumen de reglas cuando procede.
- signal_coverage: cubre las senales textuales principales.
- legal_traceability: P1/P2 incluyen citas legales.
- no_contradiction: no menciona otra prioridad incompatible.
- confidence_disclaimer: comunica cautela o modo degradado.

## Artefactos

- json: `artifacts\reports\explanation_fidelity_v0.1.0.json`
- markdown: `artifacts\reports\explanation_fidelity_v0.1.0.md`
- cases_csv: `artifacts\reports\explanation_fidelity_cases_v0.1.0.csv`
