# ADR-0001 — Pydantic v2 como capa de contratos vinculante

- **Estado**: Aceptada
- **Fecha**: 2026-05-24
- **Versión paquete**: 0.1.0
- **Principio constitucional asociado**: VIII (Contratos antes que código)

## Contexto

El sistema tiene tres capas independientes (NLP, RuleFit, LLM/MCP) desarrolladas por tres autores en paralelo. Sin un contrato fuerte y ejecutable, cada interfaz se convierte en un punto de divergencia, errores silenciosos (e.g. probabilidades que no suman 1) y debt técnico exponencial. El TFM exige además trazabilidad (Principio VII) y reproducibilidad (Principio IX), lo que requiere serialización determinista de los intercambios.

## Alternativas evaluadas

1. **Tipado dinámico + asserts ad-hoc**. Rechazada: imposible enforcement en CI, no genera JSON Schema.
2. **`dataclasses` + `marshmallow`**. Rechazada: doble definición (clase + schema), peor inferencia de tipos, sin invariantes cross-field declarativas.
3. **`attrs` + `cattrs`**. Rechazada: ecosistema más pequeño, menos integrado con FastAPI/MCP.
4. **Protocol Buffers**. Rechazada: introduce un toolchain extra (`protoc`), peor DX para un TFM, mismas garantías que Pydantic v2 con más fricción.
5. **Pydantic v2** ← elegida.

## Decisión

Toda comunicación entre capas pasa por modelos Pydantic v2 con:

- `ConfigDict(extra="forbid", frozen=True)` por defecto: rechazo de campos desconocidos e inmutabilidad.
- `model_validator(mode="after")` para invariantes cross-field (`sum(probs)==1`, `argmax==recommended`, P1/P2 ⇒ ≥1 regla, etc.).
- JSON Schema generado vía `model_json_schema(mode="serialization")` y commiteado a `docs/schemas/`.

## Consecuencias

**Positivas**

- Una sola fuente de verdad (`src/contracts/contracts/`).
- Validación runtime + generación schema con la misma definición.
- Mensajes de error consistentes a través del stack FastAPI / MCP / Streamlit.
- `mypy --strict` limitado a `src/contracts/` queda viable (modelos auto-tipados).

**Negativas / mitigaciones**

- Acoplamiento a Pydantic v2 (riesgo de breaking change). Mitigado fijando `pydantic>=2.7,<3` y aislando dependencias del paquete `contracts` (sin sklearn/torch).
- Pequeño coste de validación runtime (~µs por modelo). Aceptable: invariantes son baratos vs latencia LLM.

## Referencias

- `data-model.md` §"Convenciones de validación"
- `plan.md` §"ADR seeds"
