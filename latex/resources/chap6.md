Capítulo 6. Diseño del motor de priorización
Este capítulo presenta el núcleo analítico del TFM: el diseño del motor de priorización, que constituye la aportación principal del trabajo. Todo lo desarrollado en los capítulos anteriores converge aquí en una especificación funcional que define qué información entra en el motor, cómo se procesa y qué salida produce.
El capítulo se organiza de forma progresiva. En primer lugar, se presenta el motor como sistema de apoyo a la decisión y se delimita su función dentro del prototipo. A continuación, se desarrolla la escala de prioridad operativa P1–P4, se definen las variables de entrada y las variables derivadas, se introduce la guía de etiquetado y se describe la arquitectura del baseline interpretable de tres capas. Después, se formulan las reglas duras del sistema, se establecen pesos orientativos y umbrales iniciales del scoring, se justifica la elección metodológica del baseline frente a modelos más complejos y se muestra un ejemplo de funcionamiento paso a paso. Por último, se sintetiza la lógica del sistema mediante una fórmula conceptual de prioridad.
La finalidad de este capítulo no es describir una implementación cerrada y ya validada empíricamente, sino fijar con precisión el diseño analítico y funcional del motor. La calibración definitiva de pesos y umbrales, así como la evaluación cuantitativa del comportamiento del sistema, se desarrollan en el capítulo de evaluación.
6.1. Planteamiento general: el «cerebro» del sistema
El motor de priorización es el componente que transforma la información disponible sobre un incidente en una recomendación estructurada de urgencia operativa. Si el prototipo completo funciona como un sistema de apoyo a la decisión, el motor constituye su núcleo lógico: recibe datos del incidente, integra contexto oficial, aplica reglas y una lógica de ponderación explicable, y devuelve una salida que el operador puede utilizar como apoyo para la primera decisión.
La entrada del motor está delimitada a un conjunto cerrado de quince variables operativas. Esta restricción es deliberada y responde a una decisión metodológica del proyecto: priorizar un diseño robusto, trazable y viable frente a un modelo excesivamente amplio y difícil de justificar. Las entradas del motor son las siguientes: riesgo vital inmediato, víctimas confirmadas o probables, tipo de daño principal, tipo de incidente, población vulnerable, personas en riesgo estimadas, emplazamiento crítico, nivel de aviso AEMET, fenómeno meteorológico activo, peligrosidad por inundación, presencia de instalación Seveso, tendencia del incidente, fiabilidad del informador, número de avisos simultáneos y accesibilidad al punto.
La salida del motor está compuesta por cuatro elementos funcionales: prioridad operativa recomendada en escala P1–P4, nivel de confianza de la recomendación, situación operativa sugerida y explicación resumida de los factores determinantes. Estas salidas no constituyen una decisión automática ni un despacho de recursos, sino una recomendación revisable por el operador humano. El sistema no sustituye al decisor; reduce el tiempo necesario para alcanzar una primera valoración razonada y trazable.
La explicabilidad no se incorpora como una capa estética posterior, sino como un requisito de diseño desde el origen. En un dominio donde las recomendaciones afectan a la protección de personas y a la activación de respuestas coordinadas, una prioridad que no pueda entenderse, discutirse o corregirse carece de valor operativo. Por esa razón, el motor se construye sobre un baseline interpretable, basado en reglas duras, scoring explicable y cálculo explícito de confianza.
6.2. Escala de prioridad operativa del sistema (P1–P4)
El motor necesita una escala con capacidad discriminante suficiente para ordenar incidentes en condiciones de información incompleta. Se ha optado por una escala de cuatro niveles —P1, P2, P3 y P4— porque permite distinguir con claridad entre incidentes críticos, altos, medios y bajos sin introducir una granularidad artificial difícil de sostener en la práctica operativa.
La escala P1–P4 es una abstracción operativa propia del prototipo. Se inspira en la lógica gradual de las situaciones operativas de protección civil y en los criterios de activación de planes, pero no constituye una categoría jurídica oficial ni una reproducción literal del marco normativo. Su función es ordenar incidentes individuales por urgencia operativa relativa dentro de un entorno de coordinación, no declarar formalmente una situación operativa ni activar jurídicamente un plan.
6.2.1. P1 — Prioridad crítica
La prioridad P1 se asigna a incidentes que requieren atención inmediata porque existe riesgo vital confirmado o altamente probable, o porque concurren condiciones que hacen previsible una escalada extremadamente rápida con afectación grave a personas. Se trata de incidentes en los que una demora en la primera decisión puede traducirse en pérdida de vidas o en un deterioro severo del escenario.
De forma orientativa, pertenecen a este nivel los incidentes con personas atrapadas en riesgo vital, accidentes con múltiples víctimas graves, inundaciones con personas aisladas o arrastradas, fugas tóxicas con afectación en zona habitada o incendios con amenaza directa e inmediata a población expuesta.
6.2.2. P2 — Prioridad alta
La prioridad P2 se asigna a incidentes con gravedad significativa o con potencial de escalado relevante, pero en los que el riesgo vital no es inmediato o no está todavía confirmado. Requieren una respuesta rápida y coordinada, aunque admiten un margen breve para la verificación y la valoración adicional.
Pertenecen típicamente a este nivel los incendios forestales en interfaz urbano-forestal con condiciones meteorológicas desfavorables, los accidentes de tráfico con víctimas no críticas, los fenómenos meteorológicos adversos con aviso naranja o rojo asociados al incidente, o los incidentes en entornos Seveso sin afectación directa confirmada.
6.2.3. P3 — Prioridad media
La prioridad P3 corresponde a incidentes que exigen gestión activa, pero que no presentan urgencia vital ni un potencial de escalado elevado a corto plazo. Son escenarios controlables con medios ordinarios, en los que una demora razonable no produce, previsiblemente, un agravamiento sustancial.
Se incluyen aquí, por ejemplo, accidentes sin víctimas graves, incendios contenidos sin amenaza a personas, incidencias meteorológicas con afectación limitada o rescates sin compromiso vital inmediato.
6.2.4. P4 — Prioridad baja
La prioridad P4 se reserva para incidentes menores que requieren registro, seguimiento o gestión diferida, pero que no compiten en urgencia con incidentes de niveles superiores. Este nivel es necesario para evitar que el sistema sature artificialmente los niveles altos de la escala y pierda poder discriminante.
Se incluyen en este grupo consultas informativas, incidencias menores sin daño relevante, verificaciones rutinarias y avisos sin componente claro de urgencia operativa.
Tabla 6.1. Escala de prioridad operativa P1–P4 del sistema
Nivel
Denominación
Condiciones típicas
Referente normativo orientativo
Acción
P1
Prioridad crítica
Riesgo vital confirmado o muy probable; AMV; personas atrapadas; fuga tóxica en zona habitada; inundación con personas aisladas
Referencia funcional frecuente a escenarios compatibles con mayor complejidad de coordinación
Atención inmediata; movilización urgente
P2
Prioridad alta
Gravedad sin riesgo vital inmediato; potencial de escalado relevante; aviso AEMET naranja/rojo; proximidad Seveso sin afectación directa
Referencia funcional frecuente a escenarios de respuesta rápida reforzada
Respuesta rápida coordinada
P3
Prioridad media
Gestión activa sin urgencia vital; controlable con medios ordinarios; afectación moderada
Referencia funcional frecuente a gestión ordinaria reforzada
Gestión activa con demora razonable
P4
Prioridad baja
Incidente menor; consultas informativas; verificaciones rutinarias
Sin correlato operativo reforzado
Registro y seguimiento diferido

