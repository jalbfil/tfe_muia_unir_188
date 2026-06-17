# Constitución del proyecto — TFM 188 MUIA UNIR

**Sistema inteligente de apoyo a la decisión para puestos de mando de emergencias**
Versión: 1.0.0 · Ratificada: 2026-05-24 · Última enmienda: 2026-05-24

Este documento contiene los principios **inmutables** del proyecto. Toda decisión técnica, narrativa o evaluativa debe ser coherente con ellos. Cualquier desviación requiere enmienda explícita y justificación en `research.md`.

---

## Principio I — Caso empírico real (no simulado)

El sistema se construye y evalúa sobre el **Registro de Emergencias del 112 de Castilla y León 2008–2022** (datos.gob.es, CC BY 4.0, n=9 380 registros válidos tras limpieza). Aragón queda relegado a una frase histórica. Se prohíben datasets sintéticos como evidencia principal; solo se permiten para pruebas unitarias o data augmentation justificada.

## Principio II — Supervisión humana obligatoria (no agente autónomo)

El sistema es un **DSS de recomendación**, no un agente. La salida es una sugerencia P1–P4 acompañada de explicación, reglas activadas, confianza y bases legales. La decisión final es siempre del operador 112. Esta restricción se justifica por el Reglamento (UE) 2024/1689, Anexo III, que clasifica los sistemas de priorización de llamadas de emergencia como **alto riesgo** y exige supervisión humana efectiva.

## Principio III — Explicabilidad por diseño (RuleFit como núcleo)

El modelo de priorización es **RuleFit** (Friedman & Popescu, 2008; implementación vía `imodels` o Microsoft InterpretML). Se compara obligatoriamente contra:
1. Un **baseline experto** basado en reglas (techo de interpretabilidad, suelo de rendimiento esperado).
2. Un **techo de rendimiento** opaco (XGBoost + SHAP) que sirve únicamente como referencia superior, nunca como modelo desplegable.

Quedan prohibidos como modelo principal: redes neuronales profundas opacas, ensembles sin restricción de sparsity, y cualquier modelo cuya predicción no pueda trazarse a reglas humanas legibles.

## Principio IV — Etiqueta académica P1–P4 (no oficial)

La escala P1–P4 **no existe en el dataset** y **no es oficial del 112 CyL**. Se construye mediante **supervisión débil** con ≥3 anotadores independientes y guía de etiquetado anclada en PLANCAL (Decreto 4/2019). Toda referencia a P1–P4 en el TFM debe incluir esta aclaración. Se evalúa acuerdo inter-anotador (Krippendorff α ≥ 0,67) y se hace ablación anti-circularidad para evitar que RuleFit reaprenda las reglas del anotador-reglas.

## Principio V — Prevención de fuga de información (no negociable)

Solo se usan como entrada al modelo variables disponibles en el **momento de la primera valoración**. Quedan **excluidas como features**, sin excepción:
- `MediosMov`, `medios_mov_*` (decisión post-priorización)
- `PacientesAten`, `pacientes_aten_*` (resultado clínico)
- `IncidenteCerrado` (estado final)
- `ultimaActualizacion` (cierre)

Estas columnas pueden usarse **únicamente** para validación ex-post de coherencia. La sección "Prevención de fuga de información" es obligatoria en el Cap. 7 y en `data-model.md`.

## Principio VI — Soberanía del dato (todo local)

Toda inferencia y entrenamiento se ejecuta **on-premise** sobre el hardware del equipo (RTX 5070 8GB VRAM, 64GB RAM, Ryzen 9). El LLM de explicación es cuantizado (Q4_K_M) y se invoca vía `llama.cpp` / `ollama`. Quedan prohibidos: APIs cloud de inferencia, fine-tuning en servicios externos, envío de datos 112 a terceros. Justificación: RGPD, LOPDGDD, Ley 11/2022 art. 74 (limitación de finalidad).

## Principio VII — Trazabilidad normativa → variable → regla

Toda variable del modelo y toda regla de RuleFit o del baseline debe poder mapearse a un criterio normativo concreto mediante la **tabla de trazabilidad** (Cap. 3 + Anexo M). Una variable sin anclaje normativo no entra al modelo.

## Principio VIII — Contratos antes que código

El trabajo paralelo entre las tres capas (NLP, RuleFit, LLM+MCP) se coordina mediante **contratos Pydantic v2** versionados (`src/contracts/`). Ninguna capa puede modificar la firma de salida sin bump de versión y ADR. JSON Schema se autogenera y se compara en CI (schema diff).

## Principio IX — Evaluación cuantitativa obligatoria

El Cap. 9 reporta, como mínimo: F1 macro, F1 por clase, recall@P1 (crítico: ≥0,85), ECE (≤0,10), sparsity de RuleFit (≤30 reglas activas), AUC, matriz de confusión, análisis de sesgo por provincia/año/categoría, fidelidad de explicaciones (LLM-as-Judge + panel experto ≥3 personas sobre ≥30 casos), y comparativa baseline-experto / RuleFit / XGBoost. Sin estas métricas no hay defensa.

## Principio X — Conformidad con Reglamento UE de IA (inspiración, no certificación)

El diseño incorpora las exigencias del Reglamento (UE) 2024/1689 para sistemas de alto riesgo: supervisión humana, gestión de riesgos, calidad de datos, trazabilidad, transparencia, robustez. Se evalúa el grado de conformidad en Cap. 9. **No se afirma "cumplimiento"** porque no hay despliegue real ni auditoría externa; se afirma **alineación de diseño**.

---

## Gobernanza

- Las enmiendas a esta constitución requieren consenso explícito de los tres autores y registro en `.specify/memory/amendments.log`.
- Cualquier `spec.md`, `plan.md` o `tasks.md` que entre en conflicto con un principio debe corregirse o, excepcionalmente, justificar la desviación en `research.md` bajo epígrafe "Desviación constitucional".
- Versionado semver: MAJOR = cambio de principio, MINOR = nuevo principio, PATCH = aclaración.
