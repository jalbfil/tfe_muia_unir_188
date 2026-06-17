# Evaluación Capa 2 v0.1.0

Generado: `2026-06-17T15:28:22.840997+00:00`

## Resumen

| Split | Filas | Accuracy | Macro-F1 | Recall P1 |
|---|---:|---:|---:|---:|
| Test estratificado | 1453 | 0.903648 | 0.905604 | 0.909924 |
| Test temporal | 735 | 0.884354 | 0.877594 | 0.928767 |

## Matriz de confusión test estratificado

| Referencia / Prediccion | P1 | P2 | P3 | P4 |
|---|---:|---:|---:|---:|
| P1 | 596 | 34 | 18 | 7 |
| P2 | 37 | 302 | 10 | 0 |
| P3 | 0 | 31 | 341 | 3 |
| P4 | 0 | 0 | 0 | 74 |

## Falsos negativos P1

Total: 59; P1->P2: 34; P1->P3: 18; P1->P4: 7.

## Artefactos

- json: `artifacts\reports\evaluation_v0.1.0.json`
- markdown: `artifacts\reports\evaluation_v0.1.0.md`
- bias_by_province: `artifacts\reports\bias_by_province_v0.1.0.csv`
- bias_by_year: `artifacts\reports\bias_by_year_v0.1.0.csv`
- bias_by_category: `artifacts\reports\bias_by_category_v0.1.0.csv`
- figure_bias_by_province: `artifacts\reports\bias_by_province_v0.1.0.svg`
- figure_bias_by_year: `artifacts\reports\bias_by_year_v0.1.0.svg`
- figure_bias_by_category: `artifacts\reports\bias_by_category_v0.1.0.svg`
- figure_confusion_matrix: `artifacts\reports\confusion_matrix_rulefit_lite_v0.1.0.svg`
- p1_error_analysis: `artifacts\reports\p1_error_analysis_v0.1.0.csv`