Fuente: elaboración propia. La columna «Referente normativo orientativo» expresa una correspondencia funcional frecuente, no una equivalencia jurídica.
6.2.5. Relación entre P1–P4 y situaciones operativas 0–3
La relación entre la escala P1–P4 y las situaciones operativas 0–3 exige una formulación cuidadosa. Las situaciones operativas son categorías normativas que describen el estado global de una emergencia desde la perspectiva de la coordinación institucional. Determinan quién dirige, qué planes se activan y qué marco de coordinación resulta aplicable. La prioridad P1–P4, en cambio, es una escala funcional interna del prototipo que ordena incidentes individuales por urgencia operativa relativa.
La inspiración entre ambas escalas es deliberada, pero la equivalencia no existe. Un incidente puede recibir prioridad P1 por riesgo vital inmediato sin que la situación operativa global del territorio exceda una situación 0 o 1. Del mismo modo, una situación operativa 2 o 3 puede englobar incidentes heterogéneos cuya prioridad individual no sea idéntica. En consecuencia, la salida «situación operativa sugerida» que produce el motor debe entenderse siempre como una orientación complementaria no vinculante para el operador, nunca como una declaración formal de la situación.
6.3. Variables de entrada del motor
La selección de variables de entrada constituye una de las decisiones de diseño más importantes del motor. Una selección demasiado amplia haría inviable el sistema dentro del alcance del TFM; una selección demasiado reducida lo convertiría en un clasificador trivial e incapaz de discriminar entre incidentes operativamente diferentes.
La selección se ha guiado por cuatro criterios: respaldo normativo u oficial, impacto esperado sobre la prioridad, viabilidad de obtención en los primeros minutos y no redundancia con otras variables. El resultado es un conjunto cerrado de quince variables de entrada organizadas en seis grupos funcionales.
6.3.1. Gravedad inmediata
Este grupo captura el daño actual o inminente a personas y ocupa la posición central en la lógica del sistema.
Riesgo vital inmediato. Variable binaria que indica si existe peligro de muerte inminente.
Víctimas confirmadas o probables. Variable ordinal codificada por rangos, adecuada para información temprana incompleta.
Tipo de daño principal. Variable categórica que diferencia entre daño a personas, bienes, medioambiente o ausencia de daño aparente.
6.3.2. Vulnerabilidad y exposición
Este grupo incorpora el contexto humano y territorial del incidente.
Población vulnerable. Variable binaria que recoge la presencia confirmada o probable de menores, personas mayores, personas con discapacidad u otros colectivos especialmente sensibles.
Personas en riesgo estimadas. Variable ordinal que estima cuántas personas podrían verse afectadas por la evolución del incidente, aunque todavía no exista daño confirmado.
Emplazamiento crítico. Variable categórica que identifica si el incidente afecta a centros sanitarios, centros educativos, residencias, infraestructuras esenciales u otros emplazamientos sensibles.
6.3.3. Amenaza contextual
Estas variables convierten el motor en un sistema contextual y no meramente reactivo.
Nivel de aviso AEMET. Variable ordinal con valores verde, amarillo, naranja o rojo.
Fenómeno meteorológico activo. Variable categórica que identifica el fenómeno relevante para el incidente.
Peligrosidad por inundación. Variable binaria derivada del cruce espacial con cartografía oficial.
Presencia de instalación Seveso. Variable binaria que indica si el incidente se ubica en el entorno de una instalación industrial de especial riesgo.
6.3.4. Escalado y evolución del incidente
Tipo de incidente. Variable categórica que activa la taxonomía y condiciona qué contexto se consulta y qué reglas se aplican.
Tendencia del incidente. Variable ordinal con cuatro estados: mejoría, estable, agravamiento o desconocida.
6.3.5. Calidad de la información
Estas variables no miden gravedad, sino solidez informativa.
Fiabilidad del informador. Variable ordinal que diferencia entre fuente oficial, testigo directo o fuente indirecta.
Número de avisos simultáneos. Variable numérica agrupada en rangos, útil para reforzar la confirmación del evento y modular la confianza.
6.3.6. Contexto operativo
Accesibilidad al punto. Variable ordinal que refleja dificultad de acceso al lugar del incidente y, por tanto, condiciona la urgencia práctica de la decisión y de la movilización.
6.4. Variables derivadas y salidas intermedias
Además de las quince variables de entrada, el motor calcula cuatro variables derivadas. Estas no deben tratarse como entradas puras del modelo, sino como resultados intermedios obtenidos a partir de la combinación de entradas y de la lógica del motor.
Necesidad de coordinación multiagencia. Indica si el incidente exige previsiblemente la intervención simultánea de varios servicios.
Necesidad estimada de PMA. Sugiere si el escenario apunta a la conveniencia de un puesto de mando avanzado.
Situación operativa sugerida. Orientación no vinculante derivada de gravedad, extensión, coordinación y suficiencia de medios.
Plan activable recomendado. Sugerencia del plan territorial o especial potencialmente aplicable, en función del tipo de incidente y del contexto.
6.5. Matriz resumida de variables de priorización
La matriz de variables es el instrumento que consolida, para cada variable, su definición operativa, tipo de dato, valores posibles, fuente principal y papel dentro del motor. La versión completa de esta matriz se incorpora en el Anexo B. En el cuerpo del capítulo se incluye una versión resumida que permite visualizar de forma compacta el diseño.

