# Tasks â€” PriorizaciÃ³n 112 CyL

**Feature**: `001-priorizacion-112-cyl` Â· **Generated**: 2026-05-24 Â· **Last update**: 2026-05-27 (prototype v0.1.0 + memoria Juan Carlos)
**ConvenciÃ³n Spec Kit**:
- `T###` numeraciÃ³n correlativa.
- `[P]` = paralelizable (afecta ficheros distintos, sin dependencias con otras tareas en la misma oleada).
- Orden TDD: tests primero, luego implementaciÃ³n.
- Cada tarea referencia su artefacto fuente entre parÃ©ntesis.
- AsignaciÃ³n: `[A]` Ancor, `[J]` Juan Carlos, `[B]` Brian, `[C]` Conjunto.

> **Alcance v0.1.0** (R-13 en `research.md`): variables V01â€“V07, V12â€“V15 activas; V08â€“V11 (AEMET, INUNCYL/SNCZI, Seveso) diferidas. **3 tools MCP** (sin `get_aemet_context`). UI **Streamlit** Ãºnica. ValidaciÃ³n **interna** entre los 3 autores. Esto **reduce ~10 tareas** sin tocar el nÃºcleo NLP + RuleFit + LLM ni la constituciÃ³n.

---

## Fase 0 â€” Setup repositorio y constituciÃ³n

- [x] **T001** `[C]` Crear estructura `src/`, `scripts/`, `tests/`, `artifacts/`, `resources/corpus_normativo/` segÃºn `plan.md` Â§Project Structure.
- [x] **T002** `[C]` Inicializar `pyproject.toml` raÃ­z con `uv`/`hatch`, Python 3.11, lockfile reproducible.
- [x] **T003** `[C]` Configurar pre-commit: `ruff`, `black`, `mypy --strict` en `src/contracts/`, `pytest -q`.
- [x] **T004** `[C]` Configurar CI (GitHub Actions): tests + schema-diff + leakage-gate + coverage â‰¥80%.
- [x] **T005** `[C]` Crear `.specify/memory/amendments.log` vacÃ­o y `README.md` raÃ­z con enlace a constituciÃ³n.

## Fase 1 â€” Contratos (gate para todo lo demÃ¡s)

- [x] **T010** `[C]` Crear paquete `src/contracts/` con `pyproject.toml` instalable (`pip install -e ./src/contracts`).
- [x] **T011 [P]** `[C]` `src/contracts/contracts/enums.py`: `Priority`, `ConfidenceLevel`, `ModelUsed`, `VariableSource`, `ProvinciaCyL`, `CategoriaPreliminar`, `NormaID`.
- [x] **T012 [P]** `[C]` `src/contracts/contracts/incident_input.py` con tests `tests/test_incident_input.py` (validaciÃ³n lat/lon coherente, texto no vacÃ­o).
- [x] **T013 [P]** `[C]` `src/contracts/contracts/incident_features.py` (E-02) con `BoolWithConfidence`, `IntWithConfidence`, V01â€“V15, signals. Tests roundtrip + ejemplo golden.
- [x] **T014 [P]** `[C]` `src/contracts/contracts/priority_recommendation.py` (E-03) con `ActivatedRule`. Tests: sum probs == 1, argmax == recommended, â‰¤30 reglas si RULEFIT, P1/P2 requiere â‰¥1 regla.
- [x] **T015 [P]** `[C]` `src/contracts/contracts/operator_recommendation.py` (E-04) con `LegalCitation`. Tests: P1/P2 requiere â‰¥1 cita, explanation 20â€“1200 chars, temp 0.0 en producciÃ³n.
- [x] **T016 [P]** `[C]` `src/contracts/contracts/rule.py` (E-06) y `weak_label.py` (E-07).
- [x] **T017 [P]** `[C]` `src/contracts/contracts/inference_log.py` (E-08) con hash SHA-256 input.
- [x] **T018 [P]** `[C]` `src/contracts/contracts/errors.py`: `LeakageFieldRejectedError`, `LowConfidenceWarning`, `SLABreachWarning`, etc.
- [x] **T019** `[C]` Script `scripts/export_schemas.py` que dump JSON Schema de cada modelo a `src/contracts/docs/schemas/`.
- [x] **T020** `[C]` Test CI `tests/test_schema_diff.py` que compara schemas commiteados con regenerados y falla si difieren sin bump de versiÃ³n.
- [x] **T021** `[C]` Test CI `tests/test_leakage_gate.py` que escanea `src/capa1_nlp/` y `src/capa2_rulefit/` por referencias a columnas prohibidas (Principio V).
- [x] **T022 [P]** `[C]` ADR `src/contracts/docs/adr/0001-pydantic-as-contract.md`.
- [x] **T023 [P]** `[C]` ADR `0002-priority-scale-p1-p4-is-academic.md`.
- [x] **T024 [P]** `[C]` ADR `0003-versioning-strategy.md` (semver + schema diff CI).
- [x] **T025 [P]** `[C]` ADR `0004-no-leakage-policy.md`.
- [x] **T026 [P]** `[C]` ADR `0005-mcp-as-capa3-interface.md`.
- [x] **T027 [P]** `[C]` Factories en `src/contracts/tests/factories.py` con `polyfactory` para todos los modelos.

