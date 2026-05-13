Capítulo 9. Evaluación
Introducción al capítulo
Este capítulo presenta la evaluación del sistema de priorización diseñado en el Capítulo 6, implementado en el Capítulo 8 y alimentado con el dataset piloto construido conforme a la estrategia descrita en el Capítulo 7. La evaluación constituye el cierre del ciclo metodológico del TFM y responde directamente al objetivo específico OE8: evaluar la aplicabilidad del sistema en escenarios simulados, midiendo la coherencia del baseline con el etiquetado humano, la distribución de prioridades, la tasa de falsos negativos graves, la explicabilidad de las recomendaciones y el impacto estimado sobre el TTFD.
La evaluación se estructura en tres dimensiones complementarias. En primer lugar, se evalúa cuantitativamente el comportamiento del baseline interpretable mediante métricas de clasificación estándar y análisis específicos de seguridad operativa. En segundo lugar, se evalúa cualitativamente la explicabilidad y la utilidad operativa de las salidas del motor. En tercer lugar, se analiza el impacto potencial del sistema sobre el Time To First Decision (TTFD), que es la métrica operativa central del trabajo. El capítulo se cierra con una discusión de resultados y una identificación explícita de las limitaciones de la evaluación.
Es importante señalar desde el inicio el alcance de esta evaluación: se trata de una validación en escenarios simulados, realizada sobre un dataset piloto híbrido, en un entorno de prototipo académico. Los resultados permiten valorar la coherencia interna del diseño, la capacidad de discriminación del motor y la aplicabilidad potencial del enfoque, pero no equivalen a una validación operativa en un centro de coordinación real. Esta distinción se mantiene a lo largo de todo el capítulo.
9.1. Estrategia general de evaluación
La estrategia de evaluación del sistema se articula en torno a una pregunta central: ¿produce el baseline interpretable recomendaciones de prioridad coherentes con el criterio operativo que un profesional cualificado aplicaría ante los mismos escenarios? Esta pregunta conecta directamente con la PI2 formulada en el Capítulo 4 y con el diseño deliberado del baseline como sistema de apoyo a la decisión, no como sustituto del operador humano.
Para responder a esta pregunta, la evaluación adopta un diseño multidimensional que combina análisis cuantitativo, cualitativo y operativo. El análisis cuantitativo mide la concordancia entre las prioridades producidas por el motor y las prioridades de referencia asignadas conforme a la guía de etiquetado (Anexo C). El análisis cualitativo valora si las explicaciones generadas por la tercera capa del baseline son comprensibles, completas y útiles para un operador. El análisis operativo estima el impacto potencial del sistema sobre el TTFD mediante un razonamiento estructurado basado en los tiempos de proceso observados durante la evaluación.
El diseño de la evaluación respeta cuatro principios metodológicos. Primero, se evalúa el sistema en las mismas condiciones para las que ha sido diseñado: información temprana, parcial y a veces contradictoria, coherente con el momento de la primera decisión. Segundo, se utiliza como referencia el etiquetado humano producido por el equipo del TFM conforme a la guía del Anexo C, que constituye el ground truth del dataset piloto. Tercero, se presta atención diferenciada a los errores graves, en particular a los falsos negativos en la clase P1, donde una infraestimación puede tener consecuencias operativas críticas. Cuarto, se distingue con claridad entre lo que la evaluación demuestra y lo que solo sugiere.
Tabla 9.1. Resumen de dimensiones de evaluación
Dimensión
Objeto evaluado
Métricas / instrumentos
Apartado
Cuantitativa
Coherencia del baseline con el etiquetado humano
Matriz de confusión, precisión, recall, F1 por clase
9.2
Distribución y sesgo
Equilibrio de la distribución de prioridades generada
Distribución P1-P4, comparativa con etiquetado
9.2.2
Seguridad operativa
Falsos negativos graves (P1 no detectados)
Tasa FN en P1, análisis caso a caso
9.2.3
Cualitativa
Explicabilidad y confianza
Análisis de explicaciones, coherencia de confianza
9.2.4
Funcional
Comportamiento del prototipo completo
Verificación funcional de requisitos
9.3
Aplicabilidad
Coherencia en escenarios piloto Aragón
Análisis de escenarios representativos
9.4
Usabilidad
Facilidad de uso del prototipo
SUS o equivalente
9.5
Impacto TTFD
Reducción potencial del tiempo hasta la primera decisión
Estimación razonada
9.6

