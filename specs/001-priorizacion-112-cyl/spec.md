# Feature Specification: Priorización temprana explicable de incidentes 112 en Castilla y León

**Feature Branch**: `001-priorizacion-112-cyl`
**Created**: 2026-05-24
**Status**: Draft
**Input**: Pivote metodológico TFM Tipo 2 — abandono de Aragón y datos simulados; adopción del Registro 112 CyL 2008–2022 (n=9 380), etiqueta académica P1–P4 por supervisión débil, núcleo RuleFit, comparativa contra baseline experto, capa de explicación con LLM local y servidor MCP, conformidad con Reglamento UE 2024/1689 (alto riesgo).

---

## Execution Flow (resumen del rediseño)

```
1. Operador 112 recibe llamada y registra texto libre + categoría preliminar + coordenadas
2. Sistema NLP extrae entidades y variables operativas V01–V15 (Capa 1)
3. Motor RuleFit calcula prioridad recomendada P1–P4 + probabilidad + reglas activadas (Capa 2)
4. LLM local genera explicación textual con bases legales (Capa 3, con tool calling sobre corpus normativo CyL vía MCP)
5. Operador revisa la recomendación, acepta/modifica/rechaza, queda registro auditable
6. Métricas y logs alimentan evaluación continua y trazabilidad
```

---

## ⚡ Quick Guidelines

- ✅ Foco en el **QUÉ** y el **PORQUÉ**, no en el **CÓMO** (la pila técnica vive en `plan.md`).
- ✅ Dirigido a tribunal académico, director de TFM y futuros operadores 112.
- ❌ No mencionar nombres de librerías, frameworks ni endpoints concretos en este documento.

---

## User Scenarios & Testing

### Primary User Story

Un **operador del 112 de Castilla y León** recibe una llamada de emergencia. Tras anotar texto libre, categoría preliminar y obtener coordenadas del llamante, lanza el DSS. En menos de 2 segundos el sistema le devuelve una **prioridad recomendada P1–P4**, una **explicación textual breve** (por qué esa prioridad, qué señales se han detectado, qué normativa la respalda) y una **lista de reglas operativas activadas**. El operador puede aceptar la recomendación, modificarla o rechazarla; en todos los casos su decisión queda registrada junto con la recomendación del sistema para auditoría posterior.

### Acceptance Scenarios

1. **Given** un incidente con texto *"varón inconsciente tras choque frontal en N-122, herido grave atrapado"*, categoría preliminar `accidente_trafico`, coordenadas en zona rural de Soria, **When** el operador solicita priorización, **Then** el sistema devuelve P1 con probabilidad ≥0,80, reglas `signal_atrapado=TRUE AND signal_herido_grave=TRUE → P1` activadas y explicación citando Ley 17/2015 (afectación a personas) y PLANCAL Sit. 2.

2. **Given** un incidente con texto *"árbol caído en arcén, sin afectados"*, categoría `incidencia_via`, **When** el operador solicita priorización, **Then** el sistema devuelve P4 con probabilidad ≥0,70, explicación citando inexistencia de señales de riesgo vital.

3. **Given** una llamada con descripción de *"olor fuerte a químico saliendo de camión cisterna en autovía"*, **When** el operador solicita priorización, **Then** el sistema devuelve P1 o P2, activa la regla de mercancías peligrosas y cita el MPCyL (Acuerdo 3/2008) en la explicación.

4. **Given** que el operador rechaza la recomendación del sistema, **When** registra su prioridad alternativa, **Then** el sistema almacena ambas (recomendada y final), motivo opcional, y emite evento de auditoría.

5. **Given** que el sistema recibe una llamada con texto vacío o ininteligible, **When** intenta priorizar, **Then** devuelve un error controlado con `confidence=UNKNOWN`, sugiere P3 como prioridad por defecto conservadora y notifica al operador que la decisión recae íntegramente en él.

6. **Given** que el operador consulta el detalle de una regla activada, **When** invoca `get_rule_details`, **Then** el sistema devuelve la regla en lenguaje natural, su sustento normativo, ejemplos históricos y advertencias de uso.

### Edge Cases

