Anexo B. Matriz detallada de variables de priorización
B.1. Finalidad del anexo
Este anexo constituye la especificación maestra de las variables que utiliza el motor de priorización del sistema. Su finalidad es triple: documentar con precisión cada variable para garantizar la trazabilidad metodológica del motor, proporcionar al tribunal una referencia completa que permita verificar la coherencia entre el diseño analítico (Capítulo 6), el diseño de datos (Capítulo 7) y la implementación del prototipo (Capítulo 8), y servir como guía de implementación para la codificación de cada variable en el sistema.
Para cada variable se documenta su identificador, nombre, definición operativa, grupo funcional, tipo de dato, valores posibles, fuente principal de obtención, método de captura, papel dentro de la arquitectura del baseline interpretable, justificación normativa u operativa y observaciones relevantes.
El contenido de este anexo despliega con mayor nivel de detalle técnico lo ya establecido en la Tabla 6.2 del Capítulo 6 (matriz resumida de variables). No introduce variables nuevas ni modifica la lógica del motor; expande la información necesaria para la implementación, la trazabilidad y la defensa ante tribunal.
B.2. Criterios de selección de variables
La selección de las quince variables de entrada del motor se ha guiado por cuatro criterios complementarios, establecidos en el apartado 6.3 del Capítulo 6:
Respaldo normativo u oficial. Cada variable debe poder vincularse a un concepto, criterio o indicador reconocido en la normativa de protección civil o en las fuentes oficiales del dominio. Esto garantiza que el motor no opera sobre abstracciones arbitrarias, sino sobre criterios trazables y defendibles.
Impacto esperado sobre la prioridad. La variable debe aportar información discriminante para la urgencia operativa del incidente. Variables que no contribuyen a diferenciar prioridades entre incidentes no justifican su inclusión.
Viabilidad de obtención en los primeros minutos. El motor opera en el momento de la primera decisión. Por tanto, solo se incluyen variables que puedan obtenerse de forma razonable durante la fase inicial del incidente: a través de la comunicación del alertante, mediante consulta automática a fuentes oficiales o por cruce geoespacial.
No redundancia. Cada variable debe medir una dimensión distinta del incidente. Se ha evitado incluir variables que capturen información ya representada por otra, lo que reduciría la interpretabilidad del motor y podría distorsionar el scoring por doble conteo.
Adicionalmente, se distingue de forma rigurosa entre variables de entrada y variables derivadas. Las quince variables de entrada son datos que el sistema recibe o consulta; las cuatro variables derivadas son resultados intermedios calculados por el propio motor a partir de las entradas. Esta distinción es esencial para evitar circularidades en la lógica del sistema y para mantener la transparencia del diseño.

B.3. Matriz detallada de variables de entrada
La siguiente tabla presenta la especificación completa de las quince variables de entrada del motor, organizadas según los seis grupos funcionales definidos en el Capítulo 6: gravedad inmediata (V01–V03), vulnerabilidad y exposición (V05–V07), amenaza contextual (V08–V11), escalado y evolución (V04, V12), calidad de la información (V13–V14) y contexto operativo (V15).
V01. Riesgo vital inmediato
ID
V01
Nombre de la variable
Riesgo vital inmediato
Definición operativa
Indica si existe peligro de muerte inminente para una o más personas en el momento de la comunicación.
Grupo funcional
Gravedad inmediata
Tipo de dato
Binaria
Valores posibles
Sí / No
Fuente principal
Comunicación inicial del alertante
Método de obtención
Extracción directa del relato o estructuración NLP del texto de entrada
Papel en el motor
Regla dura (RD1: V01=Sí → P1 fija)
Justificación normativa u operativa
Principio de protección de la vida (Ley 17/2015 art. 1; Ley 4/2024 art. 3). El riesgo vital constituye el criterio de máxima prioridad en todo el sistema de protección civil.
Observaciones
Variable con mayor impacto en el motor. Su activación impide cualquier rebaja de prioridad por factores secundarios.


V02. Víctimas confirmadas o probables
ID
V02
Nombre de la variable
Víctimas confirmadas o probables
Definición operativa
Número estimado de personas con daño físico confirmado o altamente probable, codificado en rangos ordinales para tolerar la imprecisión de la información temprana.
Grupo funcional
Gravedad inmediata
Tipo de dato
Ordinal
Valores posibles
0 / 1–2 / 3–10 / >10
Fuente principal
Comunicación inicial del alertante
Método de obtención
Extracción del relato, clasificación en rango
Papel en el motor
Regla dura + scoring (RD2: ≥3 → P2 mín.; RD5: >10 → P1 mín.); peso en scoring de gravedad
Justificación normativa u operativa
Lógica de activación por múltiples víctimas coherente con umbrales de AMV y con los criterios de escalado del PLATEAR.
Observaciones
La codificación en rangos es una decisión de diseño del prototipo para operar con información imprecisa. Los umbrales 3 y 10 se basan en la experiencia operativa de coordinación.


V03. Tipo de daño principal
ID
V03
Nombre de la variable
Tipo de daño principal
Definición operativa
Categoría del daño predominante observado o esperado: daño a personas, a bienes, al medioambiente o ausencia de daño aparente.
Grupo funcional
Gravedad inmediata
Tipo de dato
Categórica
Valores posibles
Personas / Bienes / Medioambiente / Sin daño
Fuente principal
Comunicación inicial del alertante
Método de obtención
Clasificación a partir del relato o selección por el operador
Papel en el motor
Scoring (ponderación diferenciada según categoría: Personas > Bienes > Medioambiente > Sin daño)
Justificación normativa u operativa
Ley 17/2015 art. 1: la protección civil protege personas, bienes y medioambiente. Ley 4/2024 art. 3: jerarquía de protección.
Observaciones
La jerarquía Personas > Bienes > Medioambiente es coherente con el principio de protección de la vida y no implica que el daño medioambiental sea irrelevante.



V04. Tipo de incidente
ID
V04
Nombre de la variable
Tipo de incidente
Definición operativa
Categoría del incidente según la taxonomía operativa del sistema, organizada en dos niveles: emergencias de protección civil (Nivel 1) y emergencias operativas ordinarias (Nivel 2).
Grupo funcional
Escalado
Tipo de dato
Categórica
Valores posibles
Valores de la taxonomía operativa (Cap. 3)
Fuente principal
Comunicación inicial / estructuración del incidente
Método de obtención
Clasificación automática o manual según taxonomía
Papel en el motor
Activación de contexto + scoring (determina qué variables contextuales se consultan y qué reglas aplican)
Justificación normativa u operativa
Catálogo de riesgos de la Norma Básica de Protección Civil (RD 524/2023); planes especiales de Aragón (PROCINFO, PROCINAR, PROCIFEMAR, PROCIMER).
Observaciones
Variable estructural del motor: no puntúa directamente gravedad, sino que condiciona qué contexto es pertinente y qué reglas duras pueden activarse.


V05. Población vulnerable
ID
V05
Nombre de la variable
Población vulnerable
Definición operativa
Presencia confirmada o probable de colectivos especialmente sensibles: menores, personas mayores, personas con discapacidad u otros grupos vulnerables en la zona del incidente.
Grupo funcional
Vulnerabilidad
Tipo de dato
Binaria
Valores posibles
Sí / No
Fuente principal
Comunicación inicial / contexto oficial (INE, cartografía)
Método de obtención
Declaración del alertante, cruce con datos censales o localización de centros sensibles
Papel en el motor
Scoring (incrementa puntuación en el grupo de vulnerabilidad)
Justificación normativa u operativa
Ley 4/2024 art. 6.2: atención especial a colectivos vulnerables. Ley 17/2015: protección reforzada.
Observaciones
Su combinación con V06 y V07 permite modular la exposición real. Activa regla RD6 cuando se trata de búsqueda de menor o persona vulnerable.


V06. Personas en riesgo estimadas
ID
V06
Nombre de la variable
Personas en riesgo estimadas
Definición operativa
Estimación del número de personas que podrían verse afectadas por la evolución del incidente, aunque aún no exista daño confirmado. Codificada en rangos ordinales.
Grupo funcional
Exposición
Tipo de dato
Ordinal
Valores posibles
0 / 1–10 / 11–100 / >100
Fuente principal
Comunicación inicial / contexto oficial (INE, ICEARAGON)
Método de obtención
Declaración del alertante, cruce con datos demográficos por zona
Papel en el motor
Scoring (ponderación creciente según rango)
Justificación normativa u operativa
PLATEAR: los criterios de activación consideran el número de personas potencialmente afectadas como indicador de magnitud.
Observaciones
Complementa V02 (víctimas ya confirmadas) con una perspectiva prospectiva. Los rangos permiten operar con estimaciones gruesas propias de la fase inicial.



V07. Emplazamiento crítico
ID
V07
Nombre de la variable
Emplazamiento crítico
Definición operativa
Identifica si el incidente afecta o se localiza en un emplazamiento de especial sensibilidad operativa: centro sanitario, educativo, residencia, infraestructura esencial u otro.
Grupo funcional
Vulnerabilidad
Tipo de dato
Categórica
Valores posibles
Sanitario / Educativo / Residencia / Infraestructura / Otro / No
Fuente principal
Comunicación inicial / cartografía oficial (ICEARAGON)
Método de obtención
Declaración del alertante o cruce geoespacial con capas de equipamientos
Papel en el motor
Scoring (incremento diferenciado según tipo de emplazamiento)
Justificación normativa u operativa
PLATEAR cap. 2: infraestructuras relevantes. Ley 4/2024: protección de servicios esenciales.
Observaciones
Su valor «No» no reduce la prioridad; simplemente no añade el incremento que sí aportan los emplazamientos críticos.


V08. Nivel de aviso AEMET
ID
V08
Nombre de la variable
Nivel de aviso AEMET
Definición operativa
Nivel de aviso meteorológico vigente emitido por la Agencia Estatal de Meteorología para la zona del incidente en el momento de la evaluación.
Grupo funcional
Amenaza contextual
Tipo de dato
Ordinal
Valores posibles
Verde / Amarillo / Naranja / Rojo
Fuente principal
AEMET OpenData (API oficial)
Método de obtención
Consulta automática a la API de AEMET OpenData
Papel en el motor
Regla dura + scoring (RD3: rojo + coherencia con tipo → P2 mín.; RD8: naranja/rojo + incendio IUF → P2 mín.); peso en scoring contextual
Justificación normativa u operativa
PROCIFEMAR: vincula niveles AEMET con fases de emergencia. Directriz Básica de Inundaciones: umbrales de activación.
Observaciones
Solo se activa como regla dura cuando existe coherencia con el tipo de incidente, evitando que un aviso genérico infle artificialmente la prioridad de incidentes no relacionados.


V09. Fenómeno meteorológico activo
ID
V09
Nombre de la variable
Fenómeno meteorológico activo
Definición operativa
Identifica el fenómeno meteorológico específico relevante para el incidente: viento, lluvia, nieve, temperatura extrema, tormenta o ninguno.
Grupo funcional
Amenaza contextual
Tipo de dato
Categórica
Valores posibles
Viento / Lluvia / Nieve / Temperatura / Tormenta / Ninguno
Fuente principal
AEMET OpenData (API oficial)
Método de obtención
Consulta automática a la API de AEMET OpenData
Papel en el motor
Scoring condicionado (pondera solo cuando es coherente con V04 y V08)
Justificación normativa u operativa
PROCIFEMAR: define fases de emergencia por tipo de fenómeno. PROCINAR: precipitación como indicador de riesgo hidrológico.
Observaciones
Su contribución al scoring está condicionada: solo se aplica cuando el fenómeno es pertinente para el tipo de incidente. Esto evita ruido en la priorización.



V10. Peligrosidad por inundación
ID
V10
Nombre de la variable
Peligrosidad por inundación
Definición operativa
Indica si la localización del incidente se encuentra dentro de una zona de peligrosidad por inundación oficialmente cartografiada por el SNCZI.
Grupo funcional
Amenaza contextual
Tipo de dato
Binaria
Valores posibles
Sí / No
Fuente principal
SNCZI / MITECO (cartografía oficial)
Método de obtención
Cruce geoespacial de la localización del incidente con capas GeoJSON del SNCZI
Papel en el motor
Scoring (incremento en amenaza contextual cuando V10=Sí y el incidente es de naturaleza hidrológica)
Justificación normativa u operativa
Directriz Básica ante Riesgo de Inundaciones; PROCINAR: clasifica zonas por nivel de riesgo.
Observaciones
No refleja el estado hidrológico en tiempo real, sino la peligrosidad histórica cartografiada. Su valor es contextual y complementa a V08 y V09.


V11. Presencia de instalación Seveso
ID
V11
Nombre de la variable
Presencia de instalación Seveso
Definición operativa
Indica si el incidente se ubica en el entorno de influencia de una instalación industrial sujeta a la normativa Seveso (RD 840/2015).
Grupo funcional
Amenaza contextual
Tipo de dato
Binaria
Valores posibles
Sí / No
Fuente principal
Registro oficial de establecimientos Seveso (DGPCyE / datos.gob.es)
Método de obtención
Cruce geoespacial de la localización con el registro público de instalaciones Seveso
Papel en el motor
Regla dura + scoring (RD4: Seveso + afectación directa confirmada → P1 mín.); peso en scoring contextual
Justificación normativa u operativa
RD 840/2015 (transposición Seveso III). Norma Básica de Protección Civil: riesgo químico como riesgo catalogado.
Observaciones
La regla dura RD4 exige afectación directa confirmada, no solo proximidad. El scoring añade un incremento moderado por proximidad sin afectación directa.


V12. Tendencia del incidente
ID
V12
Nombre de la variable
Tendencia del incidente
Definición operativa
Valoración de la evolución temporal del incidente: si mejora, se mantiene estable, empeora o si la tendencia es desconocida.
Grupo funcional
Escalado
Tipo de dato
Ordinal
Valores posibles
Mejoría / Estable / Agravamiento / Desconocida
Fuente principal
Comunicación inicial / parte de servicio / actualizaciones
Método de obtención
Declaración del alertante, informes de servicios intervinientes
Papel en el motor
Scoring (la tendencia de agravamiento incrementa la puntuación; la tendencia desconocida aplica precaución moderada)
Justificación normativa u operativa
PLATEAR: la evolución del incidente condiciona el nivel de activación y los criterios de escalado.
Observaciones
La tendencia «desconocida» no equivale a «agravamiento»; recibe un tratamiento intermedio conforme al principio de precaución razonable de la guía de etiquetado.



V13. Fiabilidad del informador
ID
V13
Nombre de la variable
Fiabilidad del informador
Definición operativa
Tipo de fuente de la comunicación inicial, que modula la confianza del sistema en la información recibida.
Grupo funcional
Calidad de la información
Tipo de dato
Ordinal
Valores posibles
Alta (fuente oficial o agente) / Media (testigo directo) / Baja (fuente indirecta o anónima)
Fuente principal
Comunicación inicial al 112
Método de obtención
Clasificación por el operador según el origen de la llamada
Papel en el motor
Confianza (no pondera scoring de urgencia, sino que modula el nivel de confianza de la recomendación)
Justificación normativa u operativa
Protocolos de calidad del 112. ISO 9001 aplicada a centros de coordinación.
Observaciones
No reduce ni eleva la prioridad directamente; ajusta la confianza. Un incidente grave reportado por fuente anónima mantiene su prioridad, pero con confianza reducida.


V14. Número de avisos simultáneos
ID
V14
Nombre de la variable
Número de avisos simultáneos
Definición operativa
Cantidad de comunicaciones independientes recibidas sobre el mismo incidente o incidentes relacionados en la misma zona temporal y espacial.
Grupo funcional
Calidad de la información
Tipo de dato
Numérica agrupada
Valores posibles
1 / 2–3 / >3
Fuente principal
Registro de avisos del sistema
Método de obtención
Conteo automático de comunicaciones asociadas al mismo evento
Papel en el motor
Confianza (múltiples avisos independientes refuerzan la verosimilitud del evento)
Justificación normativa u operativa
Lógica operativa de confirmación de eventos: la convergencia de múltiples fuentes reduce la incertidumbre.
Observaciones
Un único aviso no invalida el incidente, pero múltiples avisos independientes elevan la confianza del motor en la información disponible.


V15. Accesibilidad al punto
ID
V15
Nombre de la variable
Accesibilidad al punto
Definición operativa
Dificultad estimada de acceso al lugar del incidente para los servicios de emergencia, considerando infraestructura viaria, orografía y condiciones del momento.
Grupo funcional
Contexto operativo
Tipo de dato
Ordinal
Valores posibles
Fácil / Moderada / Difícil / Muy difícil
Fuente principal
Comunicación inicial / cartografía oficial (ICEARAGON)
Método de obtención
Declaración del alertante, cruce con capas viarias y topográficas
Papel en el motor
Scoring (la dificultad de acceso incrementa la urgencia operativa de la decisión)
Justificación normativa u operativa
PLATEAR: accesibilidad como factor de planificación territorial. La dificultad de acceso condiciona tiempos de respuesta.
Observaciones
Una accesibilidad muy difícil no cambia la gravedad intrínseca del incidente, pero sí incrementa la urgencia de la decisión al ampliar el tiempo de intervención.


Fuente: elaboración propia. Esta matriz detallada despliega la información resumida en la Tabla 6.2 del Capítulo 6.

B.4. Matriz detallada de variables derivadas
Las cuatro variables derivadas no constituyen entradas del motor, sino resultados intermedios calculados a partir de la combinación de variables de entrada y de la lógica del baseline. Esta distinción es metodológicamente crítica: tratar una variable derivada como entrada introduciría circularidad en el diseño y comprometería la interpretabilidad del sistema.
D01. Necesidad de coordinación multiagencia
ID
D01
Nombre de la variable
Necesidad de coordinación multiagencia
Definición operativa
Indica si el incidente exige previsiblemente la intervención simultánea de varios servicios (bomberos, sanitarios, fuerzas de seguridad, protección civil).
Grupo funcional
Complejidad
Tipo de dato
Derivada (binaria)
Valores posibles
Sí / No
Fuente principal
Calculada por el motor a partir de V02, V04, V06, V08, V11
Método de obtención
Reglas combinatorias sobre variables de entrada
Papel en el motor
Salida intermedia (alimenta D02 y D03; contribuye a la explicación final)
Justificación normativa u operativa
PLATEAR: niveles de coordinación asociados a la complejidad del incidente. PLEGEM: estructura de coordinación multiagencia.
Observaciones
No es un input del modelo. Su valor se calcula a partir de las entradas y forma parte de la salida explicativa, no del scoring directo.


D02. Necesidad estimada de PMA
ID
D02
Nombre de la variable
Necesidad estimada de PMA
Definición operativa
Sugiere si el escenario apunta a la conveniencia de activar un Puesto de Mando Avanzado en la zona del incidente.
Grupo funcional
Complejidad
Tipo de dato
Derivada (binaria)
Valores posibles
Sí / No
Fuente principal
Calculada por el motor a partir de D01, V02, V06, V12
Método de obtención
Reglas combinatorias sobre variables de entrada y D01
Papel en el motor
Salida intermedia (orientación no vinculante para el operador)
Justificación normativa u operativa
PLATEAR: criterios de activación de PMA. Ley 4/2024: estructura de mando en emergencias.
Observaciones
Sugerencia operativa complementaria. Su activación no altera la prioridad P1–P4, sino que añade información al operador sobre la complejidad logística previsible.


D03. Situación operativa sugerida
ID
D03
Nombre de la variable
Situación operativa sugerida
Definición operativa
Orientación no vinculante sobre la situación operativa (0–3) que podría corresponder al incidente, derivada de la gravedad, extensión, coordinación y suficiencia de medios.
Grupo funcional
Global
Tipo de dato
Derivada (ordinal)
Valores posibles
0 / 1 / 2 / 3
Fuente principal
Calculada por el motor a partir de la prioridad resultante, D01, V02, V06
Método de obtención
Lógica de correspondencia orientativa entre P1–P4 y situaciones operativas
Papel en el motor
Salida orientativa (presentada siempre con advertencia de que la declaración formal corresponde a la autoridad competente)
Justificación normativa u operativa
Norma Básica de Protección Civil (RD 524/2023): define situaciones operativas 0–3. PLEGEM: criterios de escalado.
Observaciones
No equivale jurídicamente a la situación operativa formal. Un incidente P1 puede coexistir con una situación operativa global 0 o 1. La salida es siempre orientativa.


