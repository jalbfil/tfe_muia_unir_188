# Evaluacion Capa 2 v0.1.0

Generado: `2026-05-26T18:02:48.910643+00:00`

## Resumen

| Split | Filas | Accuracy | Macro-F1 | Recall P1 |
|---|---:|---:|---:|---:|
| Test estratificado | 1455 | 0.8811 | 0.88075 | 0.921296 |
| Test temporal | 735 | 0.884354 | 0.877594 | 0.928767 |

## Matriz de confusion test estratificado

| Referencia / Prediccion | P1 | P2 | P3 | P4 |
|---|---:|---:|---:|---:|
| P1 | 597 | 32 | 19 | 0 |
| P2 | 38 | 278 | 13 | 7 |
| P3 | 0 | 60 | 333 | 4 |
| P4 | 0 | 0 | 0 | 74 |

## Falsos negativos P1

Total: 51; P1->P2: 32; P1->P3: 19; P1->P4: 0.

## Artefactos

- json: `artifacts\reports\evaluation_rulefit_alias_v0.1.0.json`
- markdown: `artifacts\reports\evaluation_rulefit_alias_v0.1.0.md`
- bias_by_province: `artifacts\reports\bias_by_province_v0.1.0.csv`
- bias_by_year: `artifacts\reports\bias_by_year_v0.1.0.csv`
- bias_by_category: `artifacts\reports\bias_by_category_v0.1.0.csv`
- p1_error_analysis: `artifacts\reports\p1_error_analysis_v0.1.0.csv`
