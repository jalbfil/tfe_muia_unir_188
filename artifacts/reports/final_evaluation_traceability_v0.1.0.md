# Reporte final de evaluación y trazabilidad v0.1.0

Generado: `2026-06-17T15:32:07.068751+00:00`

## Resumen ejecutivo

- Modelo seleccionado: RuleFit-lite
- Test estratificado: accuracy 0.903648, macro-F1 0.905604, recall P1 0.909924.
- Test temporal 2022: accuracy 0.884354, macro-F1 0.877594, recall P1 0.928767.
- Falsos negativos P1: 59 (P1->P2=34, P1->P3=18, P1->P4=7).
- Validación interna: 119 casos, con 59 P1 falsos negativos y 60 casos equilibrados.
- Fidelidad explicativa offline: pass rate 1.0, media 0.957367, mínima 0.933333.

## Trazabilidad documental

| Documento | Papel en la evaluación |
|---|---|
| `latex/chapters/chap9.tex` | Narrativa académica de resultados, sesgo, errores P1, validación y fidelidad. |
| `latex/chapters/anexo_d.tex` | Plantilla y muestra real de validación interna. |
| `latex/chapters/anexo_l.tex` | Model card de Capa 2 y fidelidad de Capa 3. |
| `latex/chapters/chap10.tex` | Conclusiones, limitaciones y trabajo futuro. |

## Inventario de artefactos

| Artefacto | Ruta | Bytes |
|---|---|---:|
| evaluation_json | `artifacts\reports\evaluation_v0.1.0.json` | 11606 |
| evaluation_markdown | `artifacts\reports\evaluation_v0.1.0.md` | 1306 |
| explanation_fidelity_json | `artifacts\reports\explanation_fidelity_v0.1.0.json` | 1641 |
| explanation_fidelity_markdown | `artifacts\reports\explanation_fidelity_v0.1.0.md` | 1154 |
| explanation_fidelity_cases | `artifacts\reports\explanation_fidelity_cases_v0.1.0.csv` | 53644 |
| internal_validation_sample | `resources\internal_validation\casos_revision_v0.1.0.csv` | 121018 |
| internal_validation_summary | `resources\internal_validation\casos_revision_v0.1.0.md` | 2379 |
| internal_validation_protocol | `resources\internal_validation\protocolo_validacion_interna.md` | 3548 |
| p1_error_analysis | `artifacts\reports\p1_error_analysis_v0.1.0.csv` | 25302 |
| bias_by_province | `artifacts\reports\bias_by_province_v0.1.0.csv` | 536 |
| bias_by_year | `artifacts\reports\bias_by_year_v0.1.0.csv` | 783 |
| bias_by_category | `artifacts\reports\bias_by_category_v0.1.0.csv` | 246 |
| capitulo_9 | `latex\chapters\chap9.tex` | 21359 |
| anexo_d | `latex\chapters\anexo_d.tex` | 6784 |
| anexo_l | `latex\chapters\anexo_l.tex` | 11759 |
| capitulo_10 | `latex\chapters\chap10.tex` | 13880 |
| final_traceability_json | `artifacts\reports\final_evaluation_traceability_v0.1.0.json` | 3737 |
| final_traceability_markdown | `artifacts\reports\final_evaluation_traceability_v0.1.0.md` | 2829 |

## Cierre

Este reporte es el índice maestro de evaluación v0.1.0. La conformidad UE-IA extendida queda reservada para el Anexo M/T115, pero este documento ya enlaza los artefactos necesarios de métricas, sesgo, errores críticos, validación interna y fidelidad explicativa.
