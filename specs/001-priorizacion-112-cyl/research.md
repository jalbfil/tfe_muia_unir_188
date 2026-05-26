# Research — Decisiones técnicas y alternativas evaluadas

**Feature**: `001-priorizacion-112-cyl` · **Updated**: 2026-05-24

Cada entrada sigue el formato Spec Kit: **Decision · Rationale · Alternatives considered**.

---

## R-01 Modelo NLP base en español (Capa 1)

- **Decision**: `PlanTL-GOB-ES/roberta-base-bne` (MarIA-base, ~125M params), fine-tuned con cabeza multitarea (NER + multi-label V01–V15).
- **Rationale**: entrenado sobre corpus en español del BNE (~570 GB), licencia abierta, cabe holgadamente en 8 GB VRAM tanto en train como inference, evidencia sólida en tareas de información de crisis en español (Lamsal et al., 2024).
- **Alternatives considered**:
  - **BETO** (`dccuchile/bert-base-spanish-wwm-cased`) — más antiguo, peor rendimiento general en benchmarks recientes.
  - **XLM-RoBERTa-base** — multilingüe; rendimiento competitivo pero peor adaptación a giros administrativos españoles.
  - **`bertin-project/bertin-roberta-base-spanish`** — alternativa válida; queda como plan B si MarIA da problemas.
  - **LLM-only zero-shot** — descartado por latencia y por dependencia de prompts frágiles para 15 variables.

## R-02 Implementación RuleFit (Capa 2)

- **Decision**: `imodels.RuleFitClassifier` (Microsoft InterpretML-compatible).
- **Rationale**: implementación moderna mantenida, integración limpia con scikit-learn, soporta sparsity control vía LASSO, expone reglas como objetos inspeccionables.
- **Alternatives considered**:
  - **`InterpretML` ExplainableBoostingClassifier** — excelente, pero no es RuleFit estrictamente; valdría como modelo secundario.
  - **Implementación custom** sobre `sklearn.ensemble.GradientBoostingClassifier` + Lasso — más control pero más superficie de bug y menos defendible académicamente.
  - **`skope-rules`** — descartado: orientado a anomaly detection, no a multiclase calibrada.

## R-03 Framework de weak supervision

- **Decision**: Implementación con **majority voting ponderado** + **label model tipo Snorkel** simplificado, con ≥4 fuentes:
  1. LLM-as-annotator (solo texto, sin acceso a categoría)
  2. NER de víctimas + intensificadores léxicos
  3. Clustering semántico (k-means sobre embeddings)
  4. Reglas heurísticas con peso mínimo
- **Rationale**: Snorkel completo es pesado y tiene API antigua; lo esencial (label model probabilístico) se puede reimplementar en ~200 líneas. Permite ablación anti-circularidad limpia (Principio IV).
- **Alternatives considered**:
  - **Snorkel completo** (`snorkel.labeling.MajorityLabelVoter` + `LabelModel`) — válido como fallback si la implementación custom no converge.
  - **Cleanlab** — más orientado a label noise correction sobre etiquetas ya existentes.
  - **Etiquetado manual exclusivo** — descartado: 9 380 registros × ≥3 anotadores = inviable con 3 personas en 4 meses.

## R-04 LLM local (Capa 3)

- **Decision (primaria)**: **Qwen2.5-7B-Instruct** en cuantización Q4_K_M (~4,7 GB VRAM).
- **Decision (alternativa)**: **Llama-3.1-8B-Instruct** Q4_K_M (~5,4 GB VRAM).
- **Rationale Qwen2.5-7B**: rendimiento muy competitivo en español, mejor en tool calling estructurado que Llama-3.1 en pruebas recientes, licencia permisiva (Apache 2.0 para 7B).
- **Rationale Llama-3.1-8B**: ecosistema MCP/tool calling más maduro, fallback fiable.
- **Alternatives considered**:
  - **Mistral-7B-Instruct-v0.3** — peor en español que Qwen; descartado.
  - **Phi-3-mini** — demasiado pequeño para tool calling fiable con 4 tools.
  - **Modelos 13B+** — no caben con margen en 8 GB VRAM cuantizados ni dejan presupuesto para context window y vector store en memoria.

## R-05 Runtime LLM

- **Decision**: `llama-cpp-python` con backend CUDA.
- **Rationale**: control fino de parámetros, integración Python directa, soporte tool calling vía grammar, no requiere demonio externo.
- **Alternatives considered**:
  - **Ollama** — más sencillo de instalar pero añade capa REST innecesaria y menos control de grammars. Útil para reproducibilidad del entorno del tribunal; queda como modo de demostración alternativo.
  - **vLLM / TGI** — orientados a producción multi-GPU; sobredimensionados.

## R-06 Vector store para RAG

- **Decision**: **ChromaDB** en modo persistente local.
- **Rationale**: zero-config, Python-native, cabe el corpus normativo entero (~50–80 MB de texto chunked) sin problemas, persiste en disco.
- **Alternatives considered**:
  - **Qdrant local** — más rápido pero requiere ejecutable separado; sobredimensionado.
  - **FAISS** — más rápido pero sin metadata filtering nativo; obligaría a capa wrapper.
  - **LanceDB** — moderno y compacto; opción válida si Chroma da problemas.

## R-07 Modelo de embeddings

- **Decision**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (~120 MB, 384 dims).
- **Rationale**: rápido en CPU, calidad suficiente para retrieval en corpus jurídico-administrativo en español, no consume VRAM (la VRAM se reserva para LLM y transformer Capa 1).
- **Alternatives considered**:
  - **`BAAI/bge-m3`** — mejor calidad pero 2,3 GB y 1024 dims; ocupa más RAM y reduce throughput.
  - **`intfloat/multilingual-e5-base`** — alternativa razonable; queda como plan B.

## R-08 SDK MCP

- **Decision**: SDK oficial de Anthropic `mcp` para Python.
- **Rationale**: estándar de facto, mantenido, compatible con Claude Desktop y otros clientes MCP, expone tools con JSON Schema.
- **Alternatives considered**:
  - **Implementación manual del protocolo** — innecesario reinventar.
  - **OpenAI Function Calling propietario** — no es MCP; descartado por Principio VI (independencia).

## R-09 Validación anti-leakage en CI

- **Decision**: Test automático que (a) carga lista de columnas prohibidas desde `data-model.md`, (b) inspecciona `IncidentFeatures` y datasets de entrenamiento, (c) falla CI si alguna feature prohibida aparece.
- **Rationale**: el Principio V es no negociable; convertirlo en gate automático elimina riesgo humano.
- **Alternatives considered**:
  - **Revisión manual en PR** — frágil y no escala con 3 autores.

## R-10 Acuerdo inter-anotador

- **Decision**: **Krippendorff α** sobre escala ordinal P1–P4.
- **Rationale**: maneja datos ordinales, missing data, número arbitrario de anotadores. Umbral aceptable α ≥ 0,67 (Krippendorff 2004); deseable ≥ 0,80.
- **Alternatives considered**:
  - **Fleiss κ** — solo nominal, ignora orden de P1–P4.
  - **Cohen κ por pares** — no escala bien con >2 anotadores; útil como métrica complementaria.

## R-11 Estrategia de splits

- **Decision**: split **estratificado por (año, provincia, etiqueta P)** con proporciones 70/15/15, semilla fija = 42.
- **Rationale**: el dataset cubre 2008–2022; un split temporal puro podría sesgar por evolución del lenguaje administrativo. Estratificar por año+provincia preserva distribución manteniendo robustez.
- **Alternatives considered**:
  - **Split temporal puro** (entrenar ≤2020, test 2021–2022) — defendible y se mantiene como **análisis complementario** en Cap. 9 (robustez a deriva).
  - **Random puro** — descartado: rompe estratificación.

## R-12 Calibración de probabilidades

- **Decision**: **isotonic regression** sobre validación (CV interno).
- **Rationale**: no-paramétrica, robusta a mal-calibración del modelo base, suele dar mejor ECE que Platt en multiclase.
- **Alternatives considered**:
  - **Platt scaling** — más estable con poco dato pero peor en multiclase desbalanceada.
  - **Temperature scaling** — diseñado para redes neuronales; para RuleFit aporta menos.

---

## Decisiones resueltas el 2026-05-24 (cierre de Q-01..Q-04)

| ID | Pregunta | Resolución | Justificación |
|---|---|---|---|
| Q-01 | Frontend mínimo | **Streamlit** confirmado | Permite interacción suficiente para defensa académica y demo con tribunal sin coste de frontend separado. React/Vite queda fuera del MVP. |
| Q-02 | Panel experto | **Validación interna entre los 3 autores como mínimo viable**; contacto con personal del 112 queda como validación externa diferida (no bloquea defensa). | Reduce dependencias externas; Cap. 9 reporta validación interna + plan de validación externa como trabajo futuro. |
| Q-03 | Enriquecimiento AEMET (V08–V09) | **Diferido a v0.2.0 / trabajo futuro** | Implica descarga histórica + cruce geoespacial + parser de avisos; suma complejidad sin ser imprescindible para demostrar el núcleo (NLP + RuleFit + LLM). |
| Q-04 | Análisis Seveso (V11) | **Diferido a v0.2.0 / trabajo futuro** | Requiere cartografía industrial CyL externa; el riesgo químico se cubre por señales textuales (`signal_intoxicacion`) y por la regla MPCyL. |