## Fase 2 â€” Dataset + weak supervision (Juan Carlos)

- [x] **T030** `[J]` Auditar dataset limpio `resources/dataset/processed/emergencias_112_cyl_2008_2022_clean.csv` y documentar nulos, duplicados, distribuciÃ³n por aÃ±o/provincia.
- [x] **T031** `[C]` Definir guÃ­a de etiquetado P1â€“P4 anclada en PLANCAL (Decreto 4/2019). Guardar en `latex/chapters/anexo_c.tex` y `resources/labeling_guide_p1p4.md`.
- [x] **T032** `[J]` Implementar `scripts/build_weak_labels.py`:
  - 4 anotadores independientes segÃºn R-03 (LLM-as-annotator, NER+intensificadores, clustering, reglas heurÃ­sticas con peso mÃ­nimo).
  - Label model con majority voting ponderado.
  - Output: `resources/dataset/processed/weak_labels_p1p4.csv` + JSONL + metrica Krippendorff alpha global y por anotador. Parquet queda diferido para no introducir dependencia opcional.
- [x] **T033** `[J]` Test: Î± global â‰¥ 0,67 (umbral aceptable).
- [x] **T034 [P]** `[J]` Implementar splits estratificados (anio + provincia + label) en `scripts/build_splits.py`. Output: `resources/dataset/splits/{train,val,test}.csv`.
- [x] **T035 [P]** `[J]` Implementar split temporal alternativo (â‰¤2020 train, 2021â€“22 test) en mismo script con flag `--temporal`.
- [x] **T036** `[J]` AblaciÃ³n anti-circularidad: entrenar label model **sin** la fuente "reglas heurÃ­sticas" y comparar distribuciÃ³n. Documentar en `research.md` apÃ©ndice.

## Fase 3 â€” Capa 1 NLP (Ancor)

- [x] **T040** `[A]` Crear `src/capa1_nlp/` con mÃ³dulos `extraction/`, `training/`, `inference/`, `tests/`.
- [x] **T041 [P]** `[A]` Test contrato: dado un texto golden, `extract_features()` devuelve `IncidentFeatures` vÃ¡lido (Pydantic).
- [x] **T042 [P]** `[A]` Test latencia: extracciÃ³n â‰¤ 500 ms p95 sobre 100 textos del test set.
- [x] **T043 [P]** `[A]` Test anti-leakage: el extractor no consume ninguna columna prohibida (lista del Principio V).
- [x] **T044** `[A]` Implementar extractor determinista de `signals` (regex + diccionarios lÃ©xicos) en `extraction/signal_extractor.py`.
- [ ] **T045** `[A]` Dataset HuggingFace para fine-tune NER + multi-label V01â€“V15 desde weak labels + anotaciones manuales mÃ­nimas (~200 ejemplos gold por variable crÃ­tica). **Diferido v0.2.0** si se mantiene Capa 1 determinista para v0.1.0.
- [ ] **T046** `[A]` `scripts/train_capa1.py`: fine-tune `roberta-base-bne` con cabeza multitarea. Persistir en `artifacts/models/capa1/v0.1.0/`. **Diferido v0.2.0**.
- [x] **T047** `[A]` Wrapper de inferencia `inference/feature_extractor.py` que combina seÃ±ales deterministas y produce `IncidentFeatures`.
- [x] **T048** `[A]` Reporte Capa 1 determinista v0.1.0 generado en `artifacts/reports/capa1_v0.1.0.json`; metricas NER/transformer quedan diferidas con T045-T046.
- [x] **T049** `[A]` Model card Capa 1 â†’ `latex/chapters/anexo_l.tex` (extractor determinista v0.1.0).