- **Incidente sin coordenadas** → el sistema procede solo con texto + categoría; marca `tiene_coordenadas=FALSE`; reduce confianza en variables contextuales (zona inundable, distancia Seveso).
- **Incidente con múltiples categorías** simultáneas (p. ej. incendio + intoxicación) → se activan múltiples reglas; la prioridad final es el máximo (P1 ≻ P2 ≻ P3 ≻ P4).
- **Modelo no calibrado o confianza < umbral** → la recomendación se marca como `LOW_CONFIDENCE`; la UI debe destacar visualmente la necesidad de juicio humano.
- **Texto en lengua cooficial o con errores graves** → fallback al baseline experto si el modelo NLP no alcanza umbral de confianza.
- **Demanda concurrente alta** (varias llamadas simultáneas) → el sistema debe priorizar latencia; degradación elegante: omitir capa LLM si supera SLA, devolver solo RuleFit + reglas.

### Fuera de alcance — MVP v0.1.0 (decisión R-13)

Para garantizar la entrega de un núcleo evaluable y defendible en abril 2026, **se difiere a v0.2.0**:

- **Enriquecimiento meteorológico AEMET** (V08 `aviso_aemet_nivel`, V09 `condicion_meteorologica_adversa`) — requiere descarga histórica + cruce geoespacial + parser de boletines; no aporta a las métricas críticas (recall@P1, ECE) del núcleo.
- **Análisis de proximidad Seveso** (V10 `en_zona_inundable_snczi`, V11 `proximo_instalacion_seveso_km`) — requiere cartografía industrial CyL no consolidada en datos abiertos; el riesgo químico ya se cubre vía `signal_intoxicacion` + MPCyL.
- **Tool MCP `get_aemet_context`** — reservada en el contrato pero no implementada; v0.1.0 expone **3 tools** (`search_normative`, `get_rule_details`, `cite_legal_basis`).
- **Validación con panel experto externo del 112** — v0.1.0 ejecuta **validación interna entre los 3 autores** sobre ≥30 casos; el contacto y validación con personal del 112 queda como trabajo futuro y se documenta en el plan de continuidad (Cap. 10).
- **Frontend React/Vite** — descartado; v0.1.0 implementa UI en **Streamlit** (suficiente para demo, defensa académica y operación interactiva).

Estos diferidos **no comprometen ningún principio constitucional** (I–X): el caso empírico CyL, la supervisión humana, RuleFit como núcleo, la trazabilidad normativa y la conformidad UE-IA se preservan íntegros.

---

## Requirements

### Functional Requirements

- **FR-001** El sistema DEBE aceptar como entrada texto libre del operador, categoría preliminar (opcional), coordenadas (opcionales), y marca temporal del incidente.
- **FR-002** El sistema DEBE extraer automáticamente, desde el texto, un conjunto estructurado de variables operativas V01–V15 (riesgo vital, víctimas, vulnerabilidad, etc.) con confianza asociada.
- **FR-003** El sistema DEBE producir una recomendación de prioridad en el rango P1–P4, una probabilidad asociada a cada clase, y la lista de reglas activadas que justifican la decisión.
- **FR-004** El sistema DEBE generar una explicación textual breve (≤120 palabras) comprensible por personal no técnico, citando bases legales aplicables.
- **FR-005** El sistema DEBE permitir al operador aceptar, modificar o rechazar la recomendación, registrando ambas (recomendación y decisión final) con timestamp y motivo opcional.
- **FR-006** El sistema DEBE exponer una interfaz programática consultable que permita a herramientas externas (clientes MCP) invocar consultas sobre normativa, detalle de reglas, contexto meteorológico y cita legal de prioridades.
- **FR-007** El sistema DEBE rechazar (con error explícito) cualquier intento de usar como entrada variables clasificadas como **post-decisión** (medios movilizados, pacientes atendidos, incidente cerrado, última actualización).
- **FR-008** El sistema DEBE generar logs estructurados de cada inferencia (entrada hash, salida, reglas, latencia, versión del modelo) para auditoría y evaluación.
- **FR-009** El sistema DEBE poder operar en modo degradado (sin Capa 3) si el LLM no está disponible o si la latencia supera el SLA.
- **FR-010** El sistema DEBE permitir reproducir la inferencia dado un identificador de log (determinismo de las capas 1 y 2; capa 3 con temperatura 0).

### Non-Functional Requirements

