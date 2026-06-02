# Implementation Plan: Priorización temprana explicable de incidentes 112 CyL

**Branch**: `001-priorizacion-112-cyl` · **Date**: 2026-05-24 · **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-priorizacion-112-cyl/spec.md`

---

## Summary

DSS de tres capas para priorizar incidentes 112 en Castilla y León. **Capa 1** extrae variables operativas desde texto libre mediante reglas deterministas auditables en v0.1.0; los transformers quedan como línea futura si se dispone de checkpoint congelado y evaluado. **Capa 2** entrena RuleFit sobre etiqueta académica P1–P4 construida por supervisión débil, y se compara contra baseline experto y una ejecución diagnóstica de RuleFit canónico. **Capa 3** genera explicaciones con LLM local cuantizado, RAG sobre corpus normativo CyL y tool calling, y se expone como **servidor MCP** para integración con clientes externos. Coordinación entre capas mediante contratos Pydantic v2 versionados. Despliegue 100% on-premise sobre hardware del equipo.

## Technical Context

**Languages**: Python 3.11 (todas las capas + backend + scripts), Markdown/LaTeX (documento), opcional TypeScript/React (UI mínima)
**Primary Dependencies**:
- Capa 1: extractor determinista propio en `src/capa1_nlp`; `transformers`/`torch` quedan fuera del alcance v0.1.0.
- Capa 2: `imodels` (RuleFit), `scikit-learn`, `xgboost` (techo), `snorkel` o equivalente (weak supervision), `shap` (auditoría XGBoost)
- Capa 3: `llama-cpp-python` o `ollama` (LLM cuantizado), `chromadb` (vector store), `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`), `mcp` (Anthropic MCP SDK Python)
- Contratos: `pydantic>=2.5`, `polyfactory` (test fixtures)
- Backend: `fastapi`, `uvicorn`
- Eval: `scikit-learn`, `nltk` (Krippendorff α vía `krippendorff` o `simpledorff`), `mlflow` opcional

**Storage**:
- Dataset crudo: `resources/dataset/raw/`
- Dataset procesado: `resources/dataset/processed/`
- Splits versionados: `resources/dataset/splits/{train,val,test}.parquet`
- Modelos: `artifacts/models/{capa1,capa2,capa3}/v<semver>/`
- Logs de inferencia: SQLite local + ficheros JSONL rotados
- Vector store RAG: `artifacts/rag/chroma/`

**Testing**: `pytest`, `pytest-cov`, `hypothesis` (property-based para contratos), `polyfactory` (factories), `pytest-benchmark` (latencia)

**Target Platform**:
- Hardware: AMD Ryzen 9, 64 GB RAM, NVIDIA RTX 5070 8 GB VRAM
- OS: Windows 11 / Linux (Ubuntu 22.04 vía WSL2)
- LLM: cuantización Q4_K_M (ajuste ~5 GB VRAM), modelos candidatos: `Qwen2.5-7B-Instruct`, `Llama-3.1-8B-Instruct`

**Project Type**: Investigación + prototipo software (TFM grupal Tipo 2). Estructura monorepo con LaTeX y código.

**Performance Goals**:
- Capa 1+2: ≤ 500 ms p95 por incidente
- Capa 3 (con LLM y RAG): ≤ 2 s p95
- Throughput sostenido ≥ 30 incidentes/min en hardware objetivo

**Constraints**:
- Sin APIs cloud en producción (Principio VI)
- Sin uso de features post-decisión (Principio V)
- Sparsity RuleFit ≤30 reglas (NFR-004)
- Recall@P1 ≥ 0,85 (NFR-003)
- ECE ≤ 0,10 (NFR-002)

**Scale/Scope**:
- Dataset: 9380 incidentes etiquetados débilmente
- 15 variables operativas (V01–V15)
- 4 clases de prioridad (P1–P4)
- 4 tools MCP en Capa 3
- 3 contratos Pydantic principales

---

## Constitution Check

Verificación contra `.specify/memory/constitution.md` v1.0.0.

| Principio | Cumplimiento | Evidencia |
|---|---|---|
| I — Caso empírico real | ✅ | Dataset CyL 112 2008–2022, sin simulación |
| II — Supervisión humana | ✅ | Sin agente; output = recomendación; decisión final humana |
| III — Explicabilidad RuleFit | ✅ | RuleFit como núcleo; baseline experto + XGBoost como referencia |
| IV — Etiqueta P1–P4 académica | ✅ | Supervisión débil ≥3 anotadores; guía PLANCAL |
| V — No leakage | ✅ | `data-model.md` lista features excluidas; validación en CI |
| VI — Soberanía dato | ✅ | LLM local Q4_K_M; sin cloud APIs |
| VII — Trazabilidad normativa | ✅ | Tabla norma→variable→regla en `data-model.md` |
| VIII — Contratos antes que código | ✅ | `contracts/` con Pydantic; JSON Schema autogenerado |
| IX — Evaluación cuantitativa | ✅ | Quickstart + Cap. 9 con métricas obligatorias |
| X — Conformidad UE-IA | ✅ | Diseño alineado Anexo III; sin afirmación de certificación |

**Veredicto**: ✅ Plan conforme. Sin desviaciones constitucionales que justificar.

---

## Project Structure

### Documentation (TFM)

```
latex/
├── main.tex
├── bibliografia.bib
└── chapters/
    ├── chap0.tex … chap10.tex
    └── anexo_{a..m}.tex   # M nuevos: I (contratos), J (corpus RAG), K (prompts+tools), L (model cards), M (trazabilidad ext.)
