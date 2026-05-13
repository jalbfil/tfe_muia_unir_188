

# **Arquitectura Multiagente GraphRAG Híbrido: Un Blueprint de Sistemas Basado en Seis Protocolos de Interoperabilidad de IA**

## **1\. Marco Conceptual y Fundamentos del Sistema Agente AGI**

La evolución de los modelos de lenguaje a sistemas autónomos y colaborativos exige una infraestructura que estandarice la comunicación y asegure la interoperabilidad a través de múltiples dominios y plataformas. La arquitectura propuesta se fundamenta en la colaboración multiagente y el uso de la Generación Aumentada por Recuperación basada en Grafos (GraphRAG) para proporcionar razonamiento complejo y explicable.

### **1.1. La Necesidad de Sistemas Multiagente Interoperables (La Visión "Internet de Agentes")**

La ambición de construir sistemas de Inteligencia General Artificial (AGI) requiere que los agentes de IA superen la fragmentación inherente a los *frameworks* propietarios.1 La visión de un "Internet de Agentes" solo puede realizarse mediante la adopción de protocolos abiertos que definan estructuras claras para la identidad, la comunicación y la delegación de tareas.

El sistema de protocolos seleccionado opera en capas complementarias, evitando la redundancia y maximizando la funcionalidad 3:

1. **MCP (Model Context Protocol):** Actúa en la capa más baja, conectando a los Modelos de Lenguaje Grande (LLMs) con herramientas externas y fuentes de datos. Se asemeja a un puerto de interconexión estandarizado, permitiendo a los LLMs acceder a contextos en tiempo real y capacidades específicas.5  
2. **A2A (Agent 2 Agent Protocol):** Gestiona la colaboración entre agentes pares, definiendo un ciclo de vida claro para las tareas (Task) y facilitando el descubrimiento de capacidades mediante estructuras de metadatos estandarizadas llamadas *Agent Cards*.7  
3. **ACP (Agent Communication Protocol):** Se enfoca en la orquestación de flujos de trabajo y la delegación de tareas a nivel de supervisor, aprovechando la simplicidad de las convenciones RESTful sobre HTTP.9

La implementación de esta arquitectura exige abordar un desafío crítico: el déficit de confianza verificable en un entorno distribuido.10 La interoperabilidad a través de fronteras de confianza debe estar respaldada por mecanismos de seguridad específicos del protocolo.

**ACP** introduce *Capability Tokens* (basados en firmas criptográficas) para la autorización granular.12

**SLIM** asegura la capa de transporte utilizando gRPC sobre HTTP/2, a menudo con Message Layer Security (MLS) para encriptación de extremo a extremo.14 Finalmente,

**ANP** proporciona la identidad descentralizada (W3C DID) requerida para la autenticación en redes abiertas.17 Estos mecanismos de seguridad son gestionados de forma centralizada por un

**Agent Gateway** que garantiza que las capacidades anunciadas (A2A) sean invocadas solo con la autorización verificada (ACP).19

### **1.2. GraphRAG como Paradigma de Razonamiento Estructurado y Explicable**

GraphRAG es fundamental para que el chatbot trascienda la mera recuperación de texto vectorial. Al transformar datos no estructurados en un grafo de conocimiento simbólico y relacional (nodos y relaciones), GraphRAG permite un razonamiento estructurado y, crucialmente, explicable, lo que es inviable en sistemas RAG puramente basados en vectores.20

Neo4j, como base de datos de grafos líder, soporta la organización flexible de datos, albergando tanto la estructura simbólica (nodos y relaciones) como los *embeddings* de texto (vectores).21 Esto permite al sistema de

**Razonamiento GraphRAG** realizar búsquedas híbridas, combinando la proximidad semántica (búsqueda vectorial) con el recorrido lógico del grafo (consultas Cypher).20 Además, herramientas como

Text2Cypher permiten que el LLM interno del agente traduzca las preguntas complejas del usuario a consultas Cypher específicas, aumentando la precisión del *retrieval*.24

### **1.3. La Estrategia de Framework: Leveraging MetaGPT X (MGX)**

El desarrollo del sistema multiagente se centrará en el framework MetaGPT X (MGX.dev) 25, que promueve la filosofía

Code \= SOP(Team).26 Esto significa que los roles de los agentes (Ingesta, Razonamiento, Orquestación) se definen mediante Procedimientos Operativos Estándar orquestados por LLMs.

Aunque MetaGPT maneja su comunicación interna mediante documentos estructurados 27, para lograr la interoperabilidad externa y la adhesión a los protocolos estándar (A2A, ACP, ANP), los agentes internos de MGX deben ser "envueltos" con implementaciones de protocolo. Por ejemplo, el SDK de ACP facilita exponer las funciones internas de un agente mediante un simple decorador

@server.agent(), lo que permite que el agente cumpla con el estándar RESTful sin modificar su lógica interna.9

## **2\. Arquitectura de Ingesta y Construcción Dinámica del Grafo de Conocimiento**

El **Agente de Ingesta y Construcción de Grafos** es el pilar de la calidad del conocimiento del sistema, manejando la transformación de datos no estructurados a una estructura GraphRAG escalable.

### **2.1. Configuración de Neo4j y Esquema Genérico de Grafo para RAG**

Neo4j se utilizará como la base de datos principal.21 Para que el GraphRAG funcione eficientemente, debe implementarse una estrategia de búsqueda híbrida que combine las consultas Cypher con la búsqueda por similitud vectorial.

#### **Configuración de Índices Vectoriales**

La base de datos debe estar configurada con índices vectoriales en las propiedades de los nodos que contienen *embeddings* de alta dimensión, generados a partir de los fragmentos de texto procesados (Chunks).

