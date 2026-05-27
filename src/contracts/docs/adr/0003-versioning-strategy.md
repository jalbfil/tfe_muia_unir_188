# ADR-0003 — Versionado SemVer del paquete `contracts` con schema-diff CI

- **Estado**: Aceptada
- **Fecha**: 2026-05-24

## Contexto

El paquete `contracts` es **el** punto de acoplamiento entre las tres capas. Un cambio descuidado (renombrar un campo, ajustar un rango) puede romper silenciosamente el pipeline porque Pydantic admite por defecto que los consumidores ignoren campos nuevos. Necesitamos detección automática en CI.

## Decisión

- El paquete `contracts` lleva su propio `__version__` (`contracts/_version.py`) siguiendo SemVer:
  - **MAJOR** (`X.0.0`): se elimina o renombra un campo, se endurece un constraint, se cambia un tipo.
  - **MINOR** (`0.X.0`): se añade un campo opcional, una nueva enum value, un nuevo modelo.
  - **PATCH** (`0.0.X`): documentación, validadores que no cambian la superficie pública.
- Cada modelo público se exporta a `src/contracts/docs/schemas/<Model>.schema.json` vía `scripts/export_schemas.py`.
- Cada schema commiteado lleva el campo `$contractsVersion` correspondiente.
- El test `tests/test_schema_diff.py` regenera schemas y compara con disco. Si difieren, CI falla.
- Bump de versión + regeneración de schemas se hacen en el **mismo commit** que el cambio del modelo. PRs sin bump cuando hay cambio de schema se rechazan.

## Consecuencias

**Positivas**

- Cambios incompatibles imposibles de mergear sin explicitarse.
- Histórico legible: cada cambio en un schema se vincula a una versión.
- Permite a las tres capas pinear contra una versión concreta del contrato si fuera necesario en el futuro.

**Negativas / mitigaciones**

- Pequeño coste de mantenimiento (regenerar antes de commitear). Mitigado con hook pre-commit local (opcional) y mensaje explícito del test.

## Referencias

- `scripts/export_schemas.py`
- `tests/test_schema_diff.py`
- Pre-Pydantic: Bonér (2007), *Backward Compatibility Strategies for Protocols*.
