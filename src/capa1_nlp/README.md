# Guía de Ejecución y Verificación — Capa 1 NLP (Ancor)

Esta guía explica detalladamente cómo comprobar el funcionamiento, ejecutar las pruebas de calidad y correr los componentes correspondientes a la **Capa 1 NLP** (procesamiento del lenguaje natural y extracción de características) y la consola interactiva **Streamlit UI**.

---

## 📂 Estructura de la Capa 1

*   `src/capa1_nlp/extraction/signal_extractor.py`: Extractor determinista de señales léxicas por expresiones regulares en español para el 112 CyL.
*   `src/capa1_nlp/inference/feature_extractor.py`: Wrapper principal de inferencia que orquesta el extractor de señales, computa las variables operativas y valida los esquemas contractuales de Pydantic v2.
*   `scripts/train_capa1.py`: Marcador de alcance. En v0.1.0 no entrena transformers ni genera métricas simuladas; remite al reporte determinista y al E2E integrado.

---

## 📋 Tareas de Ancor y Estado de Completitud

En la siguiente tabla se detallan las tareas asignadas a Ancor (`[A]` individuales y `[C]` conjuntas asumidas) y su correspondiente ubicación de entrega en el repositorio:

| Tarea | Tipo | Descripción | Archivo / Ubicación de Entrega |
|---|---|---|---|
| **T040** | `[A]` | Crear la estructura de directorios de la Capa 1 | [src/capa1_nlp/](tfe_muia_unir_188/src/capa1_nlp) |
| **T041** | `[A]` | Test de Contrato de `IncidentFeatures` | [test_capa1_contracts.py](tfe_muia_unir_188/src/capa1_nlp/tests/test_capa1_contracts.py) |
| **T042** | `[A]` | Test de Latencia de Inferencia ($\le 500\text{ ms}$ p95) | [test_capa1_latency.py](tfe_muia_unir_188/src/capa1_nlp/tests/test_capa1_latency.py) |
| **T043** | `[A]` | Test de Prevención de Fuga de Datos (Anti-Leakage) | [test_capa1_anti_leakage.py](tfe_muia_unir_188/src/capa1_nlp/tests/test_capa1_anti_leakage.py) |
| **T044** | `[A]` | Extractor determinista de 10 señales léxicas (Regex) | [signal_extractor.py](tfe_muia_unir_188/src/capa1_nlp/extraction/signal_extractor.py) |
| **T045** | `[A]` | Dataset de PyTorch para clasificación multitarrea | Diferido a trabajo futuro; Capa 1 v0.1.0 queda determinista |
| **T046** | `[A]` | Entrenamiento multitarrea `roberta-base-bne` | Diferido a trabajo futuro; no hay checkpoint congelado en v0.1.0 |
| **T047** | `[A]` | Wrapper de inferencia unificado (Capa 1 NLP) | [feature_extractor.py](tfe_muia_unir_188/src/capa1_nlp/inference/feature_extractor.py) |
| **T048** | `[A]` | Reporte de métricas técnicas de test (F1, Recall) | [capa1_v0.1.0.json](tfe_muia_unir_188/artifacts/reports/capa1_v0.1.0.json) |
| **T049** | `[A]` | Ficha técnica (*Model Card*) académica | [anexo_l.tex](tfe_muia_unir_188/latex/chapters/anexo_l.tex) |
| **T101** | `[C]` | Consola Gráfica de Emergencias (Streamlit) | [app.py](tfe_muia_unir_188/src/ui/app.py) |
| **T102** | `[C]` | Apéndice de experiencia de usuario y capturas | [anexo_g.tex](tfe_muia_unir_188/latex/chapters/anexo_g.tex) |

---

## 🧪 1. Ejecución de Tests de Calidad (Verificación Automatizada)

Para ejecutar la batería completa de pruebas unitarias y de integración de tu parte del proyecto, abre una terminal de PowerShell en la raíz del repositorio y ejecuta:

```powershell
pytest src/capa1_nlp/tests/ -v
```

