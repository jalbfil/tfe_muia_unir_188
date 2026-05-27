# Reporte final de evaluacion y trazabilidad v0.1.0

Generado: `2026-05-27T10:24:45.151342+00:00`

## Resumen ejecutivo

- Modelo seleccionado: RuleFit-lite
- Test estratificado: accuracy 0.8811, macro-F1 0.88075, recall P1 0.921296.
- Test temporal 2022: accuracy 0.884354, macro-F1 0.877594, recall P1 0.928767.
- Falsos negativos P1: 51 (P1->P2=32, P1->P3=19, P1->P4=0).
- Validacion interna: 111 casos, con 51 P1 falsos negativos y 60 casos equilibrados.
- Fidelidad explicativa offline: pass rate 1.0, media 0.958747, minima 0.925.

## Trazabilidad documental

| Documento | Papel en la evaluacion |
|---|---|
| `latex/chapters/chap9.tex` | Narrativa academica de resultados, sesgo, errores P1, validacion y fidelidad. |
| `latex/chapters/anexo_d.tex` | Plantilla y muestra real de validacion interna. |
| `latex/chapters/anexo_l.tex` | Model card de Capa 2 y fidelidad de Capa 3. |
| `latex/chapters/chap10.tex` | Conclusiones, limitaciones y trabajo futuro. |

## Inventario de artefactos

| Artefacto | Ruta | Bytes |
|---|---|---:|
| evaluation_json | `artifacts\reports\evaluation_v0.1.0.json` | 11607 |
| evaluation_markdown | `artifacts\reports\evaluation_v0.1.0.md` | 1301 |
| explanation_fidelity_json | `artifacts\reports\explanation_fidelity_v0.1.0.json` | 1642 |
| explanation_fidelity_markdown | `artifacts\reports\explanation_fidelity_v0.1.0.md` | 1146 |
| explanation_fidelity_cases | `artifacts\reports\explanation_fidelity_cases_v0.1.0.csv` | 49756 |
| internal_validation_sample | `resources\internal_validation\casos_revision_v0.1.0.csv` | 113125 |
| internal_validation_summary | `resources\internal_validation\casos_revision_v0.1.0.md` | 2388 |
| internal_validation_protocol | `resources\internal_validation\protocolo_validacion_interna.md` | 3472 |
| p1_error_analysis | `artifacts\reports\p1_error_analysis_v0.1.0.csv` | 21854 |
| bias_by_province | `artifacts\reports\bias_by_province_v0.1.0.csv` | 539 |
| bias_by_year | `artifacts\reports\bias_by_year_v0.1.0.csv` | 784 |
| bias_by_category | `artifacts\reports\bias_by_category_v0.1.0.csv` | 245 |
| capitulo_9 | `latex\chapters\chap9.tex` | 14688 |
| anexo_d | `latex\chapters\anexo_d.tex` | 6647 |
| anexo_l | `latex\chapters\anexo_l.tex` | 6427 |
| capitulo_10 | `latex\chapters\chap10.tex` | 8146 |
| final_traceability_json | `artifacts\reports\final_evaluation_traceability_v0.1.0.json` | 3729 |
| final_traceability_markdown | `artifacts\reports\final_evaluation_traceability_v0.1.0.md` | 2809 |

## Cierre

Este reporte es el indice maestro de evaluacion v0.1.0. La conformidad UE-IA extendida queda reservada para el Anexo M/T115, pero este documento ya enlaza los artefactos necesarios de metricas, sesgo, errores criticos, validacion interna y fidelidad explicativa.