## R-13 Simplificación justificada del alcance v0.1.0

- **Decision**: Reducir el alcance del MVP eliminando enriquecimientos externos no esenciales y posponiéndolos a v0.2.0.
- **Cambios concretos**:
  - **Variables diferidas**: V08 (`aviso_aemet_nivel`), V09 (`condicion_meteorologica_adversa`), V10 (`en_zona_inundable_snczi`), V11 (`proximo_instalacion_seveso_km`). Se mantienen en el modelo de datos como **opcionales / `NO_DISPONIBLE`** pero no se entrenan ni se exponen en producción v0.1.0.
  - **Tools MCP**: pasamos de 4 a **3 tools** en v0.1.0 → `search_normative`, `get_rule_details`, `cite_legal_basis`. La tool `get_aemet_context` se reincorpora en v0.2.0.
  - **UI**: Streamlit único. Sin alternativa React.
  - **Panel experto externo**: diferido; v0.1.0 reporta validación interna.
  - **Variables centrales v0.1.0**: V01, V02, V03, V04, V05, V06, V07, V12, V13, V14, V15 + las 10 señales textuales. Suficientes para reglas de priorización P1–P4 ancladas en Ley 17/2015, RD 524/2023, PLEGEM, PLANCAL, INFOCAL, MPCyL, Ley 4/2007.
- **Rationale**:
  - **Riesgo de calendario**: defensa 22 abril 2026; AEMET + Seveso + panel externo añaden semanas que no se traducen en mejora del núcleo evaluable.
  - **Foco académico**: el aporte original es el **trío NLP + RuleFit + LLM/MCP con trazabilidad normativa**. AEMET/Seveso son features de contexto, no contribución central.
  - **Trazabilidad preservada**: la tabla de trazabilidad mantiene INUNCYL y RD 840/2015 como anclajes vigentes en marco normativo (Cap. 3) aunque las variables asociadas no se exploten todavía.
  - **No compromete constitución**: ningún principio (I–X) queda violado; Principio I sigue cumpliéndose con el registro 112 CyL real.
- **Reincorporación v0.2.0**: documentada como trabajo futuro en Cap. 10 y anexo M.
- **Alternatives considered**:
  - **Mantener alcance completo** — riesgo alto de no llegar a Cap. 9 con métricas sólidas.
  - **Cortar también RAG/LLM** — descartado: rompería el aporte principal (Capa 3 explicación normativa).

## Apendice T036 - Ablacion anti-circularidad weak supervision

- **Decision**: se ejecuta una ablacion sin la fuente `rules_heuristic` mediante `scripts/build_weak_labels.py --no-rules`.
- **Rationale**: la fuente de reglas estabiliza P1--P4, pero no debe ser la unica razon por la que el label model reproduce la logica experta. Comparar la distribucion final con y sin reglas permite detectar circularidad.
- **Artefactos**:
  - `resources/dataset/audit/weak_labels_report.json` y `.md`: ejecucion completa.
  - `resources/dataset/audit/weak_labels_ablation_no_rules.json` y `.md`: ejecucion sin reglas.
  - `resources/dataset/processed/weak_labels_p1p4.csv` y `.jsonl`: etiquetas debiles principales.
- **Criterio de aceptacion**: el acuerdo global debe mantener Krippendorff alpha >= 0.67 y la distribucion P1--P4 no debe colapsar a una sola clase. Si la ablacion cae por debajo del umbral, el Cap. 9 debe reportarlo como limite empirico.

## Apendice Capa 2 - Estudio comparativo RuleFit

- **Decision provisional**: seleccionar `rulefit_lite` como modelo Capa 2 v0.1.0 por equilibrio entre macro-F1, recall P1, velocidad e interpretabilidad.
- **Modelos comparados**:
  - `baseline_expert`: reglas expertas trazables.
  - `rulefit_lite`: reglas de arbol poco profundo + capa logistica escasa.
  - `rulefit_imodels`: `imodels.RuleFitClassifier` en one-vs-rest P1--P4.
- **Hallazgo**: en el entorno Python 3.12 aislado, `imodels` funciona pero resulta lento para el dataset completo; con ejecucion diagnostica reducida no supera a `rulefit_lite`.
- **Artefactos**:
  - `artifacts/reports/capa2_model_selection_v0.1.0.json` y `.md`.
  - `artifacts/reports/rulefit_lite_v0.1.0.json`.
  - `artifacts/reports/rulefit_imodels_v0.1.0.json`.
- **Criterio**: maximizar macro-F1 en test, mantener recall P1 alto y limitar reglas activas a 30 para cumplir NFR-004.
- **Trabajo futuro inmediato**: repetir `--engine imodels` con mas filas/arboles si se dispone de tiempo de computo suficiente, manteniendo los mismos splits para comparabilidad.
