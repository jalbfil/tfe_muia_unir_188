

# PROPUESTA “MIX” DEFINITIVA — TFE / TFM

## 1. Título del trabajo (≤ 15 palabras)

**Sistema inteligente de apoyo a la decisión para puestos de mando de emergencias**

👉 Se mantiene este título porque:

* es neutro,
* académico,
* no promete más de lo que se entrega,
* y permite introducir módulos avanzados **sin obligarte a ellos**.

---

## 2. Descripción y justificación del trabajo

La gestión de emergencias en puestos de mando civiles presenta un problema recurrente: la **recepción simultánea de información heterogénea, incompleta y en ocasiones degradada**, procedente de múltiples fuentes y canales. Durante los primeros momentos de una catástrofe (incendios, inundaciones, terremotos), esta saturación informativa incrementa la carga cognitiva de los operadores y **retrasa la adopción de la primera decisión operativa**, con impacto directo en la eficacia de la respuesta.

Este Trabajo Fin de Estudios propone el **diseño e implementación de un sistema inteligente de apoyo a la decisión** para puestos de mando de emergencias, orientado a **reducir la latencia entre la detección de un evento y la primera decisión operativa**, manteniendo siempre al operador humano como responsable final de la decisión.

El sistema se concibe como una **plataforma software modular**, ejecutada de forma local, que integra diferentes técnicas de Inteligencia Artificial para transformar información no estructurada y multimodal en **informes de situación estructurados, priorizados y trazables**, facilitando la comprensión rápida del estado de la emergencia.

La arquitectura del sistema combina:

* técnicas de **Procesamiento del Lenguaje Natural (NLP)** para la extracción de información relevante a partir de textos y mensajes ciudadanos,
* técnicas de **análisis de información geoespacial e imágenes** basadas en datasets abiertos, como apoyo contextual a la toma de decisiones,
* modelos de **aprendizaje automático** para la estimación de impacto y gravedad,
* y mecanismos de **priorización y apoyo a la decisión** integrados en una interfaz operativa.

La justificación del trabajo radica en demostrar la **viabilidad técnica y académica** de orquestar estas tecnologías en un prototipo funcional, evaluable y éticamente responsable, alineado con los principios de **IA aplicada, ingeniería software y Tech4Good**, tal y como se requiere en el TFE del Máster.

---

## 3. Objetivo general

**Diseñar e implementar un sistema inteligente de apoyo a la decisión que reduzca el tiempo hasta la primera decisión operativa en puestos de mando de emergencias civiles, bajo condiciones de saturación informativa.**

Este objetivo se evalúa de forma cuantitativa mediante la métrica **Time To First Decision (TTFD)**, definida como el tiempo transcurrido desde la recepción de la información inicial hasta la confirmación humana de la primera decisión operativa.

---

## 4. Objetivos específicos

1. Analizar el problema de la saturación informativa en puestos de mando de emergencias y las soluciones existentes en la literatura.
2. Diseñar una arquitectura software modular para la ingesta, estructuración y priorización de información multicanal.
3. Implementar un pipeline de **NLP** para la extracción de entidades, localizaciones y señales operativas a partir de texto no estructurado (avisos ciudadanos, informes, comunicaciones).
4. Integrar información geoespacial y visual procedente de **datasets abiertos** como apoyo contextual a la toma de decisiones.
5. Desarrollar un modelo de priorización de incidentes basado en criterios operativos y estimaciones de impacto.
6. Evaluar el sistema mediante escenarios civiles simulados, comparando el TTFD frente a un enfoque manual de referencia.

---

## 5. Alcance funcional del sistema (mix bien acotado)

Para evitar un alcance excesivo, el sistema se estructura en **cuatro módulos**, pero con **roles claramente delimitados**:

### 🔹 Módulo de Escucha y Estructuración (NLP)

* Procesamiento de texto no estructurado (avisos ciudadanos, informes, emails).
* Extracción de entidades (ubicaciones, eventos, recursos).
* Normalización de la información en eventos operativos estructurados.

### 🔹 Módulo de Contexto Geoespacial y Visual

* Uso de imágenes satelitales o aéreas procedentes de datasets públicos.
* Análisis visual básico (segmentación o clasificación) como **información contextual**, no como sistema de detección autónoma.
* El resultado **no decide**, solo apoya.

### 🔹 Módulo de Evaluación y Priorización

* Estimación de impacto y gravedad mediante modelos de aprendizaje automático y reglas operativas.
* Priorización de incidentes para su presentación al operador.

### 🔹 Módulo de Apoyo a la Decisión

* Generación de informes de situación estructurados.
* Interfaz de usuario que permite al operador revisar, editar y confirmar la decisión.
* Registro de tiempos y acciones para la evaluación del TTFD.

👉 **No se implementa planificación automática completa ni asignación autónoma de recursos**, evitando riesgos éticos y manteniendo el foco en el apoyo a la decisión.

---

## 6. Metodología de trabajo

El trabajo se desarrollará siguiendo una **metodología iterativa e incremental**, adaptada a un equipo de **tres personas**, combinando principios ágiles (Scrum/Kanban) con hitos bien definidos.

Las fases principales serán:

1. **Análisis y diseño**

   * Revisión del estado del arte.
   * Definición de requisitos y métricas.
   * Diseño de la arquitectura.

2. **Implementación**

   * Desarrollo progresivo de los módulos.
   * Integración en una plataforma software única.

3. **Evaluación**

   * Definición de escenarios simulados de emergencias.
   * Medición del TTFD y análisis de resultados.

4. **Documentación y conclusiones**

   * Discusión crítica.
   * Identificación de limitaciones y trabajo futuro.

---

## 7. Tecnologías y técnicas previstas

* **Ingeniería Software:** Python (backend), interfaz web ligera, arquitectura modular.
* **NLP:** Transformers (BERT/RoBERTa), spaCy para NER.
* **Visión Artificial:** CNNs o U-Net con datasets abiertos (p. ej., incendios).
* **Machine Learning:** Modelos de clasificación/regresión con Scikit-learn.
* **Datos:** Datasets abiertos (UCI Repository, AEMET, repositorios públicos de imágenes).

---

## 8. Impacto social y Tech4Good

El sistema contribuye a:

* mejorar la respuesta temprana ante catástrofes,
* reducir la carga cognitiva de los operadores,
* optimizar la toma de decisiones iniciales en situaciones críticas.

El proyecto se concibe como una **herramienta de apoyo**, no de automatización total, alineándose con principios de **IA responsable, ética y Tech4Good**.

