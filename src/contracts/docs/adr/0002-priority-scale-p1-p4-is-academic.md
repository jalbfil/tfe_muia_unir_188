# ADR-0002 — La escala P1–P4 es una etiqueta académica derivada

- **Estado**: Aceptada
- **Fecha**: 2026-05-24
- **Principio constitucional**: IV (Etiquetado académico P1–P4 con weak supervision, α ≥ 0.67)

## Contexto

El dataset 112 Castilla y León 2008–2022 NO contiene una columna "prioridad operativa real" tal cual la usaría un CECOP. El sistema necesita una etiqueta de gravedad cuatripartita anclada en marco normativo (PLANCAL Decreto 4/2019, Ley 17/2015) para entrenar Capa 2.

Existe el riesgo de presentar P1–P4 como verdad operativa cuando en realidad es una **proxy académica** construida desde texto histórico.

## Decisión

- P1–P4 se define como una **etiqueta académica derivada por weak supervision** sobre el texto histórico.
- Producción de la etiqueta: ≥3 anotadores independientes (R-03: LLM-as-annotator, NER + intensificadores, clustering, reglas heurísticas) + label model con voto mayoritario ponderado.
- Validación de calidad: Krippendorff α global ≥ 0.67 sobre el dataset (T033).
- Toda referencia a P1–P4 en la memoria (Cap. 7, 8, 9) DEBE incluir la coletilla "etiqueta académica derivada".
- El sistema produce **recomendaciones**, nunca decisiones automáticas (Principio II).

## Consecuencias

**Positivas**

- Defensible ante el tribunal: no se reclama acceso al juicio operativo del CECOP de CyL.
- Compatible con UE-IA Anexo III (sistema de apoyo, no de decisión autónoma).
- Permite ablación anti-circularidad (T036): el label model debe seguir produciendo etiquetas razonables tras retirar la fuente "heurísticas".

**Negativas / mitigaciones**

- Generalización limitada al contexto académico. Mitigado documentando explícitamente en Cap. 10 (trabajo futuro: validación externa con personal del 112).
- Sesgo de fuente (LLM-as-annotator hereda sesgos del LLM). Mitigado con anotador heurístico independiente y reporte de α por fuente.

## Referencias

- `research.md` §R-03 (weak supervision)
- `data-model.md` E-07 (`WeakLabel`)
- Krippendorff (2018), *Content Analysis*
