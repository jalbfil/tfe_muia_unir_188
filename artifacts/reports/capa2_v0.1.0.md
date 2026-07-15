# Reporte Capa 2 v0.1.0

- Modelo seleccionado: rulefit_lite
- Macro-F1 test: 0.905604
- Recall P1 test: 0.909924
- Reglas activas exportadas: 30

## Comparativa Test

| Modelo | Accuracy | Macro-F1 | Recall P1 | Reglas | Train s | Infer ms/fila |
|---|---:|---:|---:|---:|---:|---:|
| baseline_expert | 0.694425 | 0.464284 | 0.998473 | 19 | None | None |
| rulefit_lite | 0.903648 | 0.905604 | 0.909924 | 30 | 6.504204 | 0.450127 |
| rulefit_imodels | 0.768385 | 0.568239 | 0.902778 | 30 | 13.191647 | 7.496081 |

## Checks

- Recall P1 minimo: 0.85
- Maximo reglas activas: 30
- ECE objetivo para calibracion posterior: 0.1

## Anti-Leakage

Only pre-decision textual signals and derived V01-V15 proxies are used.
Columnas prohibidas excluidas: MediosMov, medios_mov_limpio, medios_mov_uso_recomendado, PacientesAten, pacientes_aten_limpio, IncidenteCerrado, ultimaActualizacion, Enlace al contenido, Unnamed: 13
