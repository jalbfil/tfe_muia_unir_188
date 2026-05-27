# Data Model

**Feature**: `001-priorizacion-112-cyl` · **Updated**: 2026-05-24

Modelo de datos del DSS. Cada entidad va acompañada de campos, tipo, restricciones, transiciones y reglas de validación. Los contratos vinculantes viven en [`contracts/`](./contracts/).

---

## E-01 IncidentInput (entrada cruda)

Recibida desde la UI o cliente externo. Representa lo que el operador 112 anota al recibir la llamada, antes de ningún procesamiento.

| Campo | Tipo | Restricciones | Origen CyL |
|---|---|---|---|
| `incident_id` | str (ULID) | obligatorio, único | generado |
| `texto_titulo` | str | 1..200 chars | columna `Título` |
| `texto_descripcion` | str | 0..5000 chars | columna `DescripcionBlob` |
| `categoria_preliminar` | str enum CategoriaPreliminar | opcional | derivada `TipoIncidente` |
| `latitud` | float | -90..90, opcional | columna `Localidad.1` |
| `longitud` | float | -180..180, opcional | columna `Localidad.1` |
| `localidad` | str | opcional | columna `Localidad` |
| `provincia` | str enum ProvinciaCyL | opcional | derivada |
| `fecha_incidente` | datetime ISO 8601 (TZ Europe/Madrid) | obligatorio | columna `FechaIncidente` |
| `operador_id` | str | obligatorio | sistema |

Invariantes:
- Si `latitud` está, `longitud` también, y viceversa.
- `texto_titulo` o `texto_descripcion` debe contener al menos un carácter alfabético (no solo espacios/símbolos).

---

## E-02 IncidentFeatures (salida Capa 1)

Estructura producida por la Capa 1 NLP. Es lo que **consume** Capa 2.

### Variables operativas V01–V15

| Var | Nombre | Tipo | Norma de anclaje |
|---|---|---|---|
| V01 | `riesgo_vital` | bool + confidence | Ley 17/2015 |
| V02 | `numero_victimas_estimado` | int (0..50, -1=desconocido) + confidence | Ley 17/2015 |
| V03 | `gravedad_lesiones` | enum {NINGUNA, LEVE, MODERADA, GRAVE, CRITICA, DESCONOCIDA} + confidence | Ley 17/2015 |
| V04 | `tipo_incidente_normalizado` | enum (taxonomía RD 524/2023) | RD 524/2023 |
| V05 | `poblacion_vulnerable` | bool + confidence | Ley 17/2015 |
| V06 | `numero_llamadas` | int (1..N) | dataset |
| V07 | `emplazamiento_critico` | bool (hospital, colegio, residencia…) + confidence | Ley 17/2015 |
| V08 | `aviso_aemet_nivel` | enum {VERDE, AMARILLO, NARANJA, ROJO, NO_DISPONIBLE} | (enriquecimiento) — **DIFERIDA v0.2.0** (R-13) |
| V09 | `condicion_meteorologica_adversa` | bool + confidence | INUNCYL / AEMET — **DIFERIDA v0.2.0** (R-13) |
| V10 | `en_zona_inundable_snczi` | bool | INUNCYL — **DIFERIDA v0.2.0** (R-13) |
| V11 | `proximo_instalacion_seveso_km` | float | RD 840/2015 — **DIFERIDA v0.2.0** (R-13) |
| V12 | `riesgo_propagacion` | bool + confidence | INFOCAL |
| V13 | `multirriesgo` | bool + confidence | PLEGEM |
| V14 | `avisos_simultaneos_zona` | int | PLEGEM |
| V15 | `accesibilidad_recursos` | enum {ALTA, MEDIA, BAJA, DESCONOCIDA} | Ley 4/2007 CyL |

### Señales operativas extraídas

`signal_fallecido`, `signal_herido_grave`, `signal_atrapado`, `signal_intoxicacion`, `signal_varias_llamadas`, `signal_incendio`, `signal_accidente_trafico`, `signal_rescate`, `signal_meteo_inundacion`, `riesgo_vital_textual` — todas `bool + confidence`.

### Metadatos

| Campo | Tipo |
|---|---|
| `incident_id` | str |
| `model_version_capa1` | str semver |
| `inference_timestamp` | datetime |
| `inference_latency_ms` | float |
| `extractor_warnings` | list[str] |

Transiciones de estado:
- `RAW` → `EXTRACTED` (tras Capa 1)
- `EXTRACTED` → `EXTRACTED_LOW_CONFIDENCE` si confianza media < 0,5 → activa fallback baseline experto

---

## E-03 PriorityRecommendation (salida Capa 2)

| Campo | Tipo | Restricciones |
|---|---|---|
| `incident_id` | str | match IncidentInput |
| `priority_recommended` | enum Priority {P1, P2, P3, P4} | obligatorio |
| `probabilities` | dict[Priority, float] | suma == 1.0 ± 1e-6 |
| `activated_rules` | list[ActivatedRule] | ≥ 0 |
| `confidence_level` | enum {HIGH, MEDIUM, LOW, UNKNOWN} | derivado de probabilidad máxima |
| `model_used` | enum {RULEFIT, BASELINE_EXPERT, FALLBACK} | obligatorio |
| `model_version_capa2` | str semver | obligatorio |
| `requires_human_attention` | bool | true si confidence ∈ {LOW, UNKNOWN} o P1 |

### ActivatedRule (sub-entidad)

| Campo | Tipo |
|---|---|
| `rule_id` | str |
| `human_text` | str (≤200 chars) |
| `weight` | float (coeficiente RuleFit) |
| `normative_anchors` | list[str] (códigos: `LEY_17_2015_ART_1`, `PLANCAL_SIT_2`, …) |

Reglas de mapeo confidence:
- `HIGH`: p_max ≥ 0,80
- `MEDIUM`: 0,60 ≤ p_max < 0,80
- `LOW`: 0,40 ≤ p_max < 0,60
- `UNKNOWN`: p_max < 0,40

---

## E-04 OperatorRecommendation (salida Capa 3)

| Campo | Tipo | Restricciones |
|---|---|---|
| `incident_id` | str | match |
| `priority_recommended` | Priority | propagada de E-03 |
| `explanation_text` | str | ≤ 120 palabras |
| `legal_citations` | list[LegalCitation] | ≥ 1 si priority ∈ {P1, P2} |
| `actuation_hints` | list[str] | sugerencias no vinculantes |
| `activated_rules_summary` | list[str] | textos humanos de E-03 |
| `confidence_disclaimer` | str | obligatorio si confidence ≠ HIGH |
| `model_version_capa3` | str semver | obligatorio |
| `llm_metadata` | dict | modelo, temperatura, tools_invoked |

### LegalCitation

| Campo | Tipo |
|---|---|
| `norma_id` | str (ej. `LEY_17_2015`) |
| `articulo_o_seccion` | str opcional |
| `texto_relevante` | str ≤ 300 chars |
| `url_oficial` | str URL BOE/BOCYL |

---

## E-05 OperatorDecision

| Campo | Tipo |
|---|---|
| `incident_id` | str |
| `priority_recommended_by_system` | Priority |
| `priority_assigned_by_operator` | Priority |
| `motivo_divergencia` | str opcional |
| `operador_id` | str |
| `timestamp` | datetime |

Invariante: si `priority_assigned_by_operator != priority_recommended_by_system` y la divergencia es ≥2 niveles (ej. sistema P3, operador P1), se marca evento de auditoría especial.

---

## E-06 OperationalRule (definición persistente)

| Campo | Tipo |
|---|---|
| `rule_id` | str único |
| `source` | enum {EXPERT_BASELINE, RULEFIT_LEARNED} |
| `condition_expression` | str (DSL legible) |
| `human_text` | str |
| `target_priority` | Priority |
| `weight` | float |
| `normative_anchors` | list[str] |
| `usage_count` | int (telemetría) |
| `precision_observed` | float |
| `recall_observed` | float |
| `created_at`, `updated_at` | datetime |

---

## E-07 WeakLabel (artefacto Capa 2 entrenamiento)

| Campo | Tipo |
|---|---|
| `incident_id` | str |
| `annotator_votes` | dict[annotator_id, Priority] |
| `final_label` | Priority |
| `label_model_confidence` | float |
| `agreement_score` | float (Krippendorff α local) |
| `was_used_in_training` | bool |

---

## E-08 InferenceLog (auditoría)