### ¿Qué validan estos tests?
1.  **Test de Contrato (`test_capa1_contracts.py`)**: Envía textos reales de incidentes y verifica que el Feature Extractor entregue un objeto `IncidentFeatures` estrictamente válido según el esquema contractual.
2.  **Test de Latencia (`test_capa1_latency.py`)**: Realiza un benchmark de 100 iteraciones rápidas y certifica que el tiempo de ejecución cumple holgadamente con el SLA de **$\le 500\text{ ms}$ p95** (obteniendo tiempos reales en torno a **$0.15\text{ ms}$**).
3.  **Test de Anti-Leakage (`test_capa1_anti_leakage.py`)**: Valida estáticamente que no se referencie ningún campo prohibido de post-decisión (`MediosMov`, `PacientesAten`, etc.) en el código productivo de la Capa 1.

Para verificar que también cumples con la política del monorepo a nivel global, corre:
```powershell
pytest tests/test_leakage_gate.py -v
```

---

## 📈 2. Alcance del entrenamiento de Capa 1

En v0.1.0 la Capa 1 no entrena transformers. Para evitar confusión metodológica,
`scripts/train_capa1.py` actúa como marcador explícito de alcance: no genera checkpoints
ni métricas simuladas. La evidencia oficial de Capa 1 procede del extractor
determinista y de la validación integrada.

```powershell
python scripts/train_capa1.py
```

### Salida Esperada:
*   Indicará que Capa 1 v0.1.0 es determinista.
*   Remitirá a `artifacts/reports/capa1_v0.1.0.json`.
*   Remitirá a `artifacts/reports/capa1_capa2_e2e_v0.1.0.json`.

---

## 🖥️ 3. Ejecución de la Consola Interactiva (Frontend Streamlit)

Para levantar el cuadro de mando gráfico del operador 112 CyL y comprobar la integración del Feature Extractor, el LLM y el flujo HITL (*Human-in-the-Loop*), corre:

```powershell
streamlit run src/ui/app.py
```

### Características de Demostración:
*   Abre tu navegador en: `http://localhost:8501`.
*   Usa el selector del menú lateral **"Plantillas de Escenarios"** para cargar de inmediato los casos de prueba de accidentes viales graves o incidencias ordinarias sin tener que escribir.
*   Pulsa en **"Analizar Incidente"** para ver las prioridades en colores curados HSL, las probabilidades reactivas, la justificación legal y registrar tu decisión final de operador.
*   **Nota de Robustez**: Si el backend de FastAPI está apagado, la aplicación de Streamlit activará automáticamente un fallback *in-process* local para ejecutar la inferencia de manera transparente.

---

## 🐍 4. Verificación Rápida por Consola de Python

Si deseas comprobar el Feature Extractor directamente mediante código de Python, puedes abrir una consola interactiva `python` en la raíz del proyecto y correr:

```python
from datetime import datetime, timezone
from contracts import IncidentInput, CategoriaPreliminar
from capa1_nlp.inference.feature_extractor import FeatureExtractor

# 1. Crear un incidente de prueba
incident = IncidentInput(
    incident_id="01AN4V07BY79KA1307SR9X4MV3",
    texto_titulo="Accidente grave",
    texto_descripcion="Choque frontal entre dos coches. Varón inconsciente atrapado.",
    categoria_preliminar=CategoriaPreliminar.ACCIDENTE_TRAFICO,
    fecha_incidente=datetime.now(timezone.utc),
    operador_id="OP_TEST",
)

# 2. Inicializar tu Feature Extractor y clasificar
extractor = FeatureExtractor()
features = extractor.extract_features(incident)

# 3. Validar resultados de tus señales léxicas
print(f"¿Atrapado?: {features.signal_atrapado.value} (Confianza: {features.signal_atrapado.confidence})")
print(f"¿Herido Grave?: {features.signal_herido_grave.value}")
print(f"¿Riesgo Vital?: {features.riesgo_vital.value}")
```