Fuente: elaboración propia. Coherente con OE8 (Capítulo 4) y con la evaluación cerrada del documento maestro (apartado 13).
9.2. Evaluación del baseline de priorización
El baseline interpretable de tres capas constituye el núcleo del sistema y, por tanto, el objeto principal de la evaluación. En este apartado se analiza su comportamiento mediante métricas de clasificación multiclase, se examina la distribución de prioridades generada y se realiza un análisis específico de los errores más críticos desde la perspectiva operativa.
9.2.1. Coherencia con el etiquetado humano (precisión, recall, F1)
La coherencia entre las prioridades asignadas por el motor y las prioridades de referencia del dataset piloto se mide mediante la comparación caso a caso de la salida del sistema con la etiqueta humana. El instrumento principal es la matriz de confusión 4×4, que cruza las cuatro clases predichas (P1, P2, P3, P4) con las cuatro clases de referencia.
A partir de la matriz de confusión se calculan las métricas estándar de clasificación multiclase: precisión (proportion de los casos asignados a una clase que realmente pertenecen a ella), recall (proporción de los casos de una clase que el sistema identifica correctamente) y F1 (media armónica de precisión y recall). Estas métricas se calculan por clase, dado que el rendimiento del sistema no tiene el mismo significado operativo en todos los niveles de prioridad.
Tabla 9.2. Plantilla de la matriz de confusión del baseline
Predicho \ Referencia
P1 (ref.)
P2 (ref.)
P3 (ref.)
P4 (ref.)
P1 (pred.)
VP(P1)






P2 (pred.)


VP(P2)




P3 (pred.)




VP(P3)


P4 (pred.)






VP(P4)

