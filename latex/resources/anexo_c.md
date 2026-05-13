Anexo C. Guía de etiquetado completa
C.1. Finalidad del anexo
Este anexo desarrolla la guía de etiquetado del sistema de priorización, cuya versión resumida se presenta en el apartado 6.6 del Capítulo 6. La guía define cómo asignar una prioridad de referencia a cada caso del dataset piloto y cumple cuatro funciones complementarias dentro del TFM.
Reducir la subjetividad. Al establecer criterios explícitos, reglas deterministas y procedimientos de resolución de conflictos, la guía limita el margen interpretativo del etiquetador y favorece la consistencia entre etiquetadores distintos.
Asegurar la consistencia interna. Casos con características similares deben recibir prioridades similares. La guía proporciona los criterios que permiten verificar esta consistencia.
Justificar la construcción del dataset. Cada caso del dataset piloto debe poder defenderse ante tribunal mediante las reglas y criterios de esta guía. Un etiquetado no justificable debilitaría la evaluación del baseline.
Proporcionar el estándar de evaluación. La prioridad de referencia asignada conforme a esta guía constituye el ground truth contra el que se evaluará la coherencia del motor de priorización en el Capítulo 9.
El contenido de este anexo es coherente con los apartados 6.6.1 a 6.6.4 del Capítulo 6, con la arquitectura del baseline (apartado 6.7), con el diseño de datos (Capítulo 7) y con los Anexos B (matriz de variables) y E (reglas y pesos del baseline). No introduce criterios nuevos ni modifica la lógica del motor.
C.2. Principios generales de etiquetado
El etiquetado de cada caso del dataset piloto se rige por los siguientes principios, que deben guiar la actuación del etiquetador en todo momento:
C.2.1. La prioridad es urgencia operativa relativa
La prioridad asignada a un incidente mide la necesidad de atención temprana en un entorno de coordinación de emergencias. No mide la importancia abstracta del suceso, ni la gravedad final que resultará horas después, ni el coste económico del daño. Un incidente puede tener consecuencias graves a largo plazo y, sin embargo, no requerir una prioridad crítica en los primeros minutos si no hay riesgo vital inminente ni potencial de escalado rápido.
C.2.2. El etiquetado se realiza en el momento de la primera decisión
El etiquetador debe situarse en el momento en que llega la información inicial del incidente al centro de coordinación. La prioridad debe reflejar la urgencia con la información disponible en ese instante, no con el conocimiento posterior de cómo evolucionó realmente el suceso. Esta regla es esencial para que el dataset evalúe al motor en las condiciones reales de uso: información incompleta, parcial y a veces contradictoria.
C.2.3. Precaución razonable, no dramatización
Cuando la información sea incompleta o ambigua, el etiquetador debe asumir un criterio de precaución razonable: considerar como plausible un escenario moderadamente desfavorable, sin llegar a asumir sistemáticamente el peor caso posible. Un incendio en un edificio sin confirmación de personas atrapadas no debe etiquetarse como P1 por defecto, pero tampoco debe descartarse que haya personas en riesgo. El criterio de precaución razonable orienta hacia P2 con confianza media, no hacia P1 con confianza baja.
C.2.4. Toda asignación debe ser justificable
El etiquetador debe poder explicar por qué ha asignado una prioridad determinada, vinculando su decisión a variables concretas, reglas duras o criterios operativos trazables. Una etiqueta que no puede justificarse mediante los criterios de esta guía es, por definición, incorrecta en el contexto del TFM.
C.2.5. Independencia entre casos
Cada caso se etiqueta de forma independiente. El etiquetador no debe dejarse influir por la prioridad asignada a casos anteriores ni buscar una distribución predeterminada. La distribución objetivo del dataset (Tabla 7.2 del Capítulo 7) se logra mediante el diseño de los casos, no mediante el ajuste del etiquetado.

C.3. Reglas maestras
Las reglas maestras son los criterios de nivel superior que gobiernan todo el proceso de etiquetado. Son anteriores a las reglas duras y al scoring: definen el marco interpretativo dentro del cual operan las demás reglas.
C.3.1. Definición operativa de cada nivel de prioridad
El etiquetador debe asignar la prioridad conforme a las siguientes definiciones, coherentes con la Tabla 6.1 del Capítulo 6:
Tabla C.1. Definición operativa de los niveles de prioridad para el etiquetado
Nivel
Denominación
Significado para el etiquetador
Criterio orientativo
P1
Prioridad crítica
El incidente requiere atención inmediata porque existe riesgo vital confirmado o altamente probable, o porque concurren condiciones que hacen previsible una escalada extremadamente rápida con afectación grave a personas.
Riesgo vital, personas atrapadas, AMV, inundación con aislados, fuga tóxica en zona habitada.
P2
Prioridad alta
El incidente presenta gravedad significativa o potencial de escalado relevante, pero el riesgo vital no es inmediato o no está todavía confirmado. Requiere respuesta rápida coordinada.
Incendio IUF con AEMET naranja/rojo, víctimas no críticas, proximidad Seveso, búsqueda de menor.
P3
Prioridad media
El incidente exige gestión activa pero no presenta urgencia vital ni potencial de escalado elevado a corto plazo. Controlable con medios ordinarios.
Accidente sin víctimas graves, incendio contenido, incidencia meteorológica con afectación limitada.
P4
Prioridad baja
Incidente menor que requiere registro, seguimiento o gestión diferida, sin urgencia operativa.
Consultas informativas, verificaciones rutinarias, incidencias menores sin daño.

Fuente: elaboración propia. Coherente con la Tabla 6.1 y los apartados 6.2.1–6.2.4 del Capítulo 6.
C.3.2. Regla del momento de la decisión
El etiquetador debe preguntarse: «con la información que tengo en este instante, ¿qué nivel de urgencia operativa requeriría este incidente para la primera decisión?». No debe incorporar información que solo estaría disponible horas después.
C.3.3. Regla de no retroactividad
Si un incidente etiquetado inicialmente como P3 resultó ser finalmente muy grave, la etiqueta correcta sigue siendo P3 si la información disponible en el momento de la primera comunicación no sugería mayor urgencia. El sistema se evalúa por su capacidad de recomendar bien con información temprana, no por su capacidad de predecir el futuro.
C.3.4. Regla de la explicación mínima
Cada etiqueta debe poder justificarse en una o dos frases que identifiquen las variables, reglas o criterios operativos que la sustentan. Si el etiquetador no puede formular esa justificación, debe revisar la asignación.

C.4. Reglas duras aplicables al etiquetado
Las reglas duras del baseline (Tabla 6.3 del Capítulo 6, ampliadas en el Anexo E) se aplican directamente al etiquetado. Si un caso cumple la condición de una regla dura, la prioridad asignada no puede ser inferior a la establecida por esa regla, salvo justificación explícita y documentada.
El etiquetador debe verificar las reglas duras antes de aplicar criterios de scoring. El procedimiento es el siguiente: primero, comprobar si alguna regla dura se activa; si se activa una regla con prioridad fija (RD1, RD7), la prioridad está determinada; si se activa una regla con prioridad mínima (RD2–RD6, RD8), la prioridad asignada puede ser igual o superior al mínimo, pero nunca inferior; si no se activa ninguna regla dura, la prioridad se determina por valoración de las variables conforme a los criterios de esta guía.
Tabla C.2. Reglas duras aplicables al etiquetado
ID
Condición
Prioridad
Instrucción para el etiquetador
RD1
Riesgo vital inmediato confirmado (V01 = Sí)
P1 fija
Si la comunicación indica peligro de muerte inminente, la prioridad es P1 sin excepción. No importa si faltan otras variables.
RD2
Víctimas confirmadas ≥ 3
P2 mín.
Con tres o más víctimas, la prioridad mínima es P2. Puede elevarse a P1 si concurren otros factores.
RD3
AEMET rojo + coherencia con el tipo de incidente
P2 mín.
Verificar que el fenómeno meteorológico es pertinente para el incidente. Si lo es y el aviso es rojo, P2 mínima.
RD4
Seveso + afectación directa confirmada
P1 mín.
No basta la proximidad. Debe haber evidencia de que el incidente involucra la instalación.
RD5
Víctimas confirmadas > 10
P1 mín.
Subsume a RD2. Más de 10 víctimas: P1 mínima.
RD6
Búsqueda de menor o persona vulnerable
P2 mín.
Combina tipo de incidente (búsqueda) con vulnerabilidad del sujeto. Ambas condiciones deben cumplirse.
RD7
Inundación con personas aisladas o atrapadas
P1 fija
Personas aisladas por agua = riesgo vital. P1 fija, incluso si el alertante no usa la expresión «riesgo vital».
RD8
Incendio IUF + AEMET ≥ naranja
P2 mín.
Interfaz urbano-forestal con condiciones meteorológicas adversas: P2 mínima por riesgo de propagación.

Fuente: elaboración propia. Coherente con la Tabla 6.3 del Capítulo 6 y el Anexo E.

C.5. Criterios de resolución de conflictos
En muchos incidentes, las variables de entrada apuntarán hacia prioridades diferentes. El etiquetador debe aplicar los siguientes criterios para resolver estos conflictos de forma sistemática y trazable.
C.5.1. Prevalencia de la señal de mayor urgencia
Cuando diferentes variables sugieren prioridades distintas, prevalece la señal de mayor urgencia compatible con la información disponible. Este criterio evita que factores secundarios rebajen artificialmente la prioridad de escenarios con indicadores críticos. Por ejemplo, si V01 = Sí (riesgo vital), la prioridad es P1 independientemente de que V15 indique accesibilidad fácil o V12 indique tendencia de mejoría.
C.5.2. Las reglas duras prevalecen sobre la valoración global
Si una regla dura fija una prioridad mínima, ningún conjunto de variables favorables puede rebajar la prioridad por debajo de ese mínimo. Un incendio forestal en IUF con AEMET naranja (RD8 → P2 mínima) no puede rebajarse a P3 aunque las demás variables sean favorables (sin víctimas, tendencia estable, accesibilidad fácil).
C.5.3. La gravedad inmediata pesa más que el contexto
En caso de conflicto entre variables de gravedad inmediata (V01, V02, V03) y variables de contexto operativo o amenaza contextual, la gravedad inmediata tiene prioridad. Un incidente con víctimas confirmadas no se rebaja porque el aviso meteorológico sea verde o la accesibilidad sea fácil.
C.5.4. La incertidumbre no rebaja la prioridad
Si la información disponible es insuficiente para descartar un escenario grave, la prioridad no debe rebajarse por falta de confirmación. La incertidumbre se refleja en el nivel de confianza (apartado C.6), no en la prioridad. Un incidente con posibles víctimas no confirmadas se etiqueta con la prioridad que correspondería al escenario razonablemente plausible, acompañada de confianza reducida.
C.5.5. El contexto solo eleva, no rebaja
Las variables de amenaza contextual (aviso AEMET, peligrosidad por inundación, proximidad Seveso) pueden elevar la prioridad de un incidente cuando son pertinentes, pero su ausencia no debe utilizarse como argumento para rebajar una prioridad ya justificada por gravedad inmediata o vulnerabilidad.
C.5.6. Documentación del conflicto
Cuando el etiquetador resuelva un conflicto entre señales contradictorias, debe anotar brevemente en la justificación del caso qué variables entraron en conflicto y cuál fue el criterio de resolución aplicado. Esta anotación es especialmente importante en los casos de frontera (apartado C.7).

C.6. Etiquetado del nivel de confianza
Además de la prioridad, cada caso del dataset piloto se acompaña de un nivel de confianza del etiquetado. Este nivel no mide la gravedad del incidente, sino la completitud y robustez de la información disponible para asignar la prioridad. Su incorporación permite distinguir entre errores del motor y limitaciones estructurales del dato.
C.6.1. Definición de los niveles de confianza
Tabla C.3. Niveles de confianza del etiquetado
Nivel
Condiciones
Significado
Alto
Las variables críticas (V01, V02, V04) están informadas. La comunicación es coherente. El etiquetador no tiene dudas significativas sobre la prioridad asignada.
La etiqueta es fiable. Un desacuerdo entre el motor y esta etiqueta indica un problema del motor, no del dato.
Medio
Alguna variable relevante está ausente o es ambigua. El etiquetador ha aplicado precaución razonable pero reconoce margen de error. La prioridad podría variar en un nivel si apareciera información adicional.
La etiqueta es razonable pero no definitiva. Un desacuerdo moderado entre el motor y esta etiqueta puede atribuirse tanto al motor como a la limitación del dato.
Bajo
Variables críticas ausentes. Información muy fragmentaria o contradictoria. El etiquetador ha asignado la prioridad más razonable dadas las circunstancias, pero reconoce incertidumbre alta.
La etiqueta tiene valor orientativo. No debe penalizarse al motor por discrepancias con etiquetas de confianza baja en la evaluación de precisión.

Fuente: elaboración propia. Coherente con el apartado 6.6.4 del Capítulo 6 y con la capa de confianza del Anexo E.
C.6.2. Criterios para asignar el nivel de confianza
El etiquetador debe considerar tres dimensiones al asignar la confianza:
Completitud de variables. ¿Cuántas de las quince variables de entrada están efectivamente informadas? Las variables críticas (V01, V02, V04) pesan más en esta valoración que las complementarias.
Coherencia de la información. ¿La información disponible es internamente consistente? Contradicciones entre variables (por ejemplo, un alertante que indica «sin víctimas» pero describe un escenario con atrapamiento) reducen la confianza.
Fiabilidad de la fuente. ¿La comunicación procede de una fuente oficial, un testigo directo o una fuente indirecta? Conforme a la definición de V13, la fiabilidad del informador modula la confianza del etiquetado.
C.6.3. Relación entre confianza y prioridad
La confianza y la prioridad son dimensiones independientes. Un incidente puede tener prioridad P1 y confianza baja (por ejemplo, un reporte de riesgo vital procedente de fuente anónima con información fragmentaria). En este caso, la prioridad refleja la urgencia que correspondería al escenario reportado, y la confianza refleja la incertidumbre sobre si el escenario es realmente como se ha reportado.
El etiquetador no debe rebajar la prioridad para compensar una confianza baja. Si la información, tomada en su valor aparente, justifica P1, la prioridad es P1 con confianza baja. La confianza informa al evaluador sobre la robustez de la etiqueta, pero no altera el nivel de urgencia asignado.

C.7. Casos frontera y criterios de desempate
Los casos de frontera son aquellos en los que las variables disponibles no permiten una asignación clara a un único nivel de prioridad. Estos casos son los más valiosos para evaluar la capacidad de discriminación del motor, pero también los más difíciles de etiquetar. A continuación se establecen los criterios de desempate para cada frontera.
C.7.1. Frontera P1/P2
La pregunta clave es: ¿existe riesgo vital inminente o es solo potencial? Si el riesgo vital es confirmado o altamente probable (personas atrapadas, parada cardiaca, personas arrastradas por agua), la prioridad es P1. Si el riesgo vital es posible pero no confirmado (edificio con humo denso y personas posiblemente dentro, accidente en vía rápida sin confirmación de víctimas), la prioridad se resuelve aplicando el principio de precaución razonable:
Si la probabilidad de riesgo vital es alta (indicios fuertes aunque no confirmados): P1 con confianza media.
Si la probabilidad es moderada (escenario plausible pero sin indicios directos): P2 con confianza media.
C.7.2. Frontera P2/P3
Esta es la frontera más frecuente en el etiquetado. La pregunta clave es: ¿el incidente requiere una respuesta rápida coordinada o es gestionable con medios ordinarios y demora razonable?
Factores que empujan hacia P2: potencial de escalado (tendencia de agravamiento, condiciones meteorológicas desfavorables), vulnerabilidad de la población expuesta (menores, mayores, centros sensibles), complejidad de coordinación previsible (múltiples servicios implicados), y señales contextuales relevantes (aviso AEMET naranja, zona inundable).
Factores que empujan hacia P3: incidente contenido o en fase de estabilización, ausencia de población vulnerable en el entorno inmediato, condiciones meteorológicas favorables, y accesibilidad razonable.
Criterio de desempate: si al menos dos factores significativos empujan hacia P2 y ninguna variable descarta el potencial de escalado, la prioridad se asigna como P2 con confianza media. En caso contrario, P3.
C.7.3. Frontera P3/P4
La pregunta clave es: ¿el incidente requiere gestión activa por parte del centro de coordinación o basta con registro y seguimiento diferido?
Si el incidente implica algún tipo de daño (aunque sea menor), requiere desplazamiento de servicios o afecta a vía pública, la prioridad es P3. Si es una consulta informativa, una verificación rutinaria, un aviso sin urgencia operativa o un incidente ya resuelto en el momento de la comunicación, la prioridad es P4.
C.7.4. Ejemplo de caso frontera P2/P3
Para ilustrar la aplicación de los criterios de desempate, se reproduce el caso ambiguo presentado en el apartado 7.3.2 del Capítulo 7:
Ficha de caso frontera P2/P3
Descripción
Incendio urbano en edificio residencial con humo visible en escalera. Una persona mayor que reside en una planta alta no ha sido localizada. No hay confirmación de atrapamiento.
V01 (Riesgo vital)
No confirmado
V02 (Víctimas)
0 confirmadas
V03 (Tipo daño)
Personas (potencial)
V04 (Tipo incidente)
Incendio urbano en edificio
V05 (Población vulnerable)
Sí (persona mayor)
V12 (Tendencia)
Desconocida
V13 (Fiabilidad)
Media (vecino testigo directo)
Reglas duras activadas
Ninguna (V01 = No, V02 = 0)
Análisis
No se activa ninguna regla dura. Sin embargo, la presencia de humo en escalera, persona mayor no localizada y tendencia desconocida configuran un escenario con potencial de escalado y vulnerabilidad. Dos factores significativos empujan a P2.
Prioridad asignada
P2
Confianza
Media (persona mayor no confirmada como atrapada; tendencia desconocida)
Justificación
Principio de precaución razonable aplicado: persona vulnerable en entorno de riesgo con evolución incierta. Criterio de desempate P2/P3 favorable a P2.


C.7.5. Ejemplo de caso claro P1
Ficha de caso claro P1
Descripción
Inundación fluvial en municipio aragonés. Varias personas reportan estar aisladas en tejados. Aviso AEMET naranja por lluvia. Localización en zona cartografiada como inundable.
V01 (Riesgo vital)
Sí (personas aisladas por agua)
V02 (Víctimas)
0 confirmadas, pero riesgo vital
V04 (Tipo incidente)
Inundación
V08 (AEMET)
Naranja
V10 (Peligrosidad inundación)
Sí
V12 (Tendencia)
Agravamiento
V13 (Fiabilidad)
Alta (múltiples alertantes)
V14 (Avisos simultáneos)
> 3
Reglas duras activadas
RD1 (riesgo vital) → P1 fija; RD7 (inundación con aislados) → P1 fija
Prioridad asignada
P1
Confianza
Alto (información completa y coherente, múltiples fuentes)
Justificación
Reglas duras RD1 y RD7 activadas. Prioridad P1 fija. Sin ambigüedad.


C.7.6. Ejemplo de caso claro P4
Ficha de caso claro P4
Descripción
Llamada al 112 consultando si un camino rural está cortado por obras. No hay incidente activo ni riesgo. Llamante solicita información.
V01 (Riesgo vital)
No
V02 (Víctimas)
0
V03 (Tipo daño)
Sin daño
V04 (Tipo incidente)
Consulta informativa
V12 (Tendencia)
No aplica
Reglas duras activadas
Ninguna
Prioridad asignada
P4
Confianza
Alto (información clara y completa)
Justificación
No hay incidente activo. Consulta informativa sin urgencia operativa. P4.