Tabla 6.2. Variables de entrada y derivadas del motor: resumen operativo
ID
Variable
Tipo de dato
Valores posibles
Fuente principal
Papel en el motor
Grupo funcional
V01
Riesgo vital inmediato
Binaria
Sí / No
Comunicación inicial
Regla dura
Gravedad inmediata
V02
Víctimas confirmadas o probables
Ordinal
0 / 1–2 / 3–10 / >10
Comunicación inicial
Regla + scoring
Gravedad inmediata
V03
Tipo de daño principal
Categórica
Personas / Bienes / Medioambiente / Sin daño
Comunicación inicial
Scoring
Gravedad inmediata
V04
Tipo de incidente
Categórica
Taxonomía operativa del sistema
Comunicación / estructuración
Activación + scoring
Escalado
V05
Población vulnerable
Binaria
Sí / No
Comunicación / contexto oficial
Scoring
Vulnerabilidad
V06
Personas en riesgo estimadas
Ordinal
0 / 1–10 / 11–100 / >100
Comunicación / contexto oficial
Scoring
Exposición
V07
Emplazamiento crítico
Categórica
Sanitario / Educativo / Residencia / Infraestructura / Otro / No
Comunicación / cartografía oficial
Scoring
Vulnerabilidad
V08
Nivel de aviso AEMET
Ordinal
Verde / Amarillo / Naranja / Rojo
AEMET OpenData
Regla + scoring
Amenaza contextual
V09
Fenómeno meteorológico activo
Categórica
Viento / Lluvia / Nieve / Temperatura / Tormenta / Ninguno
AEMET OpenData
Scoring condicionado
Amenaza contextual
V10
Peligrosidad por inundación
Binaria
Sí / No
SNCZI / MITECO
Scoring
Amenaza contextual
V11
Presencia de instalación Seveso
Binaria
Sí / No
Registro oficial Seveso
Regla + scoring
Amenaza contextual
V12
Tendencia del incidente
Ordinal
Mejoría / Estable / Agravamiento / Desconocida
Comunicación / parte de servicio
Scoring
Escalado
V13
Fiabilidad del informador
Ordinal
Alta / Media / Baja
Comunicación inicial
Confianza
Calidad de la información
V14
Número de avisos simultáneos
Numérica agrupada
1 / 2–3 / >3
Registro de avisos
Confianza
Calidad de la información
V15
Accesibilidad al punto
Ordinal
Fácil / Moderada / Difícil / Muy difícil
Comunicación / cartografía oficial
Scoring
Contexto operativo