| Campo | Tipo |
|---|---|
| `log_id` | ULID |
| `incident_id` | str |
| `input_hash` | str SHA-256 |
| `capa1_output` | IncidentFeatures (snapshot) |
| `capa2_output` | PriorityRecommendation (snapshot) |
| `capa3_output` | OperatorRecommendation (snapshot, opcional) |
| `operator_decision` | OperatorDecision (opcional) |
| `latencias_ms` | dict[capa, float] |
| `model_versions` | dict[capa, str] |
| `tools_invoked` | list[str] (MCP) |
| `timestamp_start`, `timestamp_end` | datetime |

Retención: 12 meses (configurable). Cifrado en reposo del campo `capa1_output.texto_*` (Principio VI + RGPD).

---

## Variables PROHIBIDAS como features (Principio V — gate CI)

| Columna CyL | Razón |
|---|---|
| `MediosMov`, `medios_mov_limpio`, `medios_mov_uso_recomendado` | Decisión post-priorización |
| `PacientesAten`, `pacientes_aten_limpio` | Resultado clínico ex-post |
| `IncidenteCerrado` | Estado final |
| `ultimaActualizacion` | Cierre |
| `Enlace al contenido` | Identificador externo |
| `Unnamed: 13` | Vacía (100% nulos) |

Estas columnas se permiten **solo** en el subconjunto `evaluation_only_ex_post` del dataset, marcado con bandera, y se prohíbe su importación en cualquier módulo de `capa1_nlp/` o `capa2_rulefit/inference`.

---

## Tabla de trazabilidad Norma → Criterio → Variable → Regla → Uso

| Norma | Criterio | Variable | Regla | Uso |
|---|---|---|---|---|
| Ley 17/2015 art. 1 | Protección vida | V01, V02, V03 | RD1, RD3 | Hard rule P1 |
| Ley 17/2015 | Vulnerabilidad | V05, V07 | Boost P1↑ | Soft rule |
| RD 524/2023 | Catálogo riesgos | V04 | Taxonomía | Feature categórica |
| RD 524/2023 | Sit. 0–3 | — | — | Anclaje guía P1–P4 |
| PLEGEM | Multirriesgo | V13, V14 | RD7 | Escalado |
| Ley 4/2007 CyL | Inmediatez, recursos | V15 | RD8 | Ajuste TTFD |
| PLANCAL D.4/2019 | Fases / Sit. | — | — | Guía etiquetado P1–P4 |
| Ley 11/2022 art. 74 | Localización | lat/lon | — | RNF privacidad |
| Registro 112 CyL CC BY 4.0 | Datos abiertos | Todas | — | Fuente empírica |
| RGPD + LOPDGDD | Minimización | (negativa) | — | Política exclusión |
| Reg. UE 2024/1689 Anexo III | Alto riesgo / supervisión | — | — | Arquitectura HITL |
| INFOCAL Dec.6/2025 | Incendio forestal | V12, signal_incendio | RD4 | Soft P2/P1 |
| INUNCYL | Inundación | V09, V10, signal_meteo_inundacion | RD9 | Boost contextual |
| MPCyL Acuerdo 3/2008 | Mercancías peligrosas | signal_intoxicacion | RD5, RD6 | Hard rule |
| RD 840/2015 Seveso | Riesgo químico industrial | V11 | RD10 | Soft (condicionado) |

Esta tabla se referencia desde Cap. 3 (marco normativo), Cap. 6 (diseño motor), Cap. 7 (datos) y Anexo M (extendida).

---

## Alcance v0.1.0 vs v0.2.0 (R-13)

**Variables activas en v0.1.0** (entrenadas, expuestas y evaluadas):
V01, V02, V03, V04, V05, V06, V07, V12, V13, V14, V15 + las 10 señales textuales.

**Variables diferidas a v0.2.0** (presentes en el contrato como opcionales = `NO_DISPONIBLE`, pero no entrenadas ni exigidas):
V08, V09, V10, V11. Su anclaje normativo (INUNCYL, RD 840/2015 Seveso) permanece en marco teórico (Cap. 3) como justificación de la línea de extensión.

**Razón**: Cierre de Q-03 y Q-04 con calendario abril 2026; se prioriza solidez del núcleo NLP + RuleFit + LLM sobre cobertura contextual.
