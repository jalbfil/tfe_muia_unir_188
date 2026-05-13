# 🧠 PROMPT MAESTRO — PROTOTIPO MVP

## Sistema inteligente de apoyo a la decisión para puestos de mando de emergencias

---

### CONTEXTO GENERAL

Eres un **ingeniero de software senior especializado en sistemas críticos y aplicaciones de IA aplicada**.
Tu tarea es diseñar y generar un **primer prototipo funcional (MVP)** de una aplicación software para **apoyo a la toma de decisiones en puestos de mando de emergencias civiles**.

Este proyecto corresponde a un **Trabajo Fin de Estudios (TFE) de Máster en Inteligencia Artificial**, por lo que el sistema debe ser:

* técnicamente correcto,
* modular,
* evaluable,
* ético (humano en el bucle),
* y **deliberadamente acotado** (no sobre-ingeniería).

---

### OBJETIVO DEL SISTEMA

Construir un **MVP funcional** que permita:

1. Ingerir información de emergencia en **formato texto** (simulando avisos ciudadanos, informes, emails).
2. Estructurar esa información en **eventos operativos** mediante NLP.
3. Priorizar los eventos según criterios operativos simples.
4. Presentar los eventos en una **interfaz de puesto de mando**.
5. Permitir que un operador humano **revise y confirme** una primera decisión.
6. Registrar tiempos para medir **Time To First Decision (TTFD)**.

👉 El sistema **NO toma decisiones automáticamente**.
👉 La decisión solo existe cuando el operador confirma.

---

### ALCANCE DEL MVP (MUY IMPORTANTE)

Implementa **solo lo necesario** para un prototipo académico sólido:

✅ NLP básico (NER, extracción de localización y tipo de incidente)
✅ Priorización simple (reglas + score)
✅ Interfaz web mínima
✅ Registro de tiempos y eventos
❌ NO planificación automática compleja
❌ NO visión satelital pesada
❌ NO microservicios innecesarios

---

### ARQUITECTURA DESEADA

Arquitectura **modular monolítica** (para MVP):

* **Backend**: Python
* **Frontend**: Web simple (React / HTML + JS)
* **Persistencia**: SQLite
* **Comunicación**: API REST local

#### Módulos lógicos:

1. **Ingesta**

   * Entrada manual de texto (textarea).
2. **Procesamiento NLP**

   * Extracción de:

     * tipo de incidente (incendio, inundación, accidente, etc.),
     * ubicación (si existe),
     * señales de urgencia.
3. **Estructuración**

   * Conversión a objeto `Incident`.
4. **Priorización**

   * Score simple (urgencia + impacto).
5. **Apoyo a la decisión**

   * Vista de incidente estructurado.
   * Botón “Confirmar decisión”.
6. **Métricas**

   * Registro de:

     * tiempo de ingesta,
     * tiempo de confirmación,
     * cálculo de TTFD.

---

### MODELOS Y TÉCNICAS

* NLP:

  * spaCy o modelo ligero equivalente
  * NER para localización y entidades
* Priorización:

  * reglas deterministas (no ML complejo)
* Datos:

  * ejemplos simulados incluidos en el repositorio

---

### INTERFAZ (MVP)

Diseña **3 pantallas**:

1. **Entrada**

   * Campo de texto para introducir aviso.
   * Botón “Procesar”.
2. **Cola de incidentes**

   * Lista de incidentes detectados.
   * Indicador de prioridad.
3. **Detalle de incidente**

   * Información estructurada.
   * Botón “Confirmar decisión”.
   * Mostrar TTFD cuando se confirme.

Interfaz **funcional, no estética**.

---

### REQUISITOS ACADÉMICOS CLAVE

* Código claro y comentado.
* Arquitectura explicable en memoria.
* Fácil de extender en fases posteriores.
* Todo ejecutable **localmente**.
* Incluye README explicando:

  * cómo ejecutar,
  * qué mide,
  * cómo se evalúa TTFD.

---

### ENTREGABLE ESPERADO DE ESTE PROMPT

Genera:

1. Estructura de carpetas del proyecto.
2. Código backend funcional.
3. Interfaz web mínima conectada al backend.
4. Ejemplos de datos de entrada.
5. Explicación breve de la arquitectura.
6. Instrucciones para ejecutar el MVP localmente.

---

### PRINCIPIO FUNDAMENTAL (NO LO ROMPAS)

> **Este sistema apoya decisiones, no decide.
> El humano es el nodo final del sistema.**

---

## FIN DEL PROMPT