C.8. Observaciones metodológicas
C.8.1. Procedimiento de etiquetado del dataset piloto
El etiquetado del dataset piloto sigue un procedimiento estandarizado que busca maximizar la consistencia y la trazabilidad:
Paso 1. Lectura del caso. El etiquetador lee la descripción completa del caso y los valores de las quince variables de entrada.
Paso 2. Verificación de reglas duras. El etiquetador comprueba si alguna de las ocho reglas duras se activa. Si se activa una regla fija, la prioridad queda determinada. Si se activa una regla mínima, se registra el suelo de prioridad.
Paso 3. Valoración de variables. El etiquetador evalúa las variables restantes siguiendo la jerarquía: gravedad inmediata > vulnerabilidad y exposición > amenaza contextual > escalado > contexto operativo. Esta jerarquía es coherente con los pesos del scoring (Tabla 6.4, Anexo E).
Paso 4. Asignación de prioridad. El etiquetador asigna la prioridad conforme a la Tabla C.1, respetando el mínimo de reglas duras si procede.
Paso 5. Asignación de confianza. El etiquetador asigna el nivel de confianza conforme a la Tabla C.3.
Paso 6. Justificación. El etiquetador redacta una justificación breve (una o dos frases) que identifica las variables y reglas determinantes. Si hay conflicto resuelto, se documenta el criterio aplicado.
C.8.2. Revisión cruzada
Para mitigar la subjetividad inherente al etiquetado, el equipo aplica un proceso de revisión cruzada: cada caso es etiquetado por un miembro del equipo y revisado por al menos otro. Cuando se detecta una discrepancia, los etiquetadores aplican conjuntamente los criterios de esta guía para alcanzar un consenso documentado. Si el consenso no es posible, se registra la discrepancia y se asigna confianza baja al caso.
C.8.3. Tratamiento de la información incompleta en el etiquetado
No todos los casos del dataset piloto tendrán las quince variables informadas. Cuando una variable esté ausente, el etiquetador debe:
Aplicar el valor por defecto definido en la tabla de ausencia de datos del Anexo B. Esto garantiza coherencia entre el etiquetado humano y el comportamiento del motor ante información incompleta.
Reducir la confianza proporcionalmente a la criticidad de la variable ausente. Una variable crítica ausente (V01, V04) reduce la confianza de forma significativa; una variable complementaria ausente (V14, V15) la reduce moderadamente.
Documentar la ausencia en la justificación del caso, indicando qué variable falta y cómo ha afectado a la decisión de prioridad.
C.8.4. Coherencia con el baseline
La guía de etiquetado ha sido diseñada para ser coherente con la lógica del baseline interpretable, pero no para ser idéntica a ella. El etiquetador humano aplica juicio operativo, mientras que el motor aplica reglas deterministas y scoring ponderado. La evaluación mide precisamente la concordancia entre ambos enfoques: si es alta, el baseline captura adecuadamente los criterios operativos; si es baja, los pesos, umbrales o reglas deben revisarse.
Por esta razón, el etiquetador no debe intentar replicar el cálculo del motor. Debe aplicar su criterio operativo guiado por esta guía, y dejar que la fase de evaluación mida la distancia entre el criterio humano y el criterio del sistema.
C.8.5. Limitaciones de la guía
Esta guía reduce la subjetividad del etiquetado, pero no la elimina. Los casos de frontera admiten interpretaciones razonables distintas, y el margen de variabilidad entre etiquetadores es inherente a cualquier proceso de etiquetado en dominios complejos. El proceso de revisión cruzada mitiga este riesgo, pero no lo suprime.
Además, la guía ha sido diseñada para el contexto del TFM: un dataset piloto de 120–150 casos etiquetados por el equipo del proyecto, con revisión interna. No ha sido validada por un panel externo amplio de operadores expertos del 112. Esta limitación se reconoce explícitamente en el Capítulo 7 (apartado 7.3.3) y en las conclusiones del TFM, y constituye una línea de trabajo futuro.