D01
Necesidad de coordinación multiagencia
Derivada
Sí / No
Calculada por el motor
Salida intermedia
Complejidad
D02
Necesidad estimada de PMA
Derivada
Sí / No
Calculada por el motor
Salida intermedia
Complejidad
D03
Situación operativa sugerida
Derivada
0 / 1 / 2 / 3
Calculada por el motor
Salida orientativa
Global
D04
Plan activable recomendado
Derivada
PLATEAR / plan especial / ninguno
Calculada por el motor
Salida orientativa
Global

Fuente: elaboración propia. La matriz detallada completa se incluye en el Anexo B.
La versión completa de la matriz de variables de priorización se incorpora en el Anexo B. Su inclusión en anexo responde a una decisión de claridad expositiva: permite mantener en el cuerpo del capítulo la lógica analítica general del motor, sin renunciar al detalle técnico necesario para la implementación y la trazabilidad metodológica.
6.6. Guía de etiquetado
La guía de etiquetado define cómo asignar una prioridad de referencia a los casos del dataset piloto y cumple dos funciones complementarias: reducir la subjetividad del etiquetado y proporcionar el estándar contra el que se evaluará la coherencia del baseline.
La guía completa de etiquetado se incorpora en anexo, dado que su desarrollo detallado —criterios por caso, reglas de resolución de ambigüedad, tratamiento de información incompleta y ejemplos de etiquetado— excede lo necesario para la lectura continua del capítulo, pero resulta imprescindible para justificar la construcción del dataset piloto y la coherencia del baseline.
6.6.1. Reglas maestras
La prioridad debe entenderse como urgencia operativa relativa, no como importancia abstracta. Debe reflejar la necesidad de atención temprana en un entorno de coordinación, no la gravedad final observada horas después. Cuando la información sea incompleta, el etiquetado debe asumir un criterio de precaución razonable, pero sin convertir la incertidumbre en dramatización sistemática. Además, toda asignación debe poder justificarse mediante variables, reglas o criterios operativos trazables.
6.6.2. Reglas duras del baseline
Las reglas duras son condiciones deterministas que fijan o limitan la prioridad sin necesidad de aplicar todavía la capa de scoring. Su función es actuar como red de seguridad del sistema para garantizar que ciertos escenarios no negociables no queden infraestimados.
Tabla 6.3. Reglas duras del baseline interpretable
ID
Condición
Prioridad asignada
Base normativa orientativa
Justificación operativa
RD1
Riesgo vital inmediato confirmado (V01 = Sí)
P1 fija
Principio de protección de la vida
La vida humana prevalece sobre cualquier otro criterio
RD2
Víctimas confirmadas ≥ 3
P2 mínima
Lógica de activación por múltiples víctimas
Requiere coordinación reforzada
RD3
Aviso AEMET rojo activo y coherencia con el tipo de incidente
P2 mínima
Planificación meteorológica especial
Riesgo extremo con potencial de agravamiento
RD4
Incidente en entorno Seveso con afectación directa confirmada
P1 mínima
Riesgo químico e industrial
Potencial catastrófico elevado
RD5
Víctimas confirmadas > 10
P1 mínima
Escenario compatible con AMV de alta entidad
Magnitud incompatible con prioridad media o baja
RD6
Búsqueda de persona menor o vulnerable
P2 mínima
Protección reforzada de colectivos vulnerables
Sensibilidad especial del caso
RD7
Inundación con personas aisladas o atrapadas
P1 fija
Riesgo hidrológico con afectación directa a personas
Máxima urgencia
RD8
Incendio forestal en interfaz urbano-forestal con AEMET naranja o rojo
P2 mínima
Riesgo de propagación a población
Escalada rápida plausible

Fuente: elaboración propia. Estas reglas expresan condiciones funcionales del prototipo y no decisiones jurídicas automáticas de activación.
6.6.3. Criterios de resolución de conflictos
Cuando diferentes variables apunten hacia prioridades distintas, prevalece la señal de mayor urgencia compatible con la información disponible. Este criterio evita que factores secundarios rebajen artificialmente la prioridad de escenarios con indicadores críticos. La resolución del conflicto debe quedar reflejada en la explicación final del motor.
6.6.4. Etiquetado de confianza
Además de la prioridad, cada caso se acompaña de un nivel de confianza del etiquetado: alto, medio o bajo. Este nivel no mide la gravedad del incidente, sino la completitud y robustez de la información disponible para etiquetarlo. Su incorporación permite diferenciar entre errores del motor y limitaciones estructurales del dato.
6.7. Arquitectura del baseline interpretable
El motor se implementa como un baseline interpretable de tres capas. Esta arquitectura responde a una decisión metodológica deliberada: priorizar explicabilidad, trazabilidad y robustez frente a complejidad innecesaria.
6.7.1. Capa 1: reglas duras
La primera capa evalúa secuencialmente las reglas duras. Si una de ellas se activa, fija una prioridad mínima o absoluta según el caso. Si ninguna se activa, el incidente pasa a la segunda capa.
Esta capa garantiza que los incidentes más sensibles no dependan exclusivamente de una ponderación gradual. Así, el sistema no puede «promediar» un riesgo vital confirmado con factores secundarios hasta degradar indebidamente la urgencia.
6.7.2. Capa 2: scoring explicable
La segunda capa calcula una puntuación de prioridad mediante una combinación ponderada de variables normalizadas. El scoring no sustituye a las reglas duras, sino que actúa sobre los casos en los que no existe una condición determinista suficiente o en los que conviene modular la urgencia con mayor gradación.
Los pesos iniciales se asignan por grupos funcionales, no como verdad empírica cerrada, sino como punto de partida fundamentado en la jerarquía normativa y operativa del dominio.
Tabla 6.4. Pesos orientativos del scoring por grupo funcional
Grupo funcional
Variables incluidas
Peso orientativo
Justificación
Gravedad inmediata
V01, V02, V03
0,30–0,40
Protección prioritaria de las personas
Vulnerabilidad y exposición
V05, V06, V07
0,15–0,20
Magnitud potencial y sensibilidad de la población expuesta
Amenaza contextual
V08, V09, V10, V11
0,15–0,20
Planes especiales y contexto territorial oficial
Escalado y evolución
V04, V12
0,10–0,15
Evolución previsible y tipo de incidente
Contexto operativo
V15
0,05–0,10
Condiciona la respuesta, no la gravedad intrínseca
Calidad de la información
V13, V14
No pondera scoring
Modula la confianza, no la urgencia directa

Fuente: elaboración propia. Los pesos indicados corresponden al punto medio de cada rango orientativo (Gravedad: 0,35; Vulnerabilidad: 0,18; Amenaza: 0,18; Escalado: 0,13; Contexto operativo: 0,08). Antes de aplicar la fórmula de scoring, estos valores se normalizan dividiéndolos entre su suma (0,92), de modo que los pesos efectivos sumen exactamente 1,0 (Gravedad: 0,380; Vulnerabilidad: 0,196; Amenaza: 0,196; Escalado: 0,141; Contexto operativo: 0,087). Los valores definitivos se calibran en el capítulo de evaluación.
La puntuación resultante se normaliza en el rango 0–100 y se traduce de forma inicial a la escala P1–P4 mediante umbrales orientativos.
Tabla 6.5. Umbrales indicativos de corte del scoring
Prioridad
Rango de puntuación
Interpretación
P1
≥ 75
Urgencia crítica
P2
50–74
Urgencia alta
P3
25–49
Urgencia media
P4
< 25
Urgencia baja

Fuente: elaboración propia. Estos umbrales son iniciales y su calibración definitiva se realiza en la fase de evaluación.
6.7.3. Capa 3: confianza y explicación
La tercera capa genera dos salidas adicionales: el nivel de confianza y la explicación textual de la recomendación. El nivel de confianza se calcula a partir de la cantidad y calidad de variables efectivamente informadas. La explicación resume qué regla dura se ha activado, qué variables han tenido mayor impacto en el scoring, qué señales contextuales han modulado la puntuación y qué información relevante permanece ausente.
La finalidad de esta capa es operativa. Un operador necesita saber no solo qué recomienda el sistema, sino también con qué solidez lo recomienda y sobre qué base.
6.8. Justificación del baseline frente a modelos más complejos
La elección de un baseline interpretable frente a modelos de aprendizaje automático más complejos no responde a una carencia, sino a una decisión metodológica coherente con el alcance del TFM.
En primer lugar, por viabilidad. No existe garantía de acceso a un dataset amplio, limpio y representativo de microdatos reales de 112 Aragón. En segundo lugar, por explicabilidad. Un sistema basado en reglas y scoring permite justificar internamente cada recomendación sin depender de técnicas post hoc. En tercer lugar, por trazabilidad normativa. Cada variable, regla y criterio puede vincularse a una lógica operativa documentada. En cuarto lugar, porque el baseline funciona como línea base metodológica: si en el futuro se plantea un modelo más complejo, deberá demostrar que mejora el comportamiento del baseline sin perder interpretabilidad de forma injustificada. Y, en quinto lugar, por coherencia con el objetivo del TFM: diseñar una lógica de priorización explicable y evaluable en escenarios simulados, no desplegar una solución industrial completa.
La versión ampliada de las reglas duras del baseline, así como los pesos finales y los umbrales calibrados del scoring, se documentan en el Anexo E. Esta decisión permite preservar la legibilidad del capítulo y, al mismo tiempo, ofrecer al tribunal una especificación técnica completa del motor, útil tanto para la trazabilidad metodológica como para la futura implementación del sistema.
6.9. Ejemplo de funcionamiento del motor
Para ilustrar la interacción entre las tres capas del baseline, se presenta un ejemplo simplificado de funcionamiento.
Supóngase un incendio forestal en interfaz urbano-forestal en la comarca de Cinco Villas, detectado en julio, con aviso AEMET naranja por viento y temperatura extrema, dos avisos ciudadanos independientes y sin víctimas confirmadas en el momento inicial.
En la primera capa, el sistema comprueba las reglas duras. No se activa la regla de riesgo vital inmediato ni la de víctimas múltiples, pero sí se activa la regla relativa a incendio forestal en interfaz urbano-forestal con aviso AEMET igual o superior a naranja (RD8). El sistema fija por tanto una prioridad mínima P2.
En la segunda capa, el scoring incorpora la amenaza contextual elevada, la exposición potencial, la presencia probable de población vulnerable y la accesibilidad moderada del punto. La puntuación resultante se mantiene dentro del rango P2.
En la tercera capa, el sistema calcula una confianza alta porque dispone de la mayoría de variables necesarias y genera una explicación resumida: incendio forestal en interfaz urbano-forestal, aviso AEMET naranja activo, riesgo de propagación hacia zona habitada, sin víctimas confirmadas en este momento, pero con necesidad de vigilancia reforzada y verificación de evolución.
Este ejemplo muestra la lógica general del motor: primero protege frente a la infraestimación de escenarios críticos, después gradúa la urgencia con una capa ponderada y finalmente explicita el razonamiento y la solidez de la recomendación.
6.10. Fórmula conceptual del motor de priorización
La lógica del motor puede sintetizarse en la siguiente expresión conceptual:
PRIORIDAD = 
f(gravedad actual, vulnerabilidad, exposición, amenaza contextual, potencial de escalado, complejidad de coordinación, calidad de la información)
En esta formulación, la calidad de la información no debe interpretarse como un factor que rebaje automáticamente la urgencia operativa del scoring. Su papel principal dentro del baseline es modular la confianza de la recomendación y hacer explícita la solidez del juicio automatizado ante información incompleta o contradictoria.
Esta fórmula no debe interpretarse como una ecuación cerrada con coeficientes definitivos, sino como una representación sintética de la estructura lógica del sistema. Cada uno de sus bloques se corresponde con grupos de variables del motor y expresa qué dimensiones intervienen en la recomendación de prioridad.
Con ello queda cerrado el diseño analítico del motor. El capítulo siguiente desarrolla el esquema de datos y la construcción del dataset piloto que permitirá alimentar esta lógica y evaluarla de manera consistente.