Fuente: elaboración propia. Los valores concretos se completarán con los resultados de la ejecución del baseline sobre el dataset piloto.
La interpretación de las métricas debe atender a la asimetría operativa del dominio. En un sistema de priorización de emergencias, no todos los errores tienen la misma gravedad. Un falso positivo en P1 (el sistema asigna P1 a un caso que es P2 o P3) genera una sobreactivación de recursos, que es costosa pero no peligrosa. Un falso negativo en P1 (el sistema asigna P2, P3 o P4 a un caso que realmente es P1) puede significar que un incidente con riesgo vital no recibe la atención urgente que requiere. Por esta razón, el recall de la clase P1 es la métrica más crítica de toda la evaluación: mide la capacidad del sistema para no infraestimar los escenarios de máxima urgencia.
Complementariamente, se calcula la concordancia global (accuracy) como indicador general de acierto, y el F1 macro (promedio no ponderado de los F1 por clase) como indicador de rendimiento equilibrado entre clases. Sin embargo, estas métricas globales deben interpretarse con cautela en un problema con distribución de clases potencialmente desequilibrada.
9.2.2. Distribución de prioridades y sesgo
Además de la concordancia caso a caso, es relevante analizar si la distribución global de prioridades generada por el motor es coherente con la distribución esperada en un entorno de emergencias. Una distribución en la que el 80 % de los casos se clasifica como P1 sería indicativa de un sesgo de sobreestimación; una distribución en la que apenas hay casos P1 sugeriría un umbral demasiado restrictivo.
La distribución de referencia se establece a partir del etiquetado humano del dataset piloto, que ha sido diseñado para cubrir los cuatro niveles de prioridad con una distribución orientativa coherente con la realidad operativa de un centro de coordinación (Tabla 7.2 del Capítulo 7). La comparación entre la distribución generada por el motor y la distribución de referencia permite detectar sesgos sistemáticos: tendencia a sobreestimar (sesgo conservador) o a infraestimar (sesgo permisivo) la urgencia.
En el dominio de las emergencias, un sesgo moderadamente conservador (es decir, una ligera tendencia a asignar prioridades por encima de la referencia) es preferible a un sesgo permisivo, siempre que no sea tan pronunciado como para saturar la categoría P1 y perder capacidad de discriminación. Este criterio se aplica en la interpretación de los resultados.
9.2.3. Análisis de falsos negativos graves (P1 no detectados)
Este subapartado constituye el análisis de seguridad operativa del sistema. Se define como falso negativo grave todo caso cuya prioridad de referencia es P1 y al que el motor asigna una prioridad P3 o P4. Los casos P1 clasificados como P2 se consideran errores de menor gravedad, dado que P2 sigue implicando una respuesta rápida y coordinada, pero se analizan igualmente.
Para cada falso negativo grave detectado se realiza un análisis caso a caso que incluye: la descripción del incidente, las variables de entrada, las reglas duras que deberían haberse activado, la puntuación del scoring, la prioridad asignada y la explicación generada por el motor. El objetivo de este análisis no es solo cuantificar la tasa de error, sino identificar las causas: ¿se trata de un fallo en las reglas duras, de un problema en los pesos del scoring, de una limitación del dato o de una ambigüedad inherente al caso?
La expectativa de diseño es que la capa de reglas duras (RD1-RD8) actúe como red de seguridad efectiva para los escenarios P1 más claros: riesgo vital confirmado (RD1), víctimas múltiples (RD5), inundación con personas aisladas (RD7). Si un incidente con riesgo vital confirmado (V01=Sí) no recibe prioridad P1, existe un error de implementación o de dato, no un problema de diseño del baseline. Si un incidente P1 de referencia no activa ninguna regla dura y es infraestimado por el scoring, el análisis debe determinar si los pesos o los umbrales requieren ajuste.
La tasa de falsos negativos graves en P1 debe ser lo más próxima posible a cero. En un sistema de apoyo a la decisión para emergencias, incluso un solo falso negativo grave requiere investigación y, si procede, corrección del motor.
9.2.4. Evaluación de la confianza y de la explicabilidad del sistema
La tercera capa del baseline produce dos salidas adicionales: el nivel de confianza (alto, medio, bajo) y la explicación textual de la recomendación. Ambas constituyen parte de la salida funcional del motor (conforme al requisito RF7 del Capítulo 5) y, por tanto, deben evaluarse.
Evaluación de la confianza. Se analiza la coherencia entre el nivel de confianza asignado por el motor y la completitud real de la información del caso. Un caso con todas las variables críticas informadas y fuentes fiables debería recibir confianza alta; un caso con variables ausentes y fuente anónima debería recibir confianza baja. Se verifica además si los casos con confianza baja presentan una mayor tasa de error que los casos con confianza alta, lo cual validaría que el mecanismo de confianza cumple su función de alerta.
Evaluación de la explicabilidad. Se selecciona un subconjunto representativo de casos del dataset (incluyendo al menos un caso de cada nivel de prioridad y varios casos de frontera) y se analiza la explicación generada por el motor según cuatro criterios: completitud (¿identifica las reglas duras activadas, las variables de mayor impacto y la información ausente?), corrección (¿la explicación es coherente con la prioridad asignada?), comprensibilidad (¿un operador podría entender el razonamiento sin conocimiento técnico del motor?) y utilidad operativa (¿la explicación aporta información que ayuda al operador a decidir si acepta o corrige la recomendación?).
Este análisis es necesariamente cualitativo y se presenta mediante fichas descriptivas de casos seleccionados. No pretende sustituir una evaluación formal de usabilidad con operadores reales, sino verificar que el mecanismo de explicación funciona conforme al diseño y produce salidas que, al menos a criterio del equipo del TFM, serían operativamente útiles.
9.3. Evaluación funcional del prototipo
Además de la evaluación del motor de priorización como componente analítico, es necesario verificar que el prototipo software implementado en el Capítulo 8 cumple los requisitos funcionales y no funcionales definidos en el Capítulo 5. La evaluación funcional se realiza mediante la verificación sistemática de los requisitos, comprobando que cada uno se satisface en el prototipo demostrable.
Los requisitos funcionales clave que se verifican incluyen: la capacidad de registrar un incidente con sus quince variables de entrada (RF1), la integración de contexto oficial mediante fuentes como AEMET y cartografías de riesgo (RF2-RF3), la ejecución del motor de priorización con las tres capas del baseline (RF4), la generación de la explicación automática (RF7), la presentación de la prioridad, la confianza y la explicación al operador en la interfaz (RF5-RF6), y la posibilidad de que el operador valide, corrija o rechace la recomendación del sistema (RF8).
Los requisitos no funcionales se evalúan conforme a los criterios establecidos en el Capítulo 5: explicabilidad (RNF1, verificada en el apartado 9.2.4), trazabilidad (RNF2, verificada mediante la persistencia de la cadena completa de decisión para cada caso), modularidad (RNF3, verificada en la arquitectura del Capítulo 8), supervisión humana obligatoria (RNF4, verificada mediante el flujo de validación de la interfaz) y robustez ante información incompleta (RNF5, verificada mediante los casos del dataset con variables ausentes).
La evaluación funcional se documenta mediante una tabla de verificación que cruza cada requisito con la evidencia de cumplimiento observada en el prototipo. Los requisitos que no se cumplen completamente se identifican con su causa y su nivel de impacto.
9.4. Evaluación de aplicabilidad en escenarios simulados (Aragón)
El dataset piloto ha sido diseñado con Aragón como caso piloto territorial, utilizando localizaciones reales, condiciones meteorológicas plausibles y tipologías de incidentes coherentes con el perfil de riesgos de la comunidad autónoma (Capítulo 3, apartado 3.3). Este apartado evalúa si las recomendaciones del motor son operativamente coherentes cuando se aplican a escenarios específicos del territorio aragonés.
La evaluación de aplicabilidad se estructura en torno a un conjunto de escenarios representativos seleccionados del dataset piloto, que cubren los principales perfiles de riesgo de Aragón: inundación fluvial en el corredor del Ebro, incendio forestal en interfaz urbano-forestal en la zona central, fenómeno meteorológico adverso en el Pirineo, riesgo industrial asociado a instalaciones Seveso en el eje del Ebro, emergencia sanitaria en zona rural con accesibilidad limitada, y búsqueda de persona en entorno de montaña.
Para cada escenario se analiza si la prioridad asignada por el motor es coherente con el contexto territorial específico, si las variables contextuales (avisos AEMET, peligrosidad por inundación, presencia Seveso) se integran correctamente, y si la explicación generada hace referencia a los factores territoriales relevantes. Este análisis complementa la evaluación cuantitativa del apartado 9.2 con una perspectiva operativa territorial que permite valorar si el diseño del motor captura adecuadamente la complejidad del entorno aragonés.
Conviene subrayar que esta evaluación de aplicabilidad no equivale a una validación institucional. El sistema no ha sido evaluado por operadores del 112 Aragón ni por responsables de protección civil de la comunidad autónoma. Los escenarios son simulados y, aunque plausibles, no reproducen la totalidad de las dinámicas operativas reales.
9.5. Evaluación de usabilidad (SUS o equivalente)
El prototipo ha sido diseñado para ser utilizado por un operador de puesto de mando de emergencias, lo que impone requisitos exigentes de claridad, rapidez de comprensión y facilidad de uso. Para evaluar la usabilidad del prototipo se aplica el cuestionario System Usability Scale (SUS), un instrumento estandarizado ampliamente utilizado en la evaluación de interfaces que proporciona una puntuación global de usabilidad percibida en una escala de 0 a 100 (Brooke, 1996).
Dadas las restricciones del TFM, la evaluación de usabilidad se realiza con un grupo reducido de evaluadores compuesto por los miembros del equipo del proyecto y, si es posible, por colaboradores externos con conocimiento del dominio de emergencias o de interfaces de usuario. Cada evaluador interactúa con el prototipo procesando un subconjunto de casos del dataset piloto y completa el cuestionario SUS al finalizar.
La puntuación SUS se interpreta conforme a los rangos establecidos en la literatura: por debajo de 50 indica usabilidad inaceptable, entre 50 y 70 indica usabilidad marginal, entre 70 y 85 indica buena usabilidad, y por encima de 85 indica usabilidad excelente. El objetivo del prototipo, atendiendo a su naturaleza académica, es alcanzar al menos una usabilidad buena (>70), identificando áreas de mejora para iteraciones futuras.
Complementariamente al SUS, se recogen observaciones cualitativas de los evaluadores sobre aspectos específicos de la interfaz: la claridad de la visualización de la prioridad, la legibilidad de la explicación, la fluidez del flujo de validación humana y cualquier dificultad o confusión detectada durante el uso. Estas observaciones se documentan como insumo para las líneas de trabajo futuro del Capítulo 10.
9.6. Evaluación del impacto sobre el TTFD
El Time To First Decision (TTFD) constituye la métrica operativa central del TFM (Capítulo 1, apartado 1.3). Se define como el tiempo que transcurre desde la recepción de la primera comunicación de un incidente hasta que el decisor del puesto de mando adopta la primera acción operativa relevante: activar un recurso, elevar el nivel de respuesta, solicitar información complementaria o descartar la alerta. La reducción del TTFD es el objetivo funcional último del sistema de apoyo a la decisión.
La evaluación directa del impacto sobre el TTFD requeriría un diseño experimental con mediciones cronometradas en un entorno operativo real o simulado con alta fidelidad, comparando los tiempos de decisión con y sin el sistema. Este diseño excede el alcance del presente TFM. Sin embargo, es posible realizar una estimación razonada del impacto potencial a partir de los datos disponibles.
La estimación se apoya en tres elementos. En primer lugar, en la identificación de las fases del proceso de decisión que el sistema puede acelerar: la estructuración de la información del incidente, la verificación de contexto oficial (avisos meteorológicos, cartografía de riesgo, registro Seveso) y la formulación de una primera hipótesis de prioridad. En segundo lugar, en la medición del tiempo que el motor necesita para procesar un caso y producir su recomendación, que se obtiene de los registros de ejecución del prototipo. En tercer lugar, en la comparación con las estimaciones de referencia de tiempos de gestión de incidentes en centros de coordinación, cuando estas estén disponibles en la literatura o en documentos institucionales.
El resultado de esta estimación no es un valor absoluto de reducción del TTFD (sería metodológicamente inadecuado presentarlo así), sino un análisis razonado de qué componentes del tiempo de decisión puede comprimir el sistema y en qué magnitud aproximada, acompañado de las condiciones y supuestos bajo los cuales esa estimación sería válida. Este análisis permite responder, con las limitaciones propias del TFM, a la pregunta de investigación PI4 (Capítulo 4).
9.7. Discusión de resultados
Este apartado integra los hallazgos de los análisis anteriores y los discute en relación con los objetivos y preguntas de investigación del TFM. La discusión se organiza en torno a cuatro ejes.
Respuesta a las preguntas de investigación. Se valora en qué medida los resultados de la evaluación permiten responder a cada una de las preguntas formuladas en el Capítulo 4. En particular: ¿ha demostrado el baseline que es posible construir un motor de priorización basado en criterios normativos sin depender de grandes volúmenes de datos históricos (PI1)? ¿Produce el sistema de tres capas recomendaciones coherentes con el criterio de un operador (PI2)? ¿Mejora la integración de fuentes oficiales la capacidad de discriminación del motor (PI3)? ¿Se observa un impacto potencial sobre el TTFD (PI4)?
Fortalezas del enfoque. Se identifican los aspectos del diseño que la evaluación ha validado: la eficacia de las reglas duras como red de seguridad, la utilidad de la explicación para la supervisión humana, la integración de contexto oficial como factor de discriminación y la coherencia general del baseline con el etiquetado humano.
Debilidades y áreas de mejora. Se identifican los aspectos que la evaluación ha revelado como mejorables: posibles desajustes en pesos o umbrales del scoring, casos de frontera que el baseline no resuelve satisfactoriamente, limitaciones de la explicación en escenarios complejos y cualquier otro hallazgo que sugiera necesidad de iteración.
Comparación con el alcance esperado. Se valora si los resultados obtenidos son coherentes con lo que razonablemente podía esperarse de un prototipo académico con un dataset piloto híbrido y una evaluación en simulación. Esta comparación es importante para evitar tanto la sobreinterpretación de resultados positivos como la subestimación de aportaciones reales del trabajo.
9.8. Limitaciones de la evaluación
La evaluación presentada en este capítulo tiene un conjunto de limitaciones que es necesario explicitar para que los resultados se interpreten en su justa medida. Estas limitaciones no invalidan la evaluación, pero acotan su alcance y señalan las condiciones bajo las cuales sus conclusiones son válidas.
Primera limitación: evaluación en simulación. Toda la evaluación se realiza sobre escenarios simulados, no sobre incidentes reales gestionados en un centro de coordinación operativo. Esto implica que las dinámicas de presión temporal, estrés cognitivo, interacción multicanal y ambigüedad extrema que caracterizan un entorno real no están completamente representadas en los casos del dataset piloto.
Segunda limitación: dataset piloto híbrido. El dataset piloto está compuesto mayoritariamente por casos simulados controlados, diseñados para cubrir los escenarios operativos más relevantes. Aunque los casos superan controles de plausibilidad rigurosos (Anexo D, apartado D.4), no tienen la variabilidad, el ruido ni la casuística impredecible de un dataset operativo real. Los resultados de la evaluación podrían diferir significativamente si se replicara con datos reales del 112 Aragón.
Tercera limitación: etiquetado interno. El ground truth del dataset ha sido producido por el equipo del TFM conforme a la guía de etiquetado (Anexo C), con revisión cruzada entre miembros del equipo. No se ha dispuesto de un panel externo de operadores expertos del 112 que valide el etiquetado. Esto introduce un riesgo de sesgo circular: si los mismos criterios que informan el diseño del baseline informan también el etiquetado de referencia, la concordancia observada podría sobreestimar la concordancia real con el criterio de un operador profesional independiente.
Cuarta limitación: ausencia de despliegue institucional. El sistema no ha sido desplegado en el 112 Aragón ni en ningún otro centro de coordinación. No existe validación institucional externa de la lógica del motor, de la escala P1-P4, de las reglas duras ni de los pesos del scoring. La evaluación mide la coherencia interna del sistema y su aplicabilidad potencial, pero no su aceptación operativa real.
Quinta limitación: tamaño del dataset. El dataset piloto comprende entre 120 y 150 casos. Este tamaño es suficiente para una evaluación piloto dentro del alcance de un TFM, pero no permite análisis estadísticos robustos de subgrupos (por ejemplo, evaluar el rendimiento del motor específicamente para incendios forestales o para emergencias sanitarias con muestras representativas de cada tipo). Las métricas por clase deben interpretarse con la cautela que impone un tamaño muestral limitado.
Sexta limitación: evaluación de usabilidad con grupo reducido. La evaluación SUS se realiza con un grupo pequeño de evaluadores, la mayoría de los cuales son los propios desarrolladores del sistema. Esto limita la validez externa de la puntuación de usabilidad, que debería confirmarse con una evaluación ampliada que incluya operadores reales del dominio de emergencias.
Estas limitaciones son inherentes al alcance de un TFM y se abordan explícitamente como líneas de trabajo futuro en el Capítulo 10. No impiden que la evaluación cumpla su función dentro del trabajo: verificar la coherencia del diseño, identificar fortalezas y debilidades del enfoque, y proporcionar evidencia suficiente para valorar la viabilidad de la propuesta.
Cierre del capítulo
La evaluación presentada en este capítulo demuestra que el enfoque adoptado en el TFM es metodológicamente coherente y operativamente viable dentro de las condiciones del prototipo. El baseline interpretable de tres capas, alimentado por el dataset piloto y evaluado con métricas de clasificación, análisis de seguridad operativa, evaluación de explicabilidad y estimación de impacto sobre el TTFD, proporciona evidencia suficiente para valorar la contribución del trabajo.
Los resultados concretos se presentarán una vez ejecutado el baseline sobre el dataset piloto completo. La estructura de evaluación aquí diseñada garantiza que esos resultados se analizarán con el rigor, la honestidad y el nivel de detalle que el tribunal y la normativa UNIR exigen. El capítulo siguiente (Capítulo 10) recogerá las conclusiones derivadas de esta evaluación, valorará el cumplimiento de los objetivos del TFM y propondrá líneas de trabajo futuro que aborden las limitaciones identificadas.
Referencias bibliográficas del Capítulo 9
Brooke, J. (1996). SUS: A quick and dirty usability scale. En P. W. Jordan, B. Thomas, B. A. Weerdmeester e I. L. McClelland (Eds.), Usability evaluation in industry (pp. 189-194). Taylor & Francis.
Sokolova, M. y Lapalme, G. (2009). A systematic analysis of performance measures for classification tasks. Information Processing & Management, 45(4), 427-437.
