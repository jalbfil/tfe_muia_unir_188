# Feature 001 — Priorización temprana explicable de incidentes 112 CyL

Rediseño del TFM siguiendo **Spec-Driven Development** (GitHub Spec Kit).

## Artefactos

| Archivo | Contenido | Comando Spec Kit equivalente |
|---|---|---|
| [spec.md](./spec.md) | QUÉ y POR QUÉ (sin tecnología) | `/specify` |
| [plan.md](./plan.md) | CÓMO (pila, arquitectura, gates) | `/plan` |
| [research.md](./research.md) | Decisiones técnicas + alternativas | (Phase 0 de `/plan`) |
| [data-model.md](./data-model.md) | Entidades, validaciones, transiciones | (Phase 1 de `/plan`) |
| [contracts/](./contracts/) | JSON Schemas vinculantes entre capas | (Phase 1 de `/plan`) |
| [quickstart.md](./quickstart.md) | Escenarios E2E ejecutables | (Phase 1 de `/plan`) |
| [tasks.md](./tasks.md) | Tareas atómicas TDD con dependencias | `/tasks` |

## Principios inmutables

Ver [.specify/memory/constitution.md](../../.specify/memory/constitution.md) v1.0.0.

## Estado

- [x] Constitución ratificada
- [x] `spec.md` aprobada (sin `[NEEDS CLARIFICATION]`) + sección "Fuera de alcance MVP"
- [x] `plan.md` con Constitution Check ✅
- [x] `research.md` con 12 decisiones + R-13 (simplificación) + Q-01..Q-04 **cerradas**
- [x] `data-model.md` con 8 entidades + tabla de trazabilidad + alcance v0.1.0/v0.2.0
- [x] `contracts/` con 3 contratos vinculantes (3 tools MCP en v0.1.0)
- [x] `quickstart.md` con 6 escenarios E2E
- [x] `tasks.md` con ~90 tareas numeradas (tras simplificación R-13)
- [x] Decisiones Q-01..Q-04 resueltas (Streamlit, validación interna, AEMET/Seveso → v0.2.0)
- [ ] Phase 4 (implementación) iniciada
- [ ] Phase 5 (validación E2E) completada

## Alcance v0.1.0 (decidido 2026-05-24)

- **UI**: Streamlit.
- **Variables activas**: V01–V07, V12–V15 + 10 señales textuales.
- **Variables diferidas v0.2.0**: V08, V09 (AEMET), V10 (SNCZI/inundable), V11 (Seveso).
- **Tools MCP**: 3 (`search_normative`, `get_rule_details`, `cite_legal_basis`). `get_aemet_context` reservada v0.2.0.
- **Validación**: interna entre los 3 autores (≥30 casos, α local). Externa con personal 112 = trabajo futuro.

## Próximo paso

Arrancar **Fase 1** de `tasks.md` (contratos T010–T027) en paralelo entre los 3 autores.