- **NFR-001 (Latencia)** La pipeline completa Capa 1 + Capa 2 DEBE responder en ≤500 ms en p95. Capa 3 (explicación) DEBE responder en ≤2 s en p95.
- **NFR-002 (Calibración)** El modelo de Capa 2 DEBE alcanzar Expected Calibration Error (ECE) ≤ 0,10 en test.
- **NFR-003 (Sensibilidad crítica)** Recall en clase P1 DEBE ser ≥ 0,85 en test, priorizando minimizar falsos negativos en incidentes graves.
- **NFR-004 (Interpretabilidad)** RuleFit DEBE producir un modelo con ≤30 reglas activas con coeficiente ≠ 0.
- **NFR-005 (Soberanía)** Toda inferencia DEBE ejecutarse on-premise. Prohibido envío de datos a APIs externas en producción.
- **NFR-006 (Conformidad)** El diseño DEBE estar alineado con el Reglamento (UE) 2024/1689 Anexo III (sistemas de alto riesgo): supervisión humana, gestión de riesgos, calidad de datos, trazabilidad, transparencia, robustez.
- **NFR-007 (Privacidad)** El sistema DEBE cumplir RGPD y LOPDGDD: minimización, limitación de finalidad, no reidentificación.
- **NFR-008 (Accesibilidad)** La interfaz operativa DEBE cumplir requisitos básicos de accesibilidad WCAG 2.1 nivel AA en componentes críticos.
- **NFR-009 (Reproducibilidad)** Todos los experimentos del Cap. 9 DEBEN ser reproducibles a partir de seeds, splits y artefactos versionados.
- **NFR-010 (Hardware)** El sistema completo DEBE ejecutarse en hardware de gama consumer (RTX 5070 8GB VRAM, 64GB RAM, CPU x86_64).

### Key Entities

- **Incidente** — Unidad de análisis. Texto libre, categoría preliminar, coordenadas opcionales, marca temporal. Origen: llamada 112.
- **Caracterización del incidente (IncidentFeatures)** — Salida de Capa 1: V01–V15 con confianza, señales operativas extraídas (`signal_*`), entidades NER (víctimas, ubicación, agentes).
- **Recomendación de prioridad (PriorityRecommendation)** — Salida de Capa 2: prioridad P1–P4, distribución de probabilidad, reglas activadas (id + texto humano + peso), nivel de confianza global.
- **Recomendación al operador (OperatorRecommendation)** — Salida de Capa 3: prioridad + explicación textual + citas normativas + recomendaciones de actuación.
- **Decisión del operador** — Prioridad finalmente asignada por el operador (puede coincidir o no con la recomendación), motivo opcional, timestamp.
- **Regla operativa** — Regla activa en RuleFit o en el baseline experto. Tiene id, texto humano, peso, sustento normativo (lista de citas), métricas de uso.
- **Etiqueta P1–P4 académica** — Etiqueta sintética construida por supervisión débil sobre ≥3 anotadores independientes, no oficial, anclada en criterios de PLANCAL.
- **Log de inferencia** — Registro auditable de cada llamada al sistema: input hash, output completo, latencias por capa, versiones de modelo, timestamp.
- **Corpus normativo** — Documentos legales (Ley 17/2015, RD 524/2023, PLEGEM, Ley 4/2007 CyL, PLANCAL, Ley 11/2022, RGPD, LOPDGDD, Reg. UE 2024/1689, INFOCAL, INUNCYL, MPCyL, RD 840/2015) chunked y embebidos para RAG.

---

## Review & Acceptance Checklist

### Content Quality
- [x] No detalles de implementación (lenguajes, frameworks, APIs)
- [x] Enfocado en valor para el usuario (operador 112) y necesidades del tribunal
- [x] Escrito para audiencia no estrictamente técnica
- [x] Todas las secciones obligatorias completas

### Requirement Completeness
- [x] Sin marcadores `[NEEDS CLARIFICATION]` pendientes
- [x] Requisitos comprobables y no ambiguos
- [x] Criterios de éxito medibles (latencia, recall, ECE, sparsity)
- [x] Alcance acotado al pivote CyL
- [x] Dependencias y supuestos identificados (hardware, dataset, normativa)

---

## Execution Status
- [x] User description parsed
- [x] Key concepts extracted (DSS, P1–P4 académica, RuleFit, MCP, leakage, CyL)
- [x] Ambiguities resolved (Aragón fuera; agente NO; LLM local)
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed
