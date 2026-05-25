# Guía de etiquetado P1–P4 — Castilla y León v0.1.0

> **Función**: especificación canónica para los cuatro anotadores de [`scripts/build_weak_labels.py`](../scripts/build_weak_labels.py) (LLM-as-annotator, NER + intensificadores, clustering, reglas heurísticas) y para la validación interna entre los 3 autores (T114).
>
> **Versión**: 0.1.0 · **Fecha**: 2026-05-24 · **Alcance**: variables V01–V07, V12–V15 activas; V08–V11 (AEMET, INUNCYL, Seveso) diferidas a v0.2.0 según R-13.
>
> **Marco normativo de referencia**: PLANCAL (Decreto 4/2019, JCYL), Ley 17/2015 SNPC, Ley 4/2007 CyL, INFOCAL (Decreto 6/2025), MPCyL (Acuerdo 3/2008).
>
> **Naturaleza de la etiqueta** (ADR-0002): P1–P4 es una **proxy académica** derivada por weak supervision del texto histórico del 112 CyL. **No** sustituye al juicio operativo de un CECOP real.

---

## 1. Principios generales

| # | Principio | Implicación operativa |
|---|---|---|
| P-01 | La prioridad mide **urgencia operativa relativa** | No mide gravedad final ni importancia abstracta. |
| P-02 | Se etiqueta **en el momento de la primera decisión** | No incorporar información posterior. |
| P-03 | Precaución razonable, no dramatización | Ante incertidumbre, escenario moderadamente desfavorable. |
| P-04 | Toda asignación debe ser **justificable** | Vincular a variables concretas o reglas duras. |
| P-05 | Independencia entre casos | La distribución del dataset se logra por diseño, no ajustando etiquetas. |

## 2. Definición operativa de los cuatro niveles

| Nivel | Denominación | Significado operativo | Ejemplos típicos |
|---|---|---|---|
| **P1** | Crítica | Riesgo vital confirmado o altamente probable; escalada inminente. | Atrapados, AMV, fuga tóxica en zona habitada, inundación con personas aisladas. |
| **P2** | Alta | Gravedad significativa o potencial de escalado sin riesgo vital inmediato confirmado. | Incendio urbano sin atrapados confirmados, búsqueda de menor, varias llamadas coincidentes. |
| **P3** | Media | Gestionable con medios ordinarios; sin urgencia vital ni escalado a corto plazo. | Accidente sin víctimas graves, incendio contenido, incidencia meteorológica limitada. |
| **P4** | Baja | Incidente menor, consulta o gestión diferida. | Consultas informativas, verificaciones rutinarias, sucesos ya resueltos al recibirse. |

Anclaje normativo: art. 6 de **PLANCAL (Decreto 4/2019)** sobre clasificación operativa por nivel de impacto y Anexo III sobre escalado de medios.

## 3. Reglas duras (`RD-XX`)

Si un caso cumple la condición de una regla dura, la prioridad asignada **no puede ser inferior** al mínimo establecido salvo justificación explícita y documentada. Cada regla cita la norma que la fundamenta usando el `NormaID` del enum `contracts.enums.NormaID`.

| ID | Condición | Prioridad | Anclaje (`NormaID`) | Notas |
|---|---|---|---|---|
| `RD-01` | V01 = `True` (riesgo vital confirmado) | **P1 fija** | `LEY_17_2015` art. 1; `PLANCAL_DEC_4_2019` art. 6 | Sin excepción aunque falten otras variables. |
| `RD-02` | V02 ≥ 3 víctimas | **P2 mín.** | `PLANCAL_DEC_4_2019` art. 14 | Puede elevarse a P1 con otros factores. |
| `RD-03` | V02 > 10 víctimas | **P1 mín.** | `PLANCAL_DEC_4_2019` Anexo III | Subsume `RD-02`. |
| `RD-04` | Búsqueda de menor o persona vulnerable confirmada (V05) | **P2 mín.** | `LEY_4_2007_CYL` art. 3 | Ambas condiciones (búsqueda + vulnerabilidad). |
| `RD-05` | Inundación con personas aisladas o atrapadas | **P1 fija** | `LEY_17_2015` art. 1; `INUNCYL` †v0.2.0 | Riesgo vital aunque el alertante no lo verbalice. |
| `RD-06` | Incendio forestal en interfaz urbano-forestal con condiciones meteo activas | **P2 mín.** | `INFOCAL_DEC_6_2025` | IUF es el factor clave, no incendio puro. |
| `RD-07` | Fuga química con afectación directa a zona habitada | **P1 mín.** | `MPCYL_ACUERDO_3_2008`; `RD_840_2015_SEVESO` †v0.2.0 | No basta proximidad: evidencia directa. |
| `RD-08` | Categoría preliminar = consulta informativa y V01 = `False` y V02 = 0 | **P4 fija** | `REGISTRO_112_CYL` | Sin gestión operativa esperable. |
| `RD-09` | V03 (gravedad lesiones) ∈ {`CRITICA`} | **P1 fija** | `LEY_17_2015` art. 1 | Confirmación de daño vital. |
| `RD-10` | V07 (emplazamiento crítico) = `True` con afectación a continuidad de servicio esencial | **P2 mín.** | `LEY_4_2007_CYL` art. 5 | Hospital, escuela, infraestructura crítica. |

†v0.2.0: el anclaje está reservado; en v0.1.0 la regla aplica sin invocar la norma (V08–V11 no se evalúan).

## 4. Resolución de conflictos

1. **Prevalencia de la mayor urgencia** compatible con la información disponible.
2. **Las reglas duras prevalecen** sobre la valoración global. Ningún conjunto favorable rebaja un mínimo fijado por `RD-XX`.
3. **Gravedad inmediata > contexto.** En conflicto entre V01/V02/V03 y variables contextuales, prevalece la gravedad inmediata.
4. **Incertidumbre → confianza, no prioridad.** Se refleja en `ConfidenceLevel`, nunca rebajando la etiqueta.
5. **El contexto solo eleva, nunca rebaja.** La ausencia de amenaza contextual no rebaja una prioridad ya justificada por gravedad/vulnerabilidad.
6. **Documentar conflicto** en el campo `rationale` cuando aparezca.

## 5. Confianza (`ConfidenceLevel`)

| Nivel | Umbral p_max | Condiciones | Implicación |
|---|---|---|---|
| `HIGH` | ≥ 0.80 | Variables críticas (V01, V02, V07) informadas. Coherencia interna. | Etiqueta fiable. |
| `MEDIUM` | ≥ 0.60 | Variable relevante ausente o ambigua. | Etiqueta razonable, no definitiva. |
| `LOW` | ≥ 0.40 | Variables críticas ausentes. Información fragmentaria. | Orientativa. |
| `UNKNOWN` | < 0.40 | Información insuficiente. | No usar como gold. |

**Independencia confianza ↔ prioridad**: un incidente puede ser P1 con `ConfidenceLevel.LOW` si el reporte sugiere riesgo vital pero la fuente es fragmentaria. No rebajar prioridad para compensar baja confianza.

## 6. Casos frontera

### 6.1. P1 ↔ P2
Pregunta: ¿existe riesgo vital **inminente** o solo **potencial**?
- Indicios fuertes no confirmados → **P1** con `MEDIUM`.
- Riesgo moderado → **P2** con `MEDIUM`.

### 6.2. P2 ↔ P3
Pregunta: ¿requiere respuesta rápida coordinada o es gestionable con medios ordinarios?
- ≥2 factores significativos (potencial escalado + vulnerabilidad + complejidad coordinación) → **P2** con `MEDIUM`.
- En caso contrario → P3.

### 6.3. P3 ↔ P4
- Daño material, desplazamiento de servicios o afectación a vía pública → **P3**.
- Consulta informativa, verificación rutinaria o incidente ya resuelto al recibirse → **P4**.

## 7. Procedimiento de etiquetado (6 pasos)

1. **Lectura** completa del texto del incidente.
2. **Verificación de reglas duras** (`RD-01` … `RD-10`). Si una se activa con prioridad fija, FIN.
3. **Valoración de variables** V01–V07, V12–V15 por jerarquía (V01 > V02 > V03 > V07 > V05 > resto).
4. **Asignación de prioridad** considerando reglas mínimas y resolución de conflictos.
5. **Asignación de confianza** (sección 5).
6. **Redacción de `rationale`** en 1–2 frases citando variables y reglas activadas.

## 8. Acuerdo inter-anotador

- **Umbral global**: Krippendorff α ≥ **0.67** sobre el dataset completo (T033).
- **Por anotador**: cada uno de los 4 anotadores reporta su α individual respecto al label model final.
- **Validación interna 3 autores** (T114): ≥30 casos etiquetados independientemente, se calcula α local, se documentan divergencias en `anexo_d.tex`.

## 9. Limitaciones reconocidas

1. La guía **no ha sido validada** por personal operativo del 112 CyL (trabajo futuro, Cap. 10).
2. Las reglas se anclan a normativa **vigente a 2026-05** ([`resources/corpus_normativo/manifest.yaml`](corpus_normativo/manifest.yaml)).
3. Las variables V08–V11 (AEMET, INUNCYL, Seveso) están **diferidas a v0.2.0**; las reglas duras que las invocan operan con su anclaje normativo pero sin evaluación cuantitativa.
4. El etiquetado se realiza sobre **texto histórico** del 112 CyL, no sobre escenarios en tiempo real.

## 10. Referencias cruzadas

- Variables V01–V15: [`src/contracts/contracts/incident_features.py`](../src/contracts/contracts/incident_features.py).
- Enum `NormaID`: [`src/contracts/contracts/enums.py`](../src/contracts/contracts/enums.py).
- Naturaleza académica de la escala: [`src/contracts/docs/adr/0002-priority-scale-p1-p4-is-academic.md`](../src/contracts/docs/adr/0002-priority-scale-p1-p4-is-academic.md).
- Corpus normativo: [`resources/corpus_normativo/manifest.yaml`](corpus_normativo/manifest.yaml).
- Esquema del incidente (Cap. 7): [`latex/resources/chap7.md`](../latex/resources/chap7.md).
- Anexo C LaTeX (versión académica extendida): [`latex/chapters/anexo_c.tex`](../latex/chapters/anexo_c.tex).
