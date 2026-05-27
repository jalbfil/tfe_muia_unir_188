# ADR-0004 — Política no-leakage como gate de CI

- **Estado**: Aceptada
- **Fecha**: 2026-05-24
- **Principio constitucional**: V (No leakage temporal)

## Contexto

El dataset 112 CyL contiene columnas que solo existen **después** de que el operador haya tomado la decisión: `MediosMov` (recursos movilizados), `PacientesAten` (pacientes atendidos), `IncidenteCerrado` (estado administrativo), `ultimaActualizacion`. Usar cualquiera de ellas como feature haría que el modelo aprendiese a "predecir" lo que ya pasó — un caso de libro de target leakage que invalidaría todas las métricas.

## Decisión

- La lista de columnas prohibidas se mantiene en un único fichero: [`contracts/leakage_columns.py`](../../contracts/leakage_columns.py) (`PROHIBITED_FEATURE_COLUMNS`).
- El test [`tests/test_leakage_gate.py`](../../../../tests/test_leakage_gate.py) escanea `src/capa1_nlp/**/*.py` y `src/capa2_rulefit/**/*.py` y falla si encuentra cualquiera de esas cadenas.
- Excepciones explícitas: ficheros cuyo nombre incluya `leakage`, `prohibit` o `test_` (allowlist limitado a tests y al gate mismo).
- Cuando se añade una columna prohibida nueva, se actualiza la lista en `leakage_columns.py` y el commit menciona ADR-0004.
- La política es **obligatoria** y forma parte de la auditoría UE-IA Anexo III (Cap. 9).

## Consecuencias

**Positivas**

- Imposible introducir leakage por descuido entre tres autores.
- Detección estática en CI (sin tener que entrenar para detectarlo).
- Trazable: el log de commits registra cada cambio en la allowlist.

**Negativas / mitigaciones**

- Falsos positivos si un nombre prohibido aparece como substring legítimo. Mitigado restringiendo el scan a `src/capa1_nlp/` y `src/capa2_rulefit/`, no al repo entero. Si surge una colisión, se puede añadir el fichero a la allowlist con una nota.

## Referencias

- `data-model.md` §"Columnas prohibidas como features"
- Kaufman *et al.* (2012), *Leakage in Data Mining*
