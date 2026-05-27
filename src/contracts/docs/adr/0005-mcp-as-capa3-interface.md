# ADR-0005 — Model Context Protocol (MCP) como interfaz de Capa 3

- **Estado**: Aceptada
- **Fecha**: 2026-05-24
- **Principios constitucionales**: VI (Soberanía local), VII (Trazabilidad), X (UE-IA Anexo III)

## Contexto

Capa 3 necesita acceso controlado a tres recursos externos al LLM:

1. Corpus normativo CyL (RAG).
2. Detalle de reglas activadas por Capa 2.
3. Citas legales formateables.

Un acoplamiento clásico vía import directo desde el wrapper del LLM mezclaría responsabilidades, dificultaría la auditoría de qué pidió el modelo y bloquearía la posibilidad de sustituir el LLM (Qwen2.5-7B local) por otro (e.g. en evaluación externa).

## Decisión

- Capa 3 expone sus capacidades como **tools MCP** servidas por `src/capa3_llm_mcp/mcp_server/server.py`.
- v0.1.0 ofrece **exactamente 3 tools** (R-13):
  - `search_normative` — búsqueda semántica en corpus normativo CyL.
  - `get_rule_details` — detalle de una regla por `rule_id`.
  - `cite_legal_basis` — generador de cita legal canónica.
- `get_aemet_context` queda **reservada para v0.2.0** (descope justificado: las variables V08–V11 también se difieren).
- Cada invocación de tool se loguea en `InferenceLog.tools_invoked`. Cualquier tool no registrada hace fallar la validación de `LLMMetadata.tools_invoked` (Pydantic v2 enforcement).
- El LLM corre **local** (llama-cpp-python + Qwen2.5-7B Q4_K_M) — el MCP no expone llamadas a APIs externas en v0.1.0.

## Consecuencias

**Positivas**

- Auditoría completa de qué pidió el modelo (Principio VII).
- Sustituir el LLM no requiere cambiar la lógica de Capa 3.
- Cumple Principio VI (soberanía local: ningún dato sale del prototipo).
- Compatible con UE-IA Anexo III: trazabilidad de cada acción del componente IA.

**Negativas / mitigaciones**

- MCP es un protocolo reciente (Anthropic 2024) — riesgo de evolución. Mitigado anclando el SDK a una versión concreta y limitando la superficie a 3 tools.
- Overhead de orquestación (~10–30ms por tool call). Aceptable dentro del SLA Capa 3 ≤2 000 ms p95.

## Referencias

- Anthropic (2024), *Model Context Protocol Specification*.
- `research.md` §R-08 (MCP).
- `specs/001-priorizacion-112-cyl/contracts/operator_recommendation.contract.md`
