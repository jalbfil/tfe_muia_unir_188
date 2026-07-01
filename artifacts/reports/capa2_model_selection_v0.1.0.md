# Seleccion de modelo Capa 2

- Generado: 2026-06-24T16:04:58.601837+00:00
- Modelo recomendado: rulefit_lite

## Comparativa

| Modelo | Disponible | Accuracy val | Macro-F1 val | Recall P1 val | Reglas | Train s | Infer ms/fila |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_expert | True | 0.717822 | 0.691811 | 1.0 | 16 | None | None |
| rulefit_lite | True | 0.881188 | 0.879592 | 0.9344 | 30 | 6.504204 | 0.450127 |
| rulefit_imodels | True | 0.78925 | 0.584768 | 0.9104 | 30 | 13.191647 | 7.496081 |

## Lectura

La seleccion prioriza macro-F1 y recall P1 en validacion, junto con la parsimonia. El conjunto de test se reserva para estimar el rendimiento final del modelo seleccionado. El motor imodels se ha ejecutado en entorno Python 3.12 aislado; si se incrementan filas/arboles, debe repetirse el reporte con los mismos splits.
