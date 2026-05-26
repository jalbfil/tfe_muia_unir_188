# Tasks â€” PriorizaciÃ³n 112 CyL

**Feature**: `001-priorizacion-112-cyl` Â· **Generated**: 2026-05-24 Â· **Last update**: 2026-05-24 (R-13 scope simplification)
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

- [ ] **T040** `[A]` Crear `src/capa1_nlp/` con mÃ³dulos `extraction/`, `training/`, `inference/`, `tests/`.
- [ ] **T041 [P]** `[A]` Test contrato: dado un texto golden, `extract_features()` devuelve `IncidentFeatures` vÃ¡lido (Pydantic).
- [ ] **T042 [P]** `[A]` Test latencia: extracciÃ³n â‰¤ 500 ms p95 sobre 100 textos del test set.
- [ ] **T043 [P]** `[A]` Test anti-leakage: el extractor no consume ninguna columna prohibida (lista del Principio V).
- [ ] **T044** `[A]` Implementar extractor determinista de `signals` (regex + diccionarios lÃ©xicos) en `extraction/signal_extractor.py`.
- [ ] **T045** `[A]` Dataset HuggingFace para fine-tune NER + multi-label V01â€“V15 desde weak labels + anotaciones manuales mÃ­nimas (~200 ejemplos gold por variable crÃ­tica).
- [ ] **T046** `[A]` `scripts/train_capa1.py`: fine-tune `roberta-base-bne` con cabeza multitarea. Persistir en `artifacts/models/capa1/v0.1.0/`.
- [ ] **T047** `[A]` Wrapper de inferencia `inference/feature_extractor.py` que combina seÃ±ales deterministas + transformer y produce `IncidentFeatures`.
- [ ] **T048** `[A]` Reporte de mÃ©tricas Capa 1: macro-F1 NER, F1 por variable V01â€“V15, latencia. Guardar en `artifacts/reports/capa1_v0.1.0.json`.
- [ ] **T049** `[A]` Model card Capa 1 â†’ `latex/chapters/anexo_l.tex` (secciÃ³n transformer).

## Fase 4 â€” Capa 2 RuleFit + baseline + ceiling (Juan Carlos)

- [x] **T050** `[J]` Crear `src/capa2_rulefit/` con `weak_supervision/`, `baseline_expert/`, `rulefit/`, `xgboost_ceiling/`, `inference/`, `tests/`.
- [x] **T051 [P]** `[J]` Test contrato: dado `IncidentFeatures` vÃ¡lido, `predict()` devuelve `PriorityRecommendation` vÃ¡lido.
- [x] **T052 [P]** `[J]` Test invariantes: sum probs == 1, argmax == recommended, â‰¤30 reglas, P1 con â‰¥1 regla.
- [x] **T053** `[J]` Implementar `baseline_expert/expert_rules.py`: ~15 reglas a batir, basadas en seÃ±ales + V01..V15, con anclaje normativo en cada regla.
- [x] **T054** `[J]` `scripts/train_capa2.py` RuleFit:
  - `imodels.RuleFitClassifier(max_rules=80, alpha=...)` con LASSO sparsity hasta â‰¤30 reglas activas.
  - CalibraciÃ³n isotonic en validaciÃ³n.
  - Persistir en `artifacts/models/capa2/v0.1.0/rulefit.joblib` + `rules.json`.
- [ ] **T055 [P]** `[J]` `scripts/train_xgboost_ceiling.py`: techo opaco con XGBoost + SHAP. Persistir en `artifacts/models/capa2/v0.1.0/xgb_ceiling.joblib`. **Marcar como no productivo** (banner en logs).
- [x] **T056** `[J]` Wrapper `inference/predictor.py` que selecciona RuleFit / baseline / fallback segÃºn disponibilidad.
- [x] **T057** `[J]` Reporte de mÃ©tricas Capa 2: F1 macro/por clase, recall@P1 (â‰¥0,85), ECE (â‰¤0,10), sparsity, AUC. Comparativa baseline vs RuleFit vs XGBoost. `artifacts/reports/capa2_v0.1.0.json`.
- [x] **T058** `[J]` Model card RuleFit + tabla de reglas activadas â†’ `anexo_e.tex` (baseline experto) + `anexo_l.tex` (model card RuleFit).

## Fase 5 â€” Corpus normativo + RAG (Brian)