## Fase 4 â€” Capa 2 RuleFit + baseline + ceiling (Juan Carlos)

- [x] **T050** `[J]` Crear `src/capa2_rulefit/` con `weak_supervision/`, `baseline_expert/`, `rulefit/`, `xgboost_ceiling/`, `inference/`, `tests/`.
- [x] **T051 [P]** `[J]` Test contrato: dado `IncidentFeatures` vÃ¡lido, `predict()` devuelve `PriorityRecommendation` vÃ¡lido.
- [x] **T052 [P]** `[J]` Test invariantes: sum probs == 1, argmax == recommended, â‰¤30 reglas, P1 con â‰¥1 regla.
- [x] **T053** `[J]` Implementar `baseline_expert/expert_rules.py`: ~15 reglas a batir, basadas en seÃ±ales + V01..V15, con anclaje normativo en cada regla.
- [x] **T054** `[J]` `scripts/train_capa2.py` RuleFit:
  - RuleFit-lite seleccionado como motor v0.1.0 con 30 reglas activas.
  - Comparativa diagnostica con `imodels.RuleFitClassifier` documentada; la ejecucion completa puede repetirse si hay mas tiempo de computo.
  - Persistido en `artifacts/models/capa2/v0.1.0/rulefit.joblib` + `rules_lite.json`.
- [ ] **T055 [P]** `[J]` `scripts/train_xgboost_ceiling.py`: techo opaco con XGBoost + SHAP. Persistir en `artifacts/models/capa2/v0.1.0/xgb_ceiling.joblib`. **Marcar como no productivo** (banner en logs).
- [x] **T056** `[J]` Wrapper `inference/predictor.py` que selecciona RuleFit / baseline / fallback segÃºn disponibilidad.
- [x] **T057** `[J]` Reporte de mÃ©tricas Capa 2: F1 macro/por clase, recall@P1 (â‰¥0,85), sparsity y comparativa baseline experto vs RuleFit-lite vs `imodels` diagnostico. Artefactos activos: `artifacts/reports/rulefit_lite_v0.1.0.json`, `artifacts/reports/baseline_expert_v0.1.0.json`, `artifacts/reports/capa2_model_selection_v0.1.0.json`, `artifacts/reports/evaluation_v0.1.0.json`. ECE y XGBoost ceiling quedan como extension.
- [x] **T058** `[J]` Model card RuleFit + tabla de reglas activadas â†’ `anexo_e.tex` (baseline experto) + `anexo_l.tex` (model card RuleFit).

## Fase 5 â€” Corpus normativo + RAG (Brian)

- [~] **T060** `[C]` Recopilar PDFs/HTML oficiales de las 13 normas activas en `resources/corpus_normativo/`. **Progreso 11/13 fuentes indexadas en v0.1.0** Â· `INUNCYL` âœ… `BOCYL-D-03032010-14` (3 chunks, decreto + plan corto) Â· `MPCYL_ACUERDO_3_2008` âš ï¸ fuera del Ã­ndice activo al no disponer del plan tÃ©cnico completo en fuente oficial; queda pendiente su localizaciÃ³n documental Â· `REGISTRO_112_CYL` es ficha dataset (no PDF, no bloquea RAG). Total Ã­ndice actual: 1470 chunks, 11 normas.
- [x] **T061** `[B]` Pipeline ingesta: parser PDF â†’ chunking (~400 tokens, overlap 50) â†’ metadata `{norma_id, articulo, aÃ±o, jerarquÃ­a}`. Implementado en `src/capa3_llm_mcp/rag/ingestion.py`.
- [x] **T062** `[B]` `scripts/build_rag_index.py` con embeddings `paraphrase-multilingual-MiniLM-L12-v2` â†’ ChromaDB persistente en `artifacts/rag/chroma/`. âœ… 1467 chunks de 10 normas indexados.
- [x] **T063** `[B]` Test retrieval: query "atrapado herido grave" â†’ top-1 cita Ley 17/2015 art. 1. âœ… PASS.
- [x] **T064** `[B]` Test retrieval: query "fuga quÃ­mica camiÃ³n cisterna" â†’ top-1 en fallback quÃ­mico verificable de v0.1.0 (`PLANCAL_DEC_4_2019` / `INFOCAL_DEC_6_2025` / `LEY_17_2015`). âœ… PASS en `tests/test_rag_retrieval.py::test_t064_fuga_quimica_top1_verified_fallback_norma`.
- [x] **T065** `[B]` Documentar corpus en `latex/chapters/anexo_j.tex`. ✅ Anexo J creado e incluido en `latex/main.tex`.

## Fase 6 â€” Capa 3 LLM + MCP (Brian)

- [x] **T070** `[B]` Crear `src/capa3_llm_mcp/` con `rag/`, `llm/`, `prompts/`, `mcp_server/`, `tests/`. âœ… estructura completa.
- [x] **T071 [P]** `[B]` Test contrato: dado `PriorityRecommendation`, `explain()` devuelve `OperatorRecommendation` vÃ¡lido. âœ… 7 tests PASS (T071-A..G), incluyendo modo degradado.
- [x] **T072 [P]** `[B]` Test latencia: explicaciÃ³n â‰¤ 2 000 ms p95. âœ… 2 PASS (degradado + mock LLM), 1 SKIP (modelo real ausente).
- [x] **T073** `[B]` Wrapper LLM `llm/qwen_wrapper.py` actualizado a Ollama local con modelo `llama3.1:8b-instruct-q4_K_M` configurable por `OLLAMA_MODEL`. Temperature 0.0 / salida estructurada. El modo `llama-cpp`/Qwen queda sustituido para v0.1.0.
- [x] **T074** `[B]` Prompts en `prompts/`: system prompt + few-shot (3 ejemplos: P1, P3, P4). âœ…
- [x] **T075 [P]** `[B]` Tool `mcp_server/tools/search_normative.py`. âœ…
- [x] **T076 [P]** `[B]` Tool `mcp_server/tools/get_rule_details.py`. âœ…
- [ ] **~~T077~~** `[B]` ~~Tool `mcp_server/tools/get_aemet_context.py`~~ â€” **DIFERIDA v0.2.0 (R-13)**.
- [x] **T078 [P]** `[B]` Tool `mcp_server/tools/cite_legal_basis.py`. âœ…
- [x] **T079** `[B]` Servidor MCP `mcp_server/server.py` con las **3 tools v0.1.0** registradas, SSE `localhost:8765` + stdio mode. âœ…
- [x] **T080** `[B]` Test integraciÃ³n MCP: cliente test invoca cada tool y valida schema. âœ… 11 tests PASS.
- [x] **T081** `[B]` Wrapper `explainer.py` que orquesta LLM + tools + RAG y produce `OperatorRecommendation`. âœ…
- [x] **T082** `[B]` Modo degradado: si LLM no disponible, devolver explicaciÃ³n estÃ¡tica derivada de reglas activadas. âœ… `degraded_explain()` + garantÃ­a P1/P2â‰¥1 cita.
- [x] **T083** `[B]` Model card LLM + prompts â†’ Capa 3/Ollama documentada en `anexo_l.tex` y `anexo_k.tex` (prompts/tools) creada e incluida en `latex/main.tex`.

## Fase 7 â€” Backend + orquestador (Conjunto, lÃ­der Brian)

- [x] **T090** `[B]` `src/backend/api/` FastAPI con endpoints `/predict`, `/feedback`, `/healthz`, `/version`.
- [x] **T091** `[B]` `src/backend/orchestrator/pipeline.py` que encadena Capa 1 â†’ 2 â†’ 3 con timeouts y fallback degradado.
- [x] **T092** `[B]` `src/backend/logging/` con SQLite + JSONL rotado, persiste `InferenceLog`.
- [x] **T093** `[C]` Test integraciÃ³n endpoint `/predict` con Escenario 1 de quickstart.
- [x] **T094** `[C]` Test integraciÃ³n endpoint `/feedback` con Escenario 4.
- [x] **T095** `[C]` Test rechazo leakage Escenario 5.
- [x] **T096** `[C]` Test modo degradado Escenario 6.