```

### Source Code (prototipo)

```
src/
├── contracts/                    # Pydantic v2 contracts (paquete instalable)
│   ├── pyproject.toml
│   ├── contracts/
│   │   ├── __init__.py
│   │   ├── enums.py              # Priority, ConfidenceLevel, VariableSource
│   │   ├── incident_input.py     # entrada cruda del operador
│   │   ├── incident_features.py  # Capa 1 → Capa 2
│   │   ├── priority_recommendation.py  # Capa 2 → Capa 3
│   │   ├── operator_recommendation.py  # Capa 3 → UI
│   │   ├── rule.py               # regla operativa
│   │   ├── inference_log.py      # log auditable
│   │   └── errors.py
│   ├── tests/
│   └── docs/
│       ├── schemas/              # JSON Schema autogenerado (commit)
│       └── adr/
│           ├── 0001-pydantic-as-contract.md
│           ├── 0002-priority-scale-p1-p4-is-academic.md
│           ├── 0003-versioning-strategy.md
│           ├── 0004-no-leakage-policy.md
│           └── 0005-mcp-as-capa3-interface.md
│
├── capa1_nlp/                    # Ancor
│   ├── extraction/               # NER + multi-label V01..V15
│   ├── training/                 # fine-tune MarIA
│   ├── inference/                # API local in-process
│   └── tests/
│
├── capa2_rulefit/                # Juan Carlos
│   ├── weak_supervision/         # anotadores independientes + label model
│   ├── baseline_expert/          # reglas a batir
│   ├── rulefit/                  # entrenamiento + serialización
│   ├── xgboost_ceiling/          # techo opaco (no productivo)
│   ├── inference/
│   └── tests/
│
├── capa3_llm_mcp/                # Brian
│   ├── rag/                      # ingesta corpus normativo + chroma
│   ├── llm/                      # wrapper llama.cpp/ollama
│   ├── prompts/                  # system + few-shot
│   ├── mcp_server/               # servidor MCP con 4 tools
│   │   ├── server.py
│   │   └── tools/
│   │       ├── search_normative.py
│   │       ├── get_rule_details.py
│   │       ├── get_aemet_context.py
│   │       └── cite_legal_basis.py
│   └── tests/
│
├── backend/                      # transversal
│   ├── api/                      # FastAPI: /predict, /feedback, /healthz
│   ├── logging/                  # JSONL + SQLite
│   ├── orchestrator/             # encadena Capa 1 → 2 → 3 con SLA y fallback
│   └── tests/
│
└── ui/                           # opcional, mínima
    └── (Streamlit o React + Vite)

scripts/
├── clean_112_cyl.py              # ya existe
├── build_weak_labels.py
├── train_capa1.py
├── train_capa2.py
├── train_xgboost_ceiling.py
├── build_rag_index.py
├── run_evaluation.py
└── generate_model_cards.py