- [~] **T060** `[C]` Recopilar PDFs/HTML oficiales de las 13 normas activas en `resources/corpus_normativo/`. **Progreso 12/13 PDFs** Â· `INUNCYL` âœ… `BOCYL-D-03032010-14` (3 chunks, decreto + plan corto) Â· `MPCYL_ACUERDO_3_2008` âš ï¸ solo decreto de aprobaciÃ³n indexado (3 chunks); el PDF del plan completo no estÃ¡ localizado en BOCYL â€” buscar en web ProtecciÃ³n Civil CyL Â· `REGISTRO_112_CYL` es ficha dataset (no PDF, no bloquea RAG). Total Ã­ndice: 1473 chunks, 12 normas.
- [x] **T061** `[B]` Pipeline ingesta: parser PDF â†’ chunking (~400 tokens, overlap 50) â†’ metadata `{norma_id, articulo, aÃ±o, jerarquÃ­a}`. Implementado en `src/capa3_llm_mcp/rag/ingestion.py`.
- [x] **T062** `[B]` `scripts/build_rag_index.py` con embeddings `paraphrase-multilingual-MiniLM-L12-v2` â†’ ChromaDB persistente en `artifacts/rag/chroma/`. âœ… 1467 chunks de 10 normas indexados.
- [x] **T063** `[B]` Test retrieval: query "atrapado herido grave" â†’ top-1 cita Ley 17/2015 art. 1. âœ… PASS.
- [~] **T064** `[B]` Test retrieval: query "fuga quÃ­mica camiÃ³n cisterna" â†’ top-1 cita MPCyL. **FAIL** â€” MPCYL indexado (3 chunks del decreto) pero el embedder recupera INFOCAL_DEC_6_2025 (score 0.46 vs MPCYL sin aparecer en top-5). El decreto no contiene vocabulario de mercancÃ­as peligrosas suficiente. Requiere localizar el PDF del plan tÃ©cnico completo.
- [ ] **T065** `[B]` Documentar corpus en `latex/chapters/anexo_j.tex`.

## Fase 6 â€” Capa 3 LLM + MCP (Brian)

- [x] **T070** `[B]` Crear `src/capa3_llm_mcp/` con `rag/`, `llm/`, `prompts/`, `mcp_server/`, `tests/`. âœ… estructura completa.
- [x] **T071 [P]** `[B]` Test contrato: dado `PriorityRecommendation`, `explain()` devuelve `OperatorRecommendation` vÃ¡lido. âœ… 7 tests PASS (T071-A..G), incluyendo modo degradado.
- [x] **T072 [P]** `[B]` Test latencia: explicaciÃ³n â‰¤ 2 000 ms p95. âœ… 2 PASS (degradado + mock LLM), 1 SKIP (modelo real ausente).
- [x] **T073** `[B]` Wrapper LLM `llm/qwen_wrapper.py` con `llama-cpp-python`, modelo `qwen2.5-7b-instruct-q4_k_m.gguf` en `artifacts/llm/`. Temperature 0.0. âœ… `artifacts/llm/README.md` incluye instrucciones de descarga.
- [x] **T074** `[B]` Prompts en `prompts/`: system prompt + few-shot (3 ejemplos: P1, P3, P4). âœ…
- [x] **T075 [P]** `[B]` Tool `mcp_server/tools/search_normative.py`. âœ…
- [x] **T076 [P]** `[B]` Tool `mcp_server/tools/get_rule_details.py`. âœ…
- [ ] **~~T077~~** `[B]` ~~Tool `mcp_server/tools/get_aemet_context.py`~~ â€” **DIFERIDA v0.2.0 (R-13)**.
- [x] **T078 [P]** `[B]` Tool `mcp_server/tools/cite_legal_basis.py`. âœ…
- [x] **T079** `[B]` Servidor MCP `mcp_server/server.py` con las **3 tools v0.1.0** registradas, SSE `localhost:8765` + stdio mode. âœ…
- [x] **T080** `[B]` Test integraciÃ³n MCP: cliente test invoca cada tool y valida schema. âœ… 11 tests PASS.
- [x] **T081** `[B]` Wrapper `explainer.py` que orquesta LLM + tools + RAG y produce `OperatorRecommendation`. âœ…
- [x] **T082** `[B]` Modo degradado: si LLM no disponible, devolver explicaciÃ³n estÃ¡tica derivada de reglas activadas. âœ… `degraded_explain()` + garantÃ­a P1/P2â‰¥1 cita.
- [ ] **T083** `[B]` Model card LLM + prompts â†’ `anexo_l.tex` (secciÃ³n LLM) y `anexo_k.tex`.

## Fase 7 â€” Backend + orquestador (Conjunto, lÃ­der Brian)

- [x] **T090** `[B]` `src/backend/api/` FastAPI con endpoints `/predict`, `/feedback`, `/healthz`, `/version`.
- [x] **T091** `[B]` `src/backend/orchestrator/pipeline.py` que encadena Capa 1 â†’ 2 â†’ 3 con timeouts y fallback degradado.
- [x] **T092** `[B]` `src/backend/logging/` con SQLite + JSONL rotado, persiste `InferenceLog`.
- [x] **T093** `[C]` Test integraciÃ³n endpoint `/predict` con Escenario 1 de quickstart.
- [x] **T094** `[C]` Test integraciÃ³n endpoint `/feedback` con Escenario 4.
- [x] **T095** `[C]` Test rechazo leakage Escenario 5.
- [x] **T096** `[C]` Test modo degradado Escenario 6.

## Fase 8 â€” UI mÃ­nima Streamlit (Conjunto, Q-01 cerrada)

- [x] **T100** `[C]` DecisiÃ³n Q-01 cerrada: **Streamlit** (R-13). Sin alternativa React en v0.1.0.
- [ ] **T101** `[C]` Implementar UI Streamlit `src/ui/app.py`: formulario incidente + visualizaciÃ³n recomendaciÃ³n + reglas activadas + explicaciÃ³n + acciÃ³n aceptar/modificar/rechazar.
- [ ] **T102** `[C]` Capturas para `anexo_g.tex`.

## Fase 9 â€” EvaluaciÃ³n (Conjunto, lÃ­der Juan Carlos para ML; Brian para LLM)

- [x] **T110** `[J]` `scripts/run_evaluation.py` produce todas las mÃ©tricas obligatorias de Cap. 9 sobre test set y test temporal.
- [x] **T111** `[J]` AnÃ¡lisis de sesgo por provincia, aÃ±o y categorÃ­a â†’ tablas + figuras.
- [x] **T112** `[J]` Matriz de confusiÃ³n + anÃ¡lisis de errores en P1 (falsos negativos crÃ­ticos).
- [ ] **T113** `[B]` EvaluaciÃ³n fidelidad explicaciones con **LLM-as-Judge** (Zheng et al., 2023): juez independiente puntÃºa coherencia explicaciÃ³nâ†”reglas sobre â‰¥100 casos.
- [ ] **T114** `[C]` ValidaciÃ³n interna entre los 3 autores sobre â‰¥30 casos (Q-02 cerrada, R-13): cada autor etiqueta de forma independiente, se calcula Î± inter-anotador local y se documenta divergencia con el sistema. Plantilla en `anexo_d.tex`. **ValidaciÃ³n externa con personal del 112** queda como trabajo futuro documentado en Cap. 10.
- [ ] **T115** `[C]` Conformidad UE-IA: checklist Anexo III evaluada â†’ `anexo_m.tex` (trazabilidad extendida).
- [ ] **T116** `[C]` Reporte final evaluaciÃ³n â†’ `artifacts/reports/evaluation_v0.1.0.json` y `latex/chapters/chap9.tex`.

## Fase 10 â€” RedacciÃ³n capÃ­tulos (LaTeX Scribe + autores)

- [x] **T120 [P]** `[C]` Actualizar `chap0.tex` (reparto + mÃ©tricas individuales).
- [x] **T121 [P]** `[C]` Reescribir `chap1.tex` (AragÃ³n â†’ CyL + frase-espina).
- [x] **T122 [P]** `[C]` Ampliar `chap2.tex` con nuevas secciones estado-arte (RuleFit, weak supervision, LLM locales, MCP, Reg. UE IA, ello incluye fix de `(?,?)` pÃ¡gs 19â€“22).
- [x] **T123** `[C]` Reescribir `chap3.tex` completo con marco normativo CyL + tabla de trazabilidad.
- [ ] **T124 [P]** `[C]` Reformular `chap4.tex` con OG + OE1â€“OE4.
- [ ] **T125 [P]** `[C]` Actualizar `chap5.tex` con RF/RNF nuevos.
- [x] **T126** `[C]` Reescribir `chap6.tex` (3 capas reales).
- [x] **T127** `[J]` Reescribir `chap7.tex` (CyL + weak supervision + secciÃ³n anti-leakage).
- [ ] **T128** `[C]` Escribir `chap8.tex` (prototipo: contratos, mÃ³dulos, MCP, despliegue).
- [ ] **T129** `[C]` Escribir `chap9.tex` (evaluaciÃ³n con resultados reales).
- [ ] **T130** `[C]` Escribir `chap10.tex` (conclusiones + trabajo futuro).
- [ ] **T131 [P]** `[C]` Actualizar `anexo_a.tex` (taxonomÃ­a CyL), `anexo_b.tex` (variables V01â€“V15), `anexo_c.tex` (guÃ­a P1â€“P4), `anexo_d.tex` (plantilla + 20 casos), `anexo_e.tex` (baseline experto), `anexo_f.tex` (esquema datos).
- [ ] **T132 [P]** `[C]` Crear anexos nuevos: `anexo_g.tex` (capturas), `anexo_h.tex` (uso IA), `anexo_i.tex` (contratos Pydantic), `anexo_j.tex` (corpus RAG), `anexo_k.tex` (prompts+tools), `anexo_l.tex` (model cards), `anexo_m.tex` (trazabilidad extendida).
- [ ] **T133** `[C]` Pase de coherencia cross-chapter por LaTeX Scribe.
- [ ] **T134** `[C]` BibliografÃ­a: aÃ±adir 2023â€“26 (RuleFit, Snorkel, MarIA, LLM-as-Judge, MCP, Reg. UE IA Anexo III) + 15 normas CyL â†’ `bibliografia.bib`.
- [ ] **T135** `[C]` CompilaciÃ³n final `latexmk -pdf -outdir=build latex/main.tex` sin warnings crÃ­ticos.

## Fase 11 â€” ValidaciÃ³n final

- [ ] **T140** `[C]` Ejecutar `quickstart.md` completo â†’ 6/6 escenarios verdes.
- [ ] **T141** `[C]` Verificar checklist constitucional final.
- [ ] **T142** `[C]` Ensayo de defensa con tribunal simulado.

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