## Fase 8 â€” UI mÃ­nima Streamlit (Conjunto, Q-01 cerrada)

- [x] **T100** `[C]` Decisión Q-01 cerrada: **Streamlit** (R-13). Sin alternativa React en v0.1.0.
- [x] **T101** `[C]` `src/ui/app.py`: formulario IncidentInput · badge P1–P4 · reglas activadas · citas normativas · pistas de actuación · panel operador aceptar/modificar/rechazar · historial de sesión.
- [~] **T102** `[C]` Capturas para `anexo_g.tex`. Anexo G ya preparado sin capturas definitivas; queda pendiente tomar e insertar imagenes reales de la interfaz.

## Fase 9 â€” EvaluaciÃ³n (Conjunto, lÃ­der Juan Carlos para ML; Brian para LLM)

- [x] **T110** `[J]` `scripts/run_evaluation.py` produce todas las mÃ©tricas obligatorias de Cap. 9 sobre test set y test temporal.
- [x] **T111** `[J]` AnÃ¡lisis de sesgo por provincia, aÃ±o y categorÃ­a â†’ tablas + figuras.
- [x] **T112** `[J]` Matriz de confusiÃ³n + anÃ¡lisis de errores en P1 (falsos negativos crÃ­ticos).
- [~] **T113** `[B]` EvaluaciÃ³n fidelidad explicaciones con **LLM-as-Judge** (Zheng et al., 2023): base offline v0.1.0 generada por `scripts/evaluate_explanation_fidelity.py` sobre 111 casos con juez determinista (`artifacts/reports/explanation_fidelity_v0.1.0.json`). Queda pendiente sustituir/contrastar con LLM-as-Judge independiente.
- [ ] **T114** `[C]` ValidaciÃ³n interna entre los 3 autores sobre â‰¥30 casos (Q-02 cerrada, R-13): cada autor etiqueta de forma independiente, se calcula Î± inter-anotador local y se documenta divergencia con el sistema. Plantilla en `anexo_d.tex`. **ValidaciÃ³n externa con personal del 112** queda como trabajo futuro documentado en Cap. 10.
- [ ] **T115** `[C]` Conformidad UE-IA: checklist Anexo III evaluada â†’ `anexo_m.tex` (trazabilidad extendida).
- [x] **T116** `[C]` Reporte final evaluaciÃ³n â†’ `artifacts/reports/evaluation_v0.1.0.json`, `artifacts/reports/final_evaluation_traceability_v0.1.0.json` y `latex/chapters/chap9.tex`.

## Fase 10 â€” RedacciÃ³n capÃ­tulos (LaTeX Scribe + autores)

- [x] **T120 [P]** `[C]` Actualizar `chap0.tex` (reparto + mÃ©tricas individuales).
- [x] **T121 [P]** `[C]` Reescribir `chap1.tex` (AragÃ³n â†’ CyL + frase-espina).
- [x] **T122 [P]** `[C]` Ampliar `chap2.tex` con nuevas secciones estado-arte (RuleFit, weak supervision, LLM locales, MCP, Reg. UE IA, ello incluye fix de `(?,?)` pÃ¡gs 19â€“22).
- [x] **T123** `[C]` Reescribir `chap3.tex` completo con marco normativo CyL + tabla de trazabilidad.
- [x] **T124 [P]** `[C]` Reformular `chap4.tex` con OG + OE1â€“OE8 y metodologia alineada con CyL, RuleFit-lite, LLM local y validacion interna.
- [x] **T125 [P]** `[C]` Actualizar `chap5.tex` con RF/RNF nuevos y restricciones de prototipo academico.
- [x] **T126** `[C]` Reescribir `chap6.tex` (3 capas reales).
- [x] **T127** `[J]` Reescribir `chap7.tex` (CyL + weak supervision + secciÃ³n anti-leakage).
- [x] **T128** `[C]` Escribir `chap8.tex` (prototipo: contratos, modulos, backend, interfaz, Ollama, smoke test P1--P4).
- [x] **T129** `[C]` Escribir `chap9.tex` (evaluacion con resultados reales offline e integrados).
- [x] **T130** `[C]` Escribir `chap10.tex` (conclusiones + trabajo futuro).
- [x] **T131 [P]** `[C]` Actualizar `anexo_a.tex` (taxonomia CyL), `anexo_b.tex` (variables V01â€“V15), `anexo_c.tex` (guia P1â€“P4), `anexo_d.tex` (validacion interna), `anexo_e.tex` (baseline experto), `anexo_f.tex` (esquema datos).
- [~] **T132 [P]** `[C]` Crear anexos nuevos: `anexo_g.tex` (capturas previstas) y `anexo_l.tex` (model cards) completados e incluidos. Pendientes si el alcance final los exige: `anexo_h.tex` (uso IA), `anexo_i.tex` (contratos Pydantic), `anexo_j.tex` (corpus RAG), `anexo_k.tex` (prompts+tools), `anexo_m.tex` (trazabilidad extendida).
  - Avance Juan Carlos: revisados y alineados `anexo_a.tex`, `anexo_b.tex`, `anexo_c.tex`, `anexo_d.tex`, `anexo_e.tex`, `anexo_g.tex` y `anexo_l.tex` con CyL, V01--V15, weak labels P1--P4, RuleFit-lite, anti-leakage, smoke test y validacion interna.
- [~] **T133** `[C]` Pase de coherencia cross-chapter ejecutado sobre memoria activa. Sin residuos de Aragon en `latex/chapters`; recursos Markdown antiguos bajo `latex/resources/` conservan borradores previos y no forman parte de `main.tex`.
- [ ] **T134** `[C]` BibliografÃ­a: aÃ±adir 2023â€“26 (RuleFit, Snorkel, MarIA, LLM-as-Judge, MCP, Reg. UE IA Anexo III) + 15 normas CyL â†’ `bibliografia.bib`.
- [~] **T135** `[C]` CompilaciÃ³n final `latexmk -pdf -outdir=build latex/main.tex` sin warnings crÃ­ticos. `pdflatex` compilo antes de incluir Anexo G; `latexmk` requiere Perl en MiKTeX y la recompilacion final tras Anexo G queda pendiente.

## Fase 11 â€” ValidaciÃ³n final

- [~] **T140** `[C]` Ejecutar `quickstart.md` completo â†’ smoke test integrado P1--P4 con Ollama ejecutado 4/4; quickstart completo 6/6 queda pendiente de pasada final.
- [ ] **T141** `[C]` Verificar checklist constitucional final.
- [ ] **T142** `[C]` Ensayo de defensa con tribunal simulado.
  - Avance parcial: auditoria final de consistencia documental ejecutada sobre memoria activa. Sin residuos de Aragon en `latex/chapters`, metricas actualizadas, artefactos principales regenerados (`evaluation_v0.1.0`, `explanation_fidelity_v0.1.0`, `final_evaluation_traceability_v0.1.0`, `prototype_v0.1.0_smoke_test`). Compilacion pendiente de repetir tras incluir `anexo_g.tex`.

---

## Dependencias crÃ­ticas

```mermaid
graph TD
    T010[Contratos T010-T027] --> T030[Dataset T030-T036]
    T010 --> T040[Capa1 T040-T049]
    T030 --> T050[Capa2 T050-T058]
    T040 --> T050
    T010 --> T060[RAG T060-T065]
    T050 --> T070[Capa3 T070-T083]
    T060 --> T070
    T050 --> T090[Backend T090-T096]
    T070 --> T090
    T090 --> T100[UI T100-T102]
    T090 --> T110[Eval T110-T116]
    T110 --> T120[RedacciÃ³n T120-T135]
    T120 --> T140[ValidaciÃ³n T140-T142]
```

## Resumen reparto

| Persona | Tareas principales | N |
|---|---|---|
| Ancor `[A]` | T040â€“T049 (Capa 1 NLP) | 10 |
| Juan Carlos `[J]` | T030â€“T036, T050â€“T058, T110â€“T112, T127 | 18 |
| Brian `[B]` | T060â€“T065, T070â€“T083, T090â€“T092, T113 | 22 |
| Conjunto `[C]` | T001â€“T027, T093â€“T102, T114â€“T116, T120â€“T142 | 50 |
| **Total** | | **~100** |