resources/
├── dataset/
│   ├── raw/
│   ├── processed/
│   ├── splits/
│   └── audit/
└── corpus_normativo/             # PDFs/HTML de las normas para RAG
```

### Structure Decision

Monorepo con dos raíces conceptuales: `latex/` (documento) y `src/` (prototipo). Los **contratos** (`src/contracts/`) son un paquete instalable independiente que las tres capas importan. Razón: permite trabajo paralelo entre los tres autores sin colisión (Principio VIII), facilita versionado semver y auto-generación de JSON Schema para CI diff.

---

## Phase 0 — Outline & Research

Salida: [research.md](./research.md)

Decisiones que requieren justificación documental:

1. **Extractor NLP español**: reglas deterministas auditables en v0.1.0; comparación MarIA (RoBERTa-bne) vs BETO vs XLM-RoBERTa diferida a trabajo futuro.
2. **Implementación RuleFit**: `imodels` vs Microsoft `InterpretML` vs implementación custom
3. **Framework de weak supervision**: Snorkel vs Cleanlab vs implementación custom con majority voting
4. **LLM local**: Qwen2.5-7B-Instruct Q4_K_M vs Llama-3.1-8B-Instruct Q4_K_M vs Mistral-7B
5. **Runtime LLM**: llama.cpp (vía `llama-cpp-python`) vs Ollama
6. **Vector store RAG**: ChromaDB vs Qdrant local vs FAISS
7. **Embeddings multilingües**: `paraphrase-multilingual-MiniLM-L12-v2` vs `bge-m3` vs `multilingual-e5-base`
8. **MCP SDK**: Python oficial Anthropic vs implementación manual
9. **Anti-leakage en CI**: validación automática vs manual
10. **Métrica acuerdo inter-anotador**: Krippendorff α vs Fleiss κ vs Cohen κ por pares
11. **Estrategia de splits**: aleatorio estratificado vs temporal vs por provincia
12. **Calibración**: Platt scaling vs isotonic regression vs temperature scaling

---

## Phase 1 — Design & Contracts

Salidas: [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

1. Extraer entidades de spec.md → `data-model.md` con esquema, validaciones, transiciones (incidente → features → recomendación → decisión).
2. Generar **contratos** en `contracts/` como esquemas JSON Schema y plantillas Pydantic.
3. Definir tests de contrato (roundtrip serialización, validación de invariantes, ejemplos golden) — fallarán hasta implementación.
4. Generar `quickstart.md` con escenario E2E (incidente real → recomendación P1 + explicación + decisión operador) ejecutable como integration test.

**Re-evaluación constitucional post-diseño**: ✅ pendiente confirmación tras Phase 1.

---

## Phase 2 — Task Planning Approach

Esta sección **describe** lo que hará el comando `/tasks`. **No** ejecuta tareas aún.

**Estrategia de generación**:
- Cargar plantilla base `.specify/templates/tasks-template.md` (si existe) o estructura estándar Spec Kit.
- Generar tareas desde Phase 1 artifacts:
  - Cada entidad de `data-model.md` → tarea de modelo Pydantic + tests [P]
  - Cada contrato en `contracts/` → tarea de schema + test golden [P]
  - Cada escenario de `quickstart.md` → integration test
  - Cada FR/NFR → tarea de implementación
- Marcar **[P]** las tareas que afectan ficheros distintos y son independientes (típicamente: contratos paralelos, módulos por capa).
- Orden TDD: contratos → tests fallando → implementación → tests verdes → integración.
- Orden de dependencias: contratos → Capa 1 + Capa 2 baseline en paralelo → Capa 2 RuleFit → Capa 3 → orquestador → UI → evaluación → redacción capítulos.

**Reparto por autor**:
- Ancor → tareas Capa 1
- Juan Carlos → tareas Capa 2 (weak supervision + RuleFit + baseline + XGBoost ceiling)
- Brian → tareas Capa 3 (RAG + LLM + MCP server) + orquestador + logs
- Conjunto → contratos, backend API, evaluación transversal, redacción

**Estimación**: ~75–95 tareas numeradas en `tasks.md`.

**IMPORTANTE**: Esta fase la ejecuta `/tasks`, no `/plan`.

---

## Phase 3+ — Future Implementation

Más allá del alcance de `/plan`:
- Phase 3: `/tasks` produce `tasks.md`
- Phase 4: implementación siguiendo `tasks.md` y la constitución
- Phase 5: validación E2E vía `quickstart.md`, evaluación Cap. 9, redacción final

---

## Complexity Tracking

Tabla solo si alguna desviación constitucional requiere justificación.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| _(ninguna por ahora)_ | _—_ | _—_ |

---

## Progress Tracking

**Phase Status**:
- [x] Phase 0: Research outlined (decisiones listadas, sin resolver)
- [x] Phase 1: Design outlined (data-model + contracts + quickstart pendientes de detalle)
- [x] Phase 2: Task planning approach described
- [ ] Phase 3: Tasks generated (`/tasks` command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check passed
- [ ] Post-Design Constitution Check (tras completar Phase 1)
- [x] All NEEDS CLARIFICATION resolved (Aragón, agente, LLM local)
- [x] Complexity deviations documented (ninguna)