D04. Plan activable recomendado
ID
D04
Nombre de la variable
Plan activable recomendado
Definición operativa
Sugerencia del plan territorial o especial que podría ser aplicable al incidente, en función del tipo de incidente y del contexto territorial.
Grupo funcional
Global
Tipo de dato
Derivada (categórica)
Valores posibles
PLATEAR / Plan especial (PROCINFO, PROCINAR, PROCIFEMAR, PROCIMER…) / Ninguno
Fuente principal
Calculada por el motor a partir de V04, V08, V10, V11 y la taxonomía operativa
Método de obtención
Tabla de correspondencia tipo de incidente → plan aplicable, condicionada por contexto
Papel en el motor
Salida orientativa (la activación formal de planes corresponde a la autoridad competente)
Justificación normativa u operativa
PLATEAR y planes especiales de Aragón: cada plan define su ámbito de aplicación y criterios de activación.
Observaciones
No constituye una activación automática del plan. Es una orientación para el operador que le permite anticipar qué marco de coordinación podría necesitar.


Fuente: elaboración propia. Estas variables derivadas corresponden a las definidas en el apartado 6.4 del Capítulo 6.

B.5. Reglas de tratamiento de ausencia de datos
En el contexto operativo de las emergencias, la información disponible durante los primeros minutos es frecuentemente incompleta. El motor debe ser capaz de producir una recomendación incluso cuando no todas las variables de entrada están disponibles. El requisito no funcional de robustez ante información incompleta (RNF5, Capítulo 5) exige que el sistema defina explícitamente cómo tratar la ausencia de cada variable.
El tratamiento de datos ausentes se rige por tres principios:
Principio de precaución razonable. Cuando una variable crítica no está disponible, el motor no asume el peor escenario, pero tampoco lo descarta. Aplica un valor por defecto conservador que no infla la prioridad de forma artificial ni la rebaja de forma irresponsable.
Principio de transparencia. Toda variable ausente queda registrada en la explicación del motor y reduce proporcionalmente el nivel de confianza de la recomendación.
Principio de no bloqueo. La ausencia de una variable nunca impide la emisión de una recomendación. El motor funciona con la información disponible y explicita qué le falta.
La tabla B.5.1 detalla el tratamiento específico para cada variable de entrada.
Tabla B.5.1. Reglas de tratamiento de ausencia de datos por variable
Variable
Criticidad para el motor
Valor por defecto
Justificación
Efecto sobre la confianza
V01
Crítica
No (se asume ausencia de riesgo vital si no se declara explícitamente)
Principio de prudencia operativa: el riesgo vital requiere confirmación activa
Confianza reducida si la comunicación es incompleta
V02
Alta
0 (sin víctimas)
Sin mención explícita, se asume ausencia
Confianza reducida
V03
Media
Sin daño
Valor conservador neutro
Confianza reducida
V04
Crítica
Incidente no clasificado
Se mantiene la evaluación sin contexto tipológico específico
Confianza significativamente reducida; no se activan reglas dependientes del tipo
V05
Media
No
Se asume ausencia salvo indicación expresa
Confianza reducida
V06
Media
0
Sin estimación, se asume sin exposición declarada
Confianza reducida
V07
Media
No
Sin localización precisa, no se puede verificar emplazamiento
Confianza reducida
V08
Alta (si incidente meteorológico)
Verde (sin aviso)
Sin acceso a AEMET, se asume condición favorable
Confianza reducida en incidentes meteorológicos o hidrológicos
V09
Media
Ninguno
Sin información meteorológica disponible
Confianza reducida si V08 tampoco está disponible
V10
Media
No
Sin cruce geoespacial disponible
Confianza reducida en incidentes hidrológicos
V11
Alta (si incidente industrial)
No
Sin cruce disponible, se asume ausencia
Confianza reducida en incidentes químicos o industriales
V12
Media
Desconocida
Se aplica precaución moderada conforme a la guía de etiquetado
Confianza reducida
V13
Baja
Baja
Sin identificación del informador, se asume fiabilidad mínima
Confianza reducida
V14
Baja
1 (aviso único)
Sin información de avisos adicionales
Sin efecto adicional
V15
Media
Moderada
Valor intermedio conservador
Confianza reducida

Fuente: elaboración propia. Coherente con el requisito RNF5 (Capítulo 5) y con la capa de confianza del baseline (apartado 6.7.3 del Capítulo 6).