La creación de estos índices habilita la búsqueda de similitud semántica. La prescripción técnica requiere un índice en nodos, por ejemplo, los etiquetados como Chunk, utilizando la función de similitud coseno:

Este índice es vital, ya que permite al VectorCypherRetriever combinar búsquedas de proximidad semántica con travesías del grafo, enriqueciendo los resultados de la recuperación.23 Los

*embeddings* utilizados, como text-embedding-ada-002, deben ser de alta calidad y estar almacenados como propiedades del nodo.30

#### **Implementación de Text2Cypher**

El **Agente de Razonamiento GraphRAG** se basa en la capacidad de traducir la intención del usuario en consultas estructuradas de grafo. El Text2CypherRetriever delega esta traducción a un LLM.24 La precisión de este proceso depende intrínsecamente de que el LLM reciba un contexto de esquema de grafo explícito (nombres de nodos y relaciones) para evitar alucinaciones en la generación de Cypher.31 Por lo tanto, el Agente de Ingesta debe garantizar que el manifiesto del esquema de Neo4j esté actualizado y disponible (utilizando una función de

refresh\_schema) para ser inyectado en el *prompt* del LLM durante la fase de Text2Cypher.31

### **2.2. El Agente de Ingesta: Extracción Inteligente de Datos (Scraping y Enriquecimiento)**

El Agente de Ingesta utiliza herramientas especializadas que interactúan a través de protocolos estandarizados.

#### **ScrapeGraphAI para Extracción Estructurada**

Se emplea ScrapeGraphAI por su capacidad para utilizar LLMs en la extracción inteligente de datos estructurados (JSON) de contenido web y HTML.33 Herramientas como

SmartScraperTool o SmartCrawlerTool permiten al Agente de Ingesta recibir URLs y un *prompt* de lenguaje natural, devolviendo datos listos para su inyección estructurada en el grafo.34 Esta interacción con el LLM interno o con un Tool Server externo se gestiona mediante el

**Protocolo MCP**, donde SmartScraperTool se expone con un inputSchema y outputSchema definidos.35

#### **Diffbot para Enriquecimiento (Content Enrichment)**

Para garantizar que el grafo de conocimiento no solo contenga datos extraídos, sino información verificada y rica en relaciones, se integra Diffbot. Diffbot Knowledge Graph proporciona más de 15 tipos de entidades (Organización, Persona, Artículo, etc.) y las relaciones entre ellas a escala industrial, con una trazabilidad detallada de la procedencia de los datos.36

El flujo de trabajo es el siguiente: una vez que ScrapeGraphAI extrae entidades primarias, el Agente de Ingesta las pasa a la API de Diffbot para su enriquecimiento. Diffbot añade propiedades y relaciones verificadas al dato, que luego se traducen a comandos Cypher (CREATE y MERGE) para la construcción final del grafo en Neo4j.

Table 2: Arquitectura de Componentes de GraphRAG en Neo4j

| Componente de GraphRAG | Descripción Funcional | Tecnología Clave | Implementación Operativa Sugerida |
| :---- | :---- | :---- | :---- |
| Ingestión y Extracción de Entidades | Procesamiento de texto (PDF/Web) y mapeo de relaciones. | ScrapeGraphAI (MCP), LLM | Generación de comandos Cypher CREATE y MERGE optimizados. |
| Vector Index y Embeddings | Almacenamiento de representaciones semánticas del contenido. | Neo4j Vector Indexes | Índice en nodos (c:Chunk) para similitud cosine.29 |
| **Text2Cypher** | Traduce la pregunta del usuario a una consulta estructurada Cypher. | Neo4j Text2CypherRetriever | Llama a LLM con el esquema de grafo completo como contexto para generar consultas.23 |
| Razonamiento Híbrido | Combina resultados de búsqueda vectorial con recorrido de grafo. | VectorCypherRetriever | Asegura respuestas basadas en relaciones explícitas, mejorando la explicabilidad.20 |
| Deduplicación Semántica | Previene la ingesta de contenido conceptualmente redundante. | Embeddings (Transformer Models) \+ Vector DB/MinHash | Ejecutado por el Agente de Ingesta antes de la creación de Chunks.39 |

## **3\. Mecanismos de Optimización de Recursos y Calidad de Datos**

La eficiencia operativa es tan importante como la capacidad de respuesta. La optimización del sistema se centra en evitar el procesamiento y las llamadas a APIs redundantes.

### **3.1. Estrategias de Deduplicación Híbrida y Content Fingerprinting**

La deduplicación no puede limitarse a la comprobación de *hash* exacto (MD5) 40, ya que los grandes conjuntos de datos de LLM y RAG contienen frecuentemente

*near-duplicates* o contenido ligeramente parafraseado.41

El **Agente de Ingesta** implementará una estrategia híbrida de tres etapas:

1. **Fingerprinting Tradicional (Duplicados Exactos):** Se utiliza hashlib.md5 o similar en el contenido completo para una identificación rápida de duplicados idénticos.40  
2. **Fingerprinting Semántico (Duplicados Cercanos):** Para cada fragmento de contenido (*chunk*), se genera un vector de *embedding*.39  
3. **Detección de Similitud Acelerada:** Estos *embeddings* se comparan usando MinHash para la distancia Jaccard o Cosine Similarity.43 Si la similitud cae por encima de un umbral predefinido, el contenido se marca como redundante y no se procesa, ahorrando costos de LLM (MCP) y de almacenamiento en Neo4j.

### **3.2. Implementación del Caché Semántico (Utilizando Redis o similar)**

El caché semántico opera en la capa de **Agente de Orquestación** y es la primera línea de defensa contra consultas LLM repetitivas.

El proceso es como sigue: la consulta del usuario se convierte en un *embedding*.45 Este vector se compara con los vectores de consultas previamente resueltas almacenadas en un caché (ej. Redis o un vector store auxiliar).42 Si se encuentra un "cache hit" con una similitud por encima de un

distance\_threshold (ej. 0.1), la respuesta almacenada se devuelve inmediatamente.45 Esto reduce drásticamente la latencia de respuesta y minimiza los gastos asociados a las invocaciones repetitivas del LLM y del grafo GraphRAG.

### **3.3. Gestión del Crawl Budget y Actualizaciones Incrementales**

La escalabilidad del sistema se ve afectada por la necesidad de reconstruir constantemente el grafo. La estrategia consiste en realizar **Actualizaciones Incrementales**.43 Al combinar el

*Content Fingerprinting* con el almacenamiento de metadatos estructurales (fechas de ingesta, source system) 43, el Agente de Ingesta puede identificar con precisión qué documentos han sido modificados (delta updates). Solo las secciones cambiadas del grafo se actualizan o se re-procesan (vía ScrapeGraphAI/Diffbot/LLM), lo que optimiza el uso de recursos y minimiza los ciclos de LLM necesarios para el procesamiento de documentos (MCP).

Table 3: Componentes de Optimización de Ingesta de Datos

| Componente de Optimización | Agente Responsable | Función Técnica Clave | Impacto en el Sistema |
| :---- | :---- | :---- | :---- |
| Deduplicación Semántica | Agente de Ingesta | Utiliza MinHash / Embeddings para identificar contenido parafraseado o similar (fuzzy).39 | Reduce la redundancia del grafo, mejora la precisión de RAG, y ahorra costos de almacenamiento y LLM. |
| Cache Semántico | Agente de Orquestación | Vectorización de consultas y búsqueda de similitud en una capa de caché (Redis).45 | Acelera la respuesta al usuario y reduce drásticamente el uso de la API LLM para preguntas repetitivas.46 |
| Diffbot Enrichment | Agente de Ingesta | Añade metadatos y relaciones verificadas a las entidades extraídas.38 | Proporciona datos de alta calidad (*High-Quality Data*) para la construcción inicial del grafo. |

## **4\. El Fabric de Comunicación Multi-Protocolo (El Internet de Agentes)**

La arquitectura de comunicación se centraliza a través de un **Agent Gateway**, que actúa como mediador, traductor y garante de la seguridad entre los agentes que utilizan seis protocolos distintos. Este diseño mitiga la complejidad de la interoperabilidad punto a punto.19

### **4.1. Arquitectura del Agente Gateway y Registro de Servicios**

Inspirado en plataformas como agentgateway.dev, el Gateway provee un plano de control para la gobernanza de agentes y un plano de datos (Data Plane) seguro. Sus funciones incluyen mantener un registro de todos los agentes y sus capacidades (Agent Cards/Manifiestos), gestionar la seguridad mediante un sistema RBAC (Role-Based Access Control) y, fundamentalmente, enrutar el tráfico de mensajes de alta velocidad, idealmente utilizando **SLIM** en el plano de datos.19

### **4.2. Protocolo MCP (Model Context Protocol): Conexión LLM-a-Herramienta**

El MCP define cómo los LLMs invocan herramientas externas o acceden a datos estructurados.5 Los MCP Servers se definen mediante un archivo JSON (

mcp.json) que especifica las herramientas, el esquema de entrada (inputSchema) y el esquema de salida (outputSchema).35

El **Agente de Razonamiento** utiliza MCP para exponer capacidades específicas a su LLM interno, como el Text2Cypher Tool. Esto permite al LLM decidir contextualmente cuándo es necesario invocar la función de traducción a Cypher antes de consultar la base de datos Neo4j, asegurando que las capacidades se utilicen de manera autónoma.35

### **4.3. Protocolo A2A (Agent 2 Agent): Colaboración Peer-to-Peer**

A2A establece las reglas para el descubrimiento y la interacción directa entre agentes. Cada agente anuncia sus capacidades a través de una *Agent Card* (JSON) alojada en una URI conocida (/.well-known/agent.json).49 Esta tarjeta contiene detalles sobre el

*endpoint*, las capacidades, y los esquemas de autenticación necesarios.50

La unidad central de trabajo en A2A es el objeto Task, que sigue un ciclo de vida con estados definidos (submitted, working, completed).7 Las actualizaciones de estado para tareas de larga duración pueden ser transmitidas mediante Server-Sent Events (SSE).8 Es crucial reconocer que A2A define la estructura del trabajo, pero la confianza y seguridad de la interacción son provistas por otros protocolos. A pesar del soporte de A2A para redes descentralizadas 49, la implementación de producción requiere que el

**Agente de Orquestación** trate el *Agent Card* como información programática, pero la identidad subyacente y la autorización de la invocación provienen de ANP y ACP, respectivamente.11

Table 4: Estructura Prescriptiva de Agent Card (A2A/ANP Hybrid)

| Campo | Protocolo | Descripción Técnica | Significado en el Sistema |
| :---- | :---- | :---- | :---- |
| id | ANP/DID | Identificador descentralizado único (ej. did:web:agent-ingesta.example.com).17 | Proporciona identidad verificable y autenticación segura. |
| capabilities | A2A/MCP | Array de servicios disponibles, incluyendo esquemas de entrada/salida (JSON Schema).35 | Permite el descubrimiento programático de las funciones (ej. process\_pdf, run\_cypher). |
| endpoint | A2A | URL base para la recepción de solicitudes Task.8 | Define la ubicación de contacto REST/HTTP. |
| authSchemes | A2A/ACP | Métodos de autenticación requeridos (ej. apiKey, oauth2, capabilityTokens).13 | Guía al cliente (Orquestador) sobre cómo obtener y presentar el token de capacidad ACP. |
| status | A2A | Estado operativo actual del agente (live, maintenance).50 | Esencial para el registro y la federación del Agent Gateway. |

### **4.4. Protocolo ACP (Agent Communication Protocol): Orquestación Empresarial**

El protocolo ACP es la columna vertebral de la orquestación del **Agente de Orquestación**, debido a su diseño simple y neutral basado en RESTful APIs, lo que facilita su integración en entornos de producción.2 A diferencia de otros protocolos, ACP utiliza convenciones HTTP estándar, con la invocación de tareas mediante, por ejemplo,

HTTP POST /run.2

La característica de seguridad más importante de ACP es el uso de *Capability Tokens*.13 Estos tokens, que son objetos firmados (JWT), codifican explícitamente qué recursos y operaciones tiene permiso de ejecutar un agente. Al delegar una tarea, el

**Agente de Orquestación** adquiere y adjunta un token específico para la acción delegada (ej., una consulta de lectura Cypher), y el agente receptor (el **Agente de Razonamiento**) puede verificar el token de manera trivial, sin necesidad de complejos sistemas de políticas externas.12

### **4.5. Protocolo SLIM (Secure Low-Latency Interactive Messaging): Transporte Seguro**

SLIM es el protocolo de transporte de datos y mensajería de baja latencia diseñado específicamente para agentes de IA.16 Construido sobre

**gRPC sobre HTTP/2**, SLIM utiliza Protocol Buffers (Protobuf) para la serialización binaria de los mensajes, garantizando la velocidad y eficiencia necesarias para el *streaming* de grandes artefactos GraphRAG o logs de aprendizaje.15

SLIM soporta múltiples patrones de comunicación, incluyendo *request-response* y *streaming* bidireccional.15 La seguridad se garantiza mediante autenticación, autorización y encriptación de extremo a extremo, a menudo utilizando Message Layer Security (MLS).14 Esto lo convierte en el protocolo ideal para el Plano de Datos del Agent Gateway y para la comunicación entre agentes donde la integridad y privacidad de los datos son primordiales (ej. entre el Agente de Orquestación y el Agente de Aprendizaje).

### **4.6. Protocolo ANP (Agent Network Protocol): Identidad Descentralizada y Semántica**

ANP se concibe como el "HTTP de la era web de agentes".56 Su valor reside en dos capas: la capa de identidad y la capa semántica.

1. **Identidad Descentralizada (DIDs):** ANP emplea Decentralized Identifiers (DIDs) del W3C, garantizando que la identidad del agente no dependa de una única autoridad central. Esto es crucial para la confianza en un *Internet de Agentes* distribuido.17  
2. **Semántica (JSON-LD):** Utiliza JSON-LD (JSON for Linked Data) y vocabularios como schema.org para describir las capacidades y la información de los agentes con una alta riqueza semántica.18 Esto permite que el  
   **Agente de Aprendizaje** realice un descubrimiento avanzado, entendiendo el significado relacional de las capacidades de otros agentes más allá de una simple búsqueda de funciones.

### **4.7. Protocolo AGORA: Negociación Dinámica de Protocolos (Meta-Layer)**

AGORA, un meta-protocolo, introduce una capa de flexibilidad de inspiración AGI al permitir que los agentes LLM negocien el protocolo de comunicación a utilizar para una tarea específica.57 Esto es esencial para manejar tareas ambiguas o interacciones raras donde un protocolo predefinido (como ACP o A2A) podría ser ineficiente.58

El mecanismo principal es el **Protocol Document (PD)**, que se describe en lenguaje natural o código.59 El LLM del agente puede generar o modificar este PD para definir una rutina de intercambio de datos óptima

*antes* de que ocurra la comunicación real.58 Por ejemplo, el

**Agente de Razonamiento** podría utilizar AGORA para negociar un formato de salida de datos especializado (ej., un formato JSON/LD para análisis de relaciones complejas) con el **Agente de Aprendizaje** en una conversación de múltiples rondas, gestionando el estado mediante un conversationId.60

## **5\. Roles de Agentes y Flujos de Trabajo Integrados**

El sistema opera mediante cuatro agentes especializados, cada uno utilizando la combinación óptima de protocolos para sus tareas.

### **5.1. Agente de Ingesta y Construcción de Grafos (Arquitecto de Conocimiento)**

Este agente se encarga de la curación de datos y la creación de la estructura de conocimiento.

* **Tareas:** Procesamiento de documentos, extracción inteligente de la web (ScrapeGraphAI) 33, enriquecimiento de entidades (Diffbot) 38, aplicación de Deduplicación Semántica 39 y mantenimiento del esquema Neo4j.  
* **Protocolos:** Utiliza **MCP** para llamar a LLMs que realizan la extracción y el mapeo a grafo.35 Publica sus capacidades de ingesta a través de una  
  **A2A Agent Card** para el descubrimiento.49 Utiliza  
  **ANP** para asegurar su identidad con DIDs antes de aceptar tareas del Orquestador.18

### **5.2. Agente de Razonamiento GraphRAG (Analista Semántico)**

El corazón del sistema de respuesta y análisis.

* **Tareas:** Interpretar preguntas de lenguaje natural, traducirlas a consultas Cypher (*Text2Cypher*), ejecutar la recuperación híbrida (vectorial y relacional) en Neo4j 23, y generar respuestas basadas en el grafo.20  
* **Protocolos:** Usa **MCP** para exponer la función Text2Cypher como una herramienta al LLM.35 Emplea  
  **AGORA** si la consulta es compleja y requiere un formato de comunicación no estándar con otros agentes (ej., un formato de datos de evidencia negociado).57 Colabora con otros agentes según las estructuras de tarea definidas por A2A.

### **5.3. Agente de Orquestación (Supervisor AGI-Inspired)**

El director que gestiona el flujo de trabajo y garantiza la eficiencia.

* **Tareas:** Interceptar consultas, verificar el caché semántico 45, delegar tareas al agente de Razonamiento o Ingesta, gestionar la autorización de tareas y validar la calidad de las respuestas.3  
* **Protocolos:** Utiliza **ACP** como protocolo de delegación principal por su enfoque RESTful y la robustez de los *Capability Tokens* para autorizar las acciones delegadas.9 Consulta el registro a través de  
  **A2A** para descubrir las capacidades necesarias.8 Utiliza  
  **SLIM (gRPC)** para el enrutamiento seguro de mensajes y la recepción de grandes artefactos o flujos de logs.15

### **5.4. Agente de Aprendizaje y Adaptación (Evolucionador del Sistema)**

Este agente garantiza la mejora continua del sistema.

* **Tareas:** Analizar métricas de rendimiento y logs de interacción. Ajustar los hiperparámetros de búsqueda GraphRAG. Optimizar y refinar los *prompts* utilizados por *Text2Cypher*. Adaptar dinámicamente las configuraciones de protocolo.  
* **Protocolos:** Se comunica con el Orquestador y otros agentes para obtener datos de logs y rendimiento utilizando **SLIM** para la transmisión segura.16 Utiliza  
  **ANP** para autenticar las fuentes de datos durante el aprendizaje.17 Aprovecha  
  **AGORA** para sugerir o probar nuevos protocolos de comunicación basados en patrones de interacción para mejorar la eficiencia general del sistema.57

## **6\. Blueprint de Implementación y Requisitos Técnicos**

La implementación requiere un *stack* tecnológico que pueda manejar la complejidad de la comunicación multi-protocolo y las operaciones de GraphRAG.

### **6.1. Stack Tecnológico Final y Entorno Operacional**

| Capa Arquitectónica | Componentes Clave Prescritos | Función | Protocolos/Tecnologías de Soporte |
| :---- | :---- | :---- | :---- |
| **Framework de Agentes** | MetaGPT X (MGX.dev) 25 | Definición de Roles y SOPs. | Wrapper ACP/A2A para interoperabilidad externa. |
| **Data Plane / Transporte** | Agntcy SLIM (gRPC sobre HTTP/2) 15 | Comunicación segura, de baja latencia y *streaming*. | Protobuf, MLS Encryption.14 |
| **Grafo de Conocimiento** | Neo4j 5.x+ (Graph Database) 21 | Almacenamiento nativo de grafos, Vector Indexes. | Cypher, Text2Cypher, Embeddings. |
| **Caché y Mensajería** | Redis (Vector/Semantic Cache) 45 | Deduplicación de consultas LLM y almacenamiento temporal. | Cosine Similarity/Umbral de Distancia.46 |
| **Ingesta de Datos** | ScrapeGraphAI, Diffbot 33 | Extracción estructurada y enriquecimiento de entidades. | LLM (vía MCP), API REST. |
| **Orquestación/Gateway** | Agent Gateway (Rust/Proxy) 19 | Enrutamiento Multi-Protocolo, Registro (A2A/ANP), Traducción (OpenAPI a MCP). | ACP (REST), A2A (JSON), MCP. |

### **6.2. Diagrama de Conexión de Protocolos (Capas de Comunicación y Traducción)**

El sistema opera con una superposición de protocolos gestionada por el Agent Gateway, que facilita la comunicación heterogénea. Los LLMs internos de los agentes utilizan **MCP** para acceder a herramientas y datos. La colaboración entre agentes (ej., solicitar una tarea) se define mediante **A2A**. La orquestación y delegación de tareas se rige por **ACP** (RESTful), con el Agente de Orquestación gestionando los *Capability Tokens*.

La capa subyacente de Identidad se basa en **ANP** (DIDs/JSON-LD), y el transporte de datos se realiza en el Plano de Datos de **SLIM** (gRPC). **AGORA** opera como una capa meta, permitiendo la generación de Protocolos Documentales (PD) dinámicos entre agentes que necesitan una estructura de comunicación temporalmente optimizada.

### **6.3. Directrices de Seguridad y Despliegue**

La seguridad del sistema está intrínsecamente ligada a la implementación de los protocolos de identidad y autorización:

1. **Identidad:** El registro de agentes debe basarse en la implementación de **ANP** con W3C DIDs, asegurando una identidad descentralizada y verificable para cada entidad.17  
2. **Autorización Fina:** El Agente de Orquestación debe utilizar los *Capability Tokens* de **ACP** para autorizar explícitamente cada acción delegada. Esto evita que un agente comprometido pueda acceder a recursos fuera de su ámbito de tarea (ej. solo puede ejecutar run\_cypher\_query:read, no write).13  
3. **Transporte Seguro:** Toda la comunicación de datos sensibles, especialmente los *embeddings* o los resultados detallados del GraphRAG, deben utilizar la capa **SLIM (gRPC/MLS)** para garantizar la baja latencia y la encriptación de extremo a extremo.14  
4. **Despliegue:** Se recomienda el despliegue de los agentes utilizando contenedores (Docker/Kubernetes). Los agentes internos de MetaGPT X deben tener *wrappers* o *sidecars* dedicados para manejar la interfaz de los protocolos A2A, ACP y ANP, mientras que el Agent Gateway gestiona el enrutamiento seguro del Data Plane (SLIM) y la traducción de API a MCP.19

#### **Obras citadas**

1. Using ACP for AI Agent Interoperability: Building Multi-Agent Workflows \- IBM, fecha de acceso: octubre 3, 2025, [https://www.ibm.com/think/tutorials/acp-ai-agent-interoperability-building-multi-agent-workflows](https://www.ibm.com/think/tutorials/acp-ai-agent-interoperability-building-multi-agent-workflows)  
2. Agent Communication Protocol: Welcome, fecha de acceso: octubre 3, 2025, [https://agentcommunicationprotocol.dev/](https://agentcommunicationprotocol.dev/)  
3. Agentic AI Protocols: MCP, A2A, and ACP | by Manav Gupta | Medium, fecha de acceso: octubre 3, 2025, [https://medium.com/@manavg/agentic-ai-protocols-mcp-a2a-and-acp-ea0200eac18b](https://medium.com/@manavg/agentic-ai-protocols-mcp-a2a-and-acp-ea0200eac18b)  
4. AI Agent Ecosystem: A Guide to MCP, A2A, and Agent Communication Protocols \- Addepto, fecha de acceso: octubre 3, 2025, [https://addepto.com/blog/ai-agent-ecosystem-a-guide-to-mcp-a2a-and-agent-communication-protocols/](https://addepto.com/blog/ai-agent-ecosystem-a-guide-to-mcp-a2a-and-agent-communication-protocols/)  
5. Model Context Protocol, fecha de acceso: octubre 3, 2025, [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)  
6. Agentic MCP and A2A Architecture: A Comprehensive Guide | by Anil Jain | AI / ML Architect, fecha de acceso: octubre 3, 2025, [https://medium.com/@anil.jain.baba/agentic-mcp-and-a2a-architecture-a-comprehensive-guide-0ddf4359e152](https://medium.com/@anil.jain.baba/agentic-mcp-and-a2a-architecture-a-comprehensive-guide-0ddf4359e152)  
7. Agent2Agent: A practical guide to build agents \- Composio, fecha de acceso: octubre 3, 2025, [https://composio.dev/blog/agent2agent-a-practical-guide-to-build-agents](https://composio.dev/blog/agent2agent-a-practical-guide-to-build-agents)  
8. Agent2Agent (A2A) – awesome A2A agents, tools, servers & clients, all in one place. \- GitHub, fecha de acceso: octubre 3, 2025, [https://github.com/ai-boost/awesome-a2a](https://github.com/ai-boost/awesome-a2a)  
9. What is Agent Communication Protocol (ACP)? \- IBM, fecha de acceso: octubre 3, 2025, [https://www.ibm.com/think/topics/agent-communication-protocol](https://www.ibm.com/think/topics/agent-communication-protocol)  
10. Specification \- Model Context Protocol, fecha de acceso: octubre 3, 2025, [https://modelcontextprotocol.io/specification/latest](https://modelcontextprotocol.io/specification/latest)  
11. a2aproject/a2a-samples: Samples using the Agent2Agent (A2A) Protocol \- GitHub, fecha de acceso: octubre 3, 2025, [https://github.com/a2aproject/a2a-samples](https://github.com/a2aproject/a2a-samples)  
12. ACP (Agent Communication Protocol) · i-am-bee acp · Discussion \#122 \- GitHub, fecha de acceso: octubre 3, 2025, [https://github.com/i-am-bee/acp/discussions/122](https://github.com/i-am-bee/acp/discussions/122)  
13. IBM's Agent Communication Protocol (ACP): A technical overview for software engineers, fecha de acceso: octubre 3, 2025, [https://workos.com/blog/ibm-agent-communication-protocol-acp](https://workos.com/blog/ibm-agent-communication-protocol-acp)  
14. SLIM: Securing AI Agent Communication with MLS \- wolfSSL, fecha de acceso: octubre 3, 2025, [https://www.wolfssl.com/slim-securing-ai-agent-communication-with-mls/](https://www.wolfssl.com/slim-securing-ai-agent-communication-with-mls/)  
15. agntcy/slim: Secure Low-Latency Interactive Messaging \- GitHub, fecha de acceso: octubre 3, 2025, [https://github.com/agntcy/slim](https://github.com/agntcy/slim)  
16. Secure Low-Latency Interactive Messaging (SLIM) \- Agntcy, fecha de acceso: octubre 3, 2025, [https://docs.agntcy.org/messaging/slim-core/](https://docs.agntcy.org/messaging/slim-core/)  
17. A Survey of Agent Interoperability Protocols: Model Context Protocol (MCP), Agent Communication Protocol (ACP), Agent-to-Agent Protocol (A2A), and Agent Network Protocol (ANP) \- arXiv, fecha de acceso: octubre 3, 2025, [https://arxiv.org/html/2505.02279v2](https://arxiv.org/html/2505.02279v2)  
18. ANP Getting Started Guide \- Agent Network Protocol, fecha de acceso: octubre 3, 2025, [https://agent-network-protocol.com/guide/](https://agent-network-protocol.com/guide/)  
19. agentgateway/agentgateway: Next Generation Agentic Proxy for AI Agents and MCP servers \- GitHub, fecha de acceso: octubre 3, 2025, [https://github.com/agentgateway/agentgateway](https://github.com/agentgateway/agentgateway)  
20. RAG Tutorial: How to Build a RAG System on a Knowledge Graph \- Neo4j, fecha de acceso: octubre 3, 2025, [https://neo4j.com/blog/developer/rag-tutorial/](https://neo4j.com/blog/developer/rag-tutorial/)  
21. GraphRAG Developer Guide \- Neo4j, fecha de acceso: octubre 3, 2025, [https://neo4j.com/developer/genai-ecosystem/](https://neo4j.com/developer/genai-ecosystem/)  
22. Enhancing the Accuracy of RAG Applications With Knowledge Graphs \- Neo4j, fecha de acceso: octubre 3, 2025, [https://neo4j.com/blog/developer/enhance-rag-knowledge-graph/](https://neo4j.com/blog/developer/enhance-rag-knowledge-graph/)  
23. User Guide: RAG — neo4j-graphrag-python documentation, fecha de acceso: octubre 3, 2025, [https://neo4j.com/docs/neo4j-graphrag-python/current/user\_guide\_rag.html](https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_rag.html)  
24. Effortless RAG With Text2CypherRetriever | by Will Tai | Neo4j Developer Blog \- Medium, fecha de acceso: octubre 3, 2025, [https://medium.com/neo4j/effortless-rag-with-text2cypherretriever-cb1a781ca53c](https://medium.com/neo4j/effortless-rag-with-text2cypherretriever-cb1a781ca53c)  
25. FoundationAgents/MetaGPT: The Multi-Agent Framework: First AI Software Company, Towards Natural Language Programming \- GitHub, fecha de acceso: octubre 3, 2025, [https://github.com/FoundationAgents/MetaGPT](https://github.com/FoundationAgents/MetaGPT)  
26. MetaGPT: The Multi-Agent Framework, fecha de acceso: octubre 3, 2025, [https://docs.deepwisdom.ai/main/en/guide/get\_started/introduction.html](https://docs.deepwisdom.ai/main/en/guide/get_started/introduction.html)  
27. What is MetaGPT ? | IBM, fecha de acceso: octubre 3, 2025, [https://www.ibm.com/think/topics/metagpt](https://www.ibm.com/think/topics/metagpt)  
28. Neo4j GraphRAG for Python \- GitHub, fecha de acceso: octubre 3, 2025, [https://github.com/neo4j/neo4j-graphrag-python](https://github.com/neo4j/neo4j-graphrag-python)  
29. Vector indexes \- Cypher Manual \- Neo4j, fecha de acceso: octubre 3, 2025, [https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/vector-indexes/](https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/vector-indexes/)  
30. Using OpenAI semantic search with Neo4J | by Eranga Dulshan \- Medium, fecha de acceso: octubre 3, 2025, [https://erangad.medium.com/using-openai-semantic-search-with-neo4j-8cab050ee553](https://erangad.medium.com/using-openai-semantic-search-with-neo4j-8cab050ee553)  
31. Generating Cypher Queries With ChatGPT 4 on Any Graph Schema \- Neo4j, fecha de acceso: octubre 3, 2025, [https://neo4j.com/blog/developer/generating-cypher-queries-with-chatgpt-4-on-any-graph-schema/](https://neo4j.com/blog/developer/generating-cypher-queries-with-chatgpt-4-on-any-graph-schema/)  
32. Towards agentic Graph RAG: Enhancing graph retrieval with vector search \- Blog \- Kuzu, fecha de acceso: octubre 3, 2025, [https://blog.kuzudb.com/post/enhancing-graph-rag-with-vector-search/](https://blog.kuzudb.com/post/enhancing-graph-rag-with-vector-search/)  
33. ScrapeGraphAI: Introduction, fecha de acceso: octubre 3, 2025, [https://docs.scrapegraphai.com/](https://docs.scrapegraphai.com/)  
34. ScrapeGraph \- ️ LangChain, fecha de acceso: octubre 3, 2025, [https://python.langchain.com/docs/integrations/tools/scrapegraph/](https://python.langchain.com/docs/integrations/tools/scrapegraph/)  
35. Tools \- Model Context Protocol, fecha de acceso: octubre 3, 2025, [https://modelcontextprotocol.io/docs/concepts/tools](https://modelcontextprotocol.io/docs/concepts/tools)  
36. Search (DQL) Basics \- Diffbot Docs, fecha de acceso: octubre 3, 2025, [https://docs.diffbot.com/docs/tutorial-quickstart-with-knowledge-graph-search](https://docs.diffbot.com/docs/tutorial-quickstart-with-knowledge-graph-search)  
37. Knowledge Graph Entity \- Diffbot Blog, fecha de acceso: octubre 3, 2025, [https://blog.diffbot.com/knowledge-graph-glossary/knowledge-graph-entity/](https://blog.diffbot.com/knowledge-graph-glossary/knowledge-graph-entity/)  
38. The Knowledge Graph of the Public Web \- Diffbot, fecha de acceso: octubre 3, 2025, [https://www.diffbot.com/products/knowledge-graph/](https://www.diffbot.com/products/knowledge-graph/)  
39. Beyond MD5: Implementing transformer-based fuzzy deduplication for unstructured datasets at scale on AWS | by Banavalikar | Medium, fecha de acceso: octubre 3, 2025, [https://medium.com/@banavalikar/beyond-md5-implementing-transformer-based-fuzzy-deduplication-for-unstructured-datasets-at-scale-6ebff328da98](https://medium.com/@banavalikar/beyond-md5-implementing-transformer-based-fuzzy-deduplication-for-unstructured-datasets-at-scale-6ebff328da98)  
40. Spoiler Alert: The Magic of RAG Does Not Come from AI | by Frank Wittkampf \- Medium, fecha de acceso: octubre 3, 2025, [https://medium.com/data-science/spoiler-alert-the-magic-of-rag-does-not-come-from-ai-8a0ed2ad4800](https://medium.com/data-science/spoiler-alert-the-magic-of-rag-does-not-come-from-ai-8a0ed2ad4800)  
41. How I Optimized a C++ Text Deduplication Engine for LLM from a 10x to a 100x Speedup: My Day-Long Battle with 4 Hellish Bugs | by Conanhujinming \- Medium, fecha de acceso: octubre 3, 2025, [https://medium.com/@conanhujinming/how-i-optimized-a-c-deduplication-engine-from-a-10x-to-a-100x-speedup-my-day-long-battle-with-4-5b10dd40e97b](https://medium.com/@conanhujinming/how-i-optimized-a-c-deduplication-engine-from-a-10x-to-a-100x-speedup-my-day-long-battle-with-4-5b10dd40e97b)  
42. Build a Semantic Cache That Cuts RAG Costs in Half: A Developer's Guide | by Elvin Gomez, fecha de acceso: octubre 3, 2025, [https://medium.com/@elvingomez/build-a-semantic-cache-for-rag-slash-response-times-by-90-and-save-24k-month-24e473734519](https://medium.com/@elvingomez/build-a-semantic-cache-for-rag-slash-response-times-by-90-and-save-24k-month-24e473734519)  
43. Build an unstructured data pipeline for RAG \- Azure Databricks | Microsoft Learn, fecha de acceso: octubre 3, 2025, [https://learn.microsoft.com/en-us/azure/databricks/generative-ai/tutorials/ai-cookbook/quality-data-pipeline-rag](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/tutorials/ai-cookbook/quality-data-pipeline-rag)  
44. Deduplication and Author Disambiguation of Streaming Records via Supervised Models \-Reza Karimi \- YouTube, fecha de acceso: octubre 3, 2025, [https://www.youtube.com/watch?v=so4rkI3aXUY](https://www.youtube.com/watch?v=so4rkI3aXUY)  
45. Implementing Semantic Caching in RAG Using Redis for Faster Responses \- Medium, fecha de acceso: octubre 3, 2025, [https://medium.com/@yashpaddalwar/implementing-semantic-caching-in-rag-using-redis-for-faster-responses-b901bcc8324b](https://medium.com/@yashpaddalwar/implementing-semantic-caching-in-rag-using-redis-for-faster-responses-b901bcc8324b)  
46. Improving RAG Applications with Semantic Caching and RAGAS \- All Things Open 2024, fecha de acceso: octubre 3, 2025, [https://2024.allthingsopen.org/improving-rag-applications-with-semantic-caching-and-ragas](https://2024.allthingsopen.org/improving-rag-applications-with-semantic-caching-and-ragas)  
47. agentgateway | Agent Connectivity Solved, fecha de acceso: octubre 3, 2025, [https://agentgateway.dev/](https://agentgateway.dev/)  
48. Use MCP servers in VS Code, fecha de acceso: octubre 3, 2025, [https://code.visualstudio.com/docs/copilot/customization/mcp-servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)  
49. AgentCard – Agent2Agent Protocol \- The A2A Protocol Community, fecha de acceso: octubre 3, 2025, [https://agent2agent.info/docs/concepts/agentcard/](https://agent2agent.info/docs/concepts/agentcard/)  
50. Agent Registry \- Proposal · a2aproject A2A · Discussion \#741 \- GitHub, fecha de acceso: octubre 3, 2025, [https://github.com/a2aproject/A2A/discussions/741](https://github.com/a2aproject/A2A/discussions/741)  
51. Decentralized Identifiers (DIDs) v1.0 \- W3C, fecha de acceso: octubre 3, 2025, [https://www.w3.org/TR/did-1.0/](https://www.w3.org/TR/did-1.0/)  
52. i-am-bee/acp: Open protocol for communication between AI agents, applications, and humans. \- GitHub, fecha de acceso: octubre 3, 2025, [https://github.com/i-am-bee/acp](https://github.com/i-am-bee/acp)  
53. Token exchange \- IBM Security Verify, fecha de acceso: octubre 3, 2025, [https://docs.verify.ibm.com/verify/docs/oauth-20-token-exchange](https://docs.verify.ibm.com/verify/docs/oauth-20-token-exchange)  
54. What Is gRPC? | IBM, fecha de acceso: octubre 3, 2025, [https://www.ibm.com/think/topics/grpc](https://www.ibm.com/think/topics/grpc)  
55. Core concepts, architecture and lifecycle \- gRPC, fecha de acceso: octubre 3, 2025, [https://grpc.io/docs/what-is-grpc/core-concepts/](https://grpc.io/docs/what-is-grpc/core-concepts/)  
56. What Are AI Agent Protocols? \- IBM, fecha de acceso: octubre 3, 2025, [https://www.ibm.com/think/topics/ai-agent-protocols](https://www.ibm.com/think/topics/ai-agent-protocols)  
57. A Scalable Communication Protocol for Networks of Large Language Models \- arXiv, fecha de acceso: octubre 3, 2025, [https://arxiv.org/abs/2410.11905](https://arxiv.org/abs/2410.11905)  
58. Comparative Analysis of Open-Source Agent Communication Protocols: MCP, ANP, Agora, agents.json, LMOS, and AITP | by Shan Chang | Medium, fecha de acceso: octubre 3, 2025, [https://medium.com/@changshan/comparative-analysis-of-open-source-agent-communication-protocols-mcp-anp-agora-agents-json-e29dbd213e59](https://medium.com/@changshan/comparative-analysis-of-open-source-agent-communication-protocols-mcp-anp-agora-agents-json-e29dbd213e59)  
59. Comparative Analysis of Open-Source Agent Communication Protocols: MCP, ANP, Agora, agents.json, LMOS, and AITP, fecha de acceso: octubre 3, 2025, [https://agent-network-protocol.com/blogs/posts/agent-communication-protocols-comparison.html](https://agent-network-protocol.com/blogs/posts/agent-communication-protocols-comparison.html)  
60. Beginner-Friendly Specification \- Agora Protocol, fecha de acceso: octubre 3, 2025, [https://agoraprotocol.org/docs/protocol/beginner-friendly](https://agoraprotocol.org/docs/protocol/beginner-friendly)  
61. Getting Started \- Agora Protocol, fecha de acceso: octubre 3, 2025, [https://agoraprotocol.org/docs/getting-started](https://agoraprotocol.org/docs/getting-started)