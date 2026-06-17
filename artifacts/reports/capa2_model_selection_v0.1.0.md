# Seleccion de modelo Capa 2

- Generado: 2026-05-26T17:32:52.685478+00:00
- Modelo recomendado: rulefit_lite

## Comparativa

| Modelo | Disponible | Accuracy test | Macro-F1 test | Recall P1 | Reglas | Train s | Infer ms/fila |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_expert | True | 0.727835 | 0.703932 | 0.998457 | 16 | None | None |
| rulefit_lite | True | 0.885911 | 0.884163 | 0.938272 | 30 | 6.504204 | 0.450127 |
| rulefit_imodels | True | 0.768385 | 0.568239 | 0.902778 | 30 | 13.191647 | 7.496081 |

## Lectura

La comparativa prioriza macro-F1 en test, recall P1 y parsimonia. El motor imodels se ha ejecutado en entorno Python 3.12 aislado; si se incrementan filas/arboles, debe repetirse el reporte con los mismos splits.
