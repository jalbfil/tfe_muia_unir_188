Tema 10

Investigación y Gestión de Proyectos en Inteligencia Artificial

# Tema 10. Investigación en sistemas cognitivos

# Índice

## Esquema

## Ideas clave

- 10.1. Introducción y objetivos
- 10.2. Introducción a la computación cognitiva
- 10.3. Elementos de un sistema cognitivo
- 10.4. Big data y computación cognitiva
- 10.5. Percepción computacional
- 10.6. Procesamiento de lenguaje natural
- 10.7. Proyectos de investigación sobre sistemas cognitivos
- 10.8. Referencias bibliográficas

## A fondo

- The rise of cognitive computing
- Watson and the Jeopardy! Challenge

## Test

Esquema

![img-0.jpeg](img-0.jpeg)

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Esquema

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

# 10.1. Introducción y objetivos

Los sistemas cognitivos están en auge en los últimos tiempos. Aquí se proporciona una descripción conceptual de la computación cognitiva y un listado de sus aplicaciones más inmediatas. Los objetivos planteados son los siguientes:

- Reconocer las peculiaridades de un sistema cognitivo.
- Conocer las utilidades de las aplicaciones cognitivas en el ámbito empresarial.
- Ser capaz de identificar limitaciones de los sistemas cognitivos.

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

# 10.2. Introducción a la computación cognitiva

En los últimos años algunos errores asociados a las aplicaciones de inteligencia artificial han aparecido en los medios especializados. Conocido fue el caso de chatbot de Microsoft, que en el mismo día realizó comentarios racistas, antisemitas e incluso misóginos.

Accede a la noticia a través del siguiente enlace: http://www.elmundo.es/tecnologia/2016/03/28/56f95c2146163fdd268b45d2.html

Pero hay más, como por ejemplo el caso del chatbot de Facebook que «inventó» un nuevo idioma, el sistema de detección facial del iPhone X engañado por una máscara, un coche de conducción autónoma involucrado en un accidente en Las Vegas, etc.

Accede al artículo a través del siguiente enlace: https://medium.com/@Synced/2017-in-review-10-ai-failures-4a88da1bdf01

Estos errores son la prueba de que, aunque son muy importantes los logros conseguidos por la disciplina, todavía queda mucho camino por recorrer.

Muchos de estos fallos se deben a que los creadores de las aplicaciones no han sido capaces de proporcionar a la máquina el contexto adecuado a su caso de uso.

Por ejemplo, en el caso de Face ID, la aplicación de reconocimiento facial del móvil iPhone X, los desarrolladores han entrenado a la aplicación para poder identificar rostros y, por consiguiente, personas. Pero una persona está unida a un tronco, tiene una cabeza, respira... Realmente, ¿entiende la máquina que está identificando a una persona o, por el contrario, se

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

limita a analizar unas similitudes entre dos representaciones de una realidad? ¿Entiende la máquina de forma plena el contexto de la actividad que está realizando? La respuesta a esta pregunta no es trivial, porque primero tendremos que acordar qué significa «entiende». No obstante, parece obvio que la máquina maneja un contexto mucho más reducido que el que contempla un humano, puesto que este último nunca hubiese proporcionado acceso al teléfono a alguien con una máscara. El humano (medianamente avispado) reconocería que se trata de una máscara y pediría a su portador que se identificase correctamente.

La computación cognitiva se ocupa de la búsqueda de soluciones eficientes que permitan a los humanos colaborar con las máquinas de forma plena y eficaz, para generar nuevos conocimientos y experiencias.

Para ello, una de las principales necesidades es proporcionar a la máquina contexto sobre el entorno y el objetivo a conseguir. Por este motivo, las soluciones cognitivas deben hacer uso de un volumen de información muy amplio y diverso, surge aquí la relación entre la computación cognitiva y el paradigma big data.

La gran disponibilidad de datos, la reducción del coste de almacenamiento y las mejoras tecnológicas que permiten procesar grandes volúmenes de datos a altas velocidades han impulsado este tipo de soluciones.

Un sistema cognitivo se compone fundamentalmente de tres principios fundamentales:

- Aprendizaje: el sistema debe ser capaz de aprender en base a un conjunto de observaciones y realizar predicciones sobre un dominio concreto.

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

- Modelado: el aprendizaje toma como base la representación de un modelo y un conjunto de reglas de inferencia.
- Generación de hipótesis: un sistema cognitivo debe asumir que no existe una única respuesta válida. Es decir, un sistema cognitivo es un sistema probabilístico capaz de emitir varias respuestas dando una probabilidad a cada una de ellas.

Estos tres principios fundamentales se basan todos en el almacenamiento, catalogación y uso eficiente de datos que guían la toma de decisiones. Los sistemas cognitivos se encuentran todavía en una fase de desarrollo incipiente. El desarrollo de este tipo de productos involucra aspectos provenientes de otras disciplinas técnicas como el aprendizaje automático, el procesamiento de grandes volúmenes de datos, el internet de las cosas, procesamiento del lenguaje natural, razonamiento probabilístico, visualización, etc.

Los sistemas cognitivos están orientados a entornos probabilísticos, no determinísticos.

Un ejemplo típico de este escenario es el entorno clínico. Los síntomas del paciente invitan a pensar en una enfermedad concreta con una determinada probabilidad de acierto. El trabajo del facultativo en muchas ocasiones consiste en ir explorando el amplio abanico de opciones hasta localizar la raíz del problema de forma concreta. En general, se puede decir que este tipo de sistemas está enfocado para contextos que deben trabajar en un entorno de incertidumbre teniendo a su disposición una importante variedad de datos de distinta complejidad.

Investigación y Gestión de Proyectos en Inteligencia Artificial
Tema 10. Ideas clave
© Universidad Internacional de La Rioja (UNIR)

Ideas clave

# 10.3. Elementos de un sistema cognitivo

Un sistema cognitivo consta de diferentes elementos que incluyen desde la capa de hardware al software y modelos implementados. Aunque cada solución concreta particulariza su propio diseño, es posible caracterizar una serie de elementos comunes. La Figura 1 muestra los componentes principales de un sistema cognitivo:

![img-1.jpeg](img-1.jpeg)
Figura 1. Elementos de un sistema cognitivo. Fuente: Hurwitz, Kaufman y Bowles, 2015.

Un sistema cognitivo se alimenta de datos. Estos datos pueden ser estructurados (por ejemplo, los procedentes de bases de datos relacionales) o no estructurados (fotografías, vídeos, sonido, texto...).

Los datos constituirán la base para la toma de decisiones. Gracias a ellos el sistema puede interpretar el entorno y crear los modelos adecuados. Los datos precisan de una infraestructura de almacenamiento. Esta infraestructura admite muchas modalidades, normalmente basadas en productos en la nube.

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

De cara a planificar los recursos necesarios, debemos comprender que un sistema de estas características no solo tiene que almacenar los datos que recibe de entrada, la propia actividad del sistema y los modelos desarrollados crean nuevos datos que también alimentan al sistema. Además, el producto también puede contar con fuentes de datos internas y permanentes como, por ejemplo, las referidas a restricciones de contexto que se quieren mantener de forma constante.

El acceso a los datos se gestiona a través de una capa cuya labor es precisamente intermediar con la capa de almacenamiento. El módulo de acceso a datos prepara los datos para su consumo y es el encargado de verificar que la calidad de los datos es adecuada, monitorizando constantemente el proceso. Sobre esta capa se mantiene un corpus, con el cometido de codificar computacionalmente el conocimiento existente, una capa de servicios de procesamiento y una capa de servicios analíticos.

Un corpus de conocimiento estructura y codifica todo el conocimiento asociado a un ámbito concreto. Para su construcción es habitual recurrir al uso de ontologías. Estas ontologías permiten definir los conceptos, establecer sus propiedades y fijar relaciones entre ellos.

De forma continuada un proceso de aprendizaje automático alimenta la toma de decisiones del sistema. El proceso parte de una hipótesis como explicación verificable ante un hecho observado. Dicha hipótesis es verificada mediante datos para finalmente llegar a una conclusión que culmina en una acción o decisión. El proceso de aprendizaje conlleva un ajuste continuo del modelo o de los modelos.

Por último, es preciso crear varios componentes que facilitan la interacción máquina-humano e, incluso, máquina-máquina. La capa de visualización ayuda a interpretar los resultados y acciones sugeridas por el sistema, mientras que los servicios API

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

(por sus siglas en inglés: Application Program Interface) facilitan el acceso automatizado a las funcionalidades que ofrece el sistema.

## Diseño de sistemas cognitivos

En su sistema de computación cognitiva el modelo hace referencia tanto al corpus como a los algoritmos que permiten ejecutar la toma de decisiones. El modelo desarrollado por los programadores iniciales está cambiando continuamente. El aprendizaje continuo es la esencia de un sistema cognitivo. Dicho aprendizaje solo se culmina si el sistema es capaz de actualizar constantemente el modelo que guía su actividad. Asegurar esta actualización continua del modelo es el principal requisito a la hora de diseñar un sistema cognitivo.

Todo sistema cognitivo se debe diseñar de forma que:

- Permita la ingesta en el sistema de toda la información necesaria.
- Organice los datos de forma que se permita el acceso y análisis de forma eficiente.
- Permita actualizar el corpus y los modelos iniciales.
- Asegure el cumplimiento de la normativa vigente y los estándares de seguridad adecuados.
- Permita emplear las técnicas adecuadas para la extracción de conocimiento y toma de decisiones.

## Ontologías

Las ontologías permiten la representación formal de los conceptos de un dominio y las relaciones entre ellos. De esta forma no solo se modela el conocimiento existente, sino que, además, permite la estandarización del dominio

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

creando un mapa conceptual que es compartido y comúnmente usado. Las ontologías facilitan el almacenamiento ordenado de información, la búsqueda de recursos y la comunicación entre distintos dispositivos. Gracias a las ontologías podemos también formalizar muchas de las suposiciones de partida entre los elementos, en base a relaciones entre conceptos, atributos de los elementos, etc.

Las ontologías se suelen representar gráficamente en forma de grafo para facilitar su comprensión.

![img-0.jpeg](img-0.jpeg)
Figura 2. Ejemplo de parte de una ontología asociada al dominio del vino. Fuente: https://protege.stanford.edu/publications/ontology_development/image002.jpg

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

Otro ejemplo algo más elaborado podría ser el que representa la Figura 3.

![img-1.jpeg](img-1.jpeg)
Figura 3. Ejemplo de ontología clínica para una aplicación de telemedicina. Fuente: https://www.researchgate.net/figure/E-health-application-ontology-Medical-applications-which-are-currently-available-on-the_269700233

La herramienta Prótegé (https://protege.stanford.edu/), gestionada ahora por la Universidad de Stanford en colaboración con la Universidad de Manchester, es una de las herramientas más útiles para la creación de ontologías.

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

# 10.4. Big data y computación cognitiva

Se ha insistido mucho en este tema en la necesidad de disponer de grandes volúmenes de datos como materia primera para generar aplicaciones realmente eficaces. En otro caso, los sistemas cognitivos podrían encontrar serias dificultades para mostrar resultados consistentes, fiables y relevantes. Además, y dado que se precisa tanto de datos estructurados como no estructurados, es necesario emplear otras tecnologías distintas de las bases de datos relacionales, puesto que estas últimas están diseñadas específicamente para interactuar con datos relacionales.

*Big data* no hace referencia a una tecnología concreta. *Big data* hace referencia a un paradigma centrado en capturar información de fuentes de datos diversas, que se generan a una velocidad considerable y con un gran volumen. Y esta actividad viene inevitablemente unida a la obtención de valor para el negocio.

Acumular datos sin más no tiene ningún sentido. Es la obtención de información útil y conocimiento que apoye la toma de decisiones la razón de ser de este paradigma.

Las tecnologías que apoyan este nuevo proceso son varias y diversas. Intentado hacer una generalización, podríamos detectar algunas grandes categorías:

- Bases de datos NoSQL (por sus siglas en inglés *Structured Query Language*).
- Sistemas de archivos distribuidos.
- Sistemas de cómputo en paralelo.

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

# Bases de datos NoSQL

NoSQL hace referencia a Non-only SQL. Estas bases de datos se caracterizan por la facilidad de desarrollo, el desempeño escalable, la alta disponibilidad y la resiliencia.

A cambio de permitir mayores cotas de flexibilidad y versatilidad, estas herramientas han debido renunciar en mayor o menor medida a las propiedades ACID (Atomicity, Consistency, Isolation and Durability) de los sistemas de bases de datos relacionales tradicionales.

ACID, como acabamos de ver, es el acrónimo para referirse a las propiedades de atomicidad, consistencia, aislamiento y durabilidad:

- La **atomicidad** implica que una transacción se ejecuta completamente o no se ejecuta en absoluto.
- **Consistencia** quiere decir que una vez se ha ejecutado una transacción, los datos deben acoplarse al esquema de la base de datos.
- El **aislamiento** requiere que las transacciones simultáneas se ejecuten por separado.
- La **durabilidad** es la capacidad de recuperarse de un error inesperado del sistema o de un corte de energía y volver al último estado conocido.

Mantener estas propiedades ayuda a construir bases de datos más robustas, menos propensas a fallos y más formales. Sin embargo, para conseguir estas propiedades, los sistemas gestores de bases de datos incurren en penalización de rendimiento que no son sostenibles cuando la base de datos escala a grandes tamaños. Por ese

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

motivo, los sistemas NoSQL buscan crear bases de datos sin estas restricciones para ser mucho más rápidos y poder procesar mayor número de datos. A cambio, estos sistemas son más vulnerables a fallos.

Existen diversos tipos de bases de datos NoSQL, incluyendo bases de datos documentales y bases de datos orientadas a grafos. Un ejemplo es MongoDB o Cassandra.

# Sistemas de archivos distribuidos

Un sistema de archivos distribuidos proporciona un sistema de almacenamiento permanente apoyándose en una infraestructura en red. De esta forma se puede aprovechar el potencial de una red de computadoras y escalar las capacidades de almacenamiento en un sistema multiusuario.

Los sistemas de archivos distribuidos son esenciales en el ecosistema big data. La replicación de la información es una de sus características esenciales. De esta forma se facilita el acceso concurrente de los usuarios a la información. Adicionalmente, los sistemas big data de archivos distribuidos cuentan con una configuración diferente a los sistemas de archivos tradicionales.

Una de las diferencias más relevantes es el tamaño de bloque de disco. El tamaño de bloque de disco es mucho más grande en los sistemas big data que en sistemas de archivos tradicionales. De esta forma y con una sola búsqueda y acceso se accede a mucha más información de golpe. A cambio, los sistemas big data son una muy mala opción si una de las funcionalidades principales del sistema debe ser la actualización y modificación continua de la información.

# Sistemas de cómputo en paralelo

Gran parte de los procesamientos de aprendizaje automático implican la realización de múltiples cálculos repetitivos o susceptibles de ser descompuestos en tareas similares que se realizan una y otra vez. Los sistemas de cómputo en paralelo

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

aprovechan la capacidad de cálculo de redes de computadoras conectadas entre sí proporcionando la escalabilidad de cómputo necesaria para procesar grandes volúmenes de información de forma eficiente.

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

# 10.5. Percepción computacional

Los sistemas cognitivos intentan interactuar con los humanos usando su mismo lenguaje. Como hemos comentado anteriormente, la idea es que los sistemas cognitivos puedan procesar el lenguaje natural para que puedan entender a los usuarios que los usan, por ejemplo, mediante órdenes de voz. También necesitan en según qué entornos percibir lo que le rodea. La percepción computacional es una serie de algoritmos que permiten a un software reconocer imágenes, sonidos, etc. De forma que puede procesar la voz humana o puede procesar el rostro de una persona para reconocerle.

Podemos definir la percepción como la capacidad de los organismos para obtener información sobre su ambiente a partir de los efectos que los estímulos producen sobre los sistemas sensoriales. La percepción computacional es la capacidad que tiene las máquinas de imitar la percepción de los organismos.

Tradicionalmente, hacer que una computadora procesara imágenes, por ejemplo, en tiempo real, era algo bastante difícil de conseguir. Sin embargo, con las mejoras de las técnicas y el aumento de la potencia de cálculo disponible, actualmente un computador puede reconocer, clasificar, etiquetar y analizar imágenes de forma bastante solvente. Aunque sigue siendo una de las tareas pendientes de mejora, las técnicas de machine learning utilizadas para la visión por computador, por ejemplo, nos permiten hacer cosas que eran impensables hace tiempo.

Las redes más usadas para el procesado de imágenes son las redes convolucionales y los autoencoders. Estas se van aplicando por capas y estas capas se concatenan unas con las otras. Es muy típico que en las primeras capas la red aprenda unas simples características y sobre ellas se va construyendo otras capas que realizan otras áreas, por ejemplo, la diferenciación de objetos.

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

Los autoencoders ayudan a la extracción de características de una imagen, lo que hace que se elimine el paso previo de clasificación que se solía dar antiguamente.

Las redes convolucionales se utilizan también para procesar las imágenes. Normalmente se aplican en las primeras capas para extraer características, reducir la dimensión de la imagen, etc.

Finalmente, se suelen utilizar perceptrones multicapa simples para la etapa de clasificación. Un ejemplo de esta arquitectura por capas se puede ver en la Figura 4.

![img-0.jpeg](img-0.jpeg)
Figura 4. Esquema de una red que procesa imágenes con diferentes capas. Fuente: https://www.ellaberintodefalken.com/2019/10/vision-artificial-redes-convolucionales-CNN.html

Con estos modelos se han conseguido importantes avances en esta área. Aquí tenemos un ejemplo de una aplicación para crear tiendas autónomas sin dependientes:

Accede al siguiente enlace: https://computerhoy.com/noticias/tecnologia/startup-francesa-tiendas-autonomas-inteligencia-vision-artificial-712177

La visión artificial tiene diferentes aplicaciones, podemos resumirlas como:

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

- Reconocimiento de objetos: decir qué objetos hay en una imagen, etiquetar las caras en una fotografía, etc.
- Reconstrucción de objetos 3D a partir de objetos 2D. Poder construir a partir de una serie de imágenes en 2D un objeto en 3D. Se le suele denominar fotometría.
- Análisis de vídeo: reconocer en tiempo real intrusos, la posición de un objeto, la distancia. A veces se apoyan en sensores de infrarrojo que ayudan a estos cálculos.
- Aplicaciones industriales. Por ejemplo, se utiliza visión artificial para el control de calidad de ciertos productos, para su clasificación, el guiado de robots, la medición de objetos, etc.

Para conseguir esos resultados se necesita normalmente varias etapas. Normalmente hay que procesar de alguna forma la señal visual para ayudar a los algoritmos de machine learning a trabajar con las imágenes. Así que pueden procesarse la imagen para eliminar ruido, aplicar la transformada de Fourier para analizarla, detectar los bordes de los objetos, etc.

La iluminación es un aspecto clave en la visión artificial. Muchas veces un objeto no se reconoce por cambios en la iluminación de la escena. Así que, si utilizamos la visión artificial en un entorno controlado, es mejor ayudar al sistema de visión con una iluminación apropiada.

# Ventajas de la visión artificial

Algunas ventajas de la visión artificial sobre la humana son las siguientes: la visión humana es mejor para la interpretación cualitativa y para interpretar escenas sin estructura, mientras que en la visión artificial destaca que es mejor en tomar medidas cuantitativas sobre escenas con cierta estructura, precisión y repetibilidad.

Investigación y Gestión de Proyectos en Inteligencia Artificial
Tema 10. Ideas clave
© Universidad Internacional de La Rioja (UNIR)

Ideas clave

Por ejemplo, en una línea de producción, un sistema de visión artificial puede inspeccionar cientos, o incluso miles, de piezas por minuto. También puede procesar detalles más pequeños si la cámara tiene mucha resolución o aumento.

## Procesamiento y generación de sonido

Además de la visión como percepción computacional debemos tener en cuenta también el procesamiento del sonido. Y no solo el procesamiento sino la generación de sonido. Trabajos relacionados con esta área son los siguientes:

- Síntesis de voz.
- Reconocimiento del habla.
- Traducción automática.
- Generación de música.
- Reconocimiento de objetos mediante el audio.

© Universidad Internacional de La Rioja (UNIR)

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

Ideas clave

# 10.6. Procesamiento de lenguaje natural

Se ha insistido mucho en lo que llevamos de tema en que los sistemas cognitivos introducen nuevos elementos en la relación humano-máquina. Efectivamente, muchos de estos sistemas contemplan en su funcionalidad una interacción continua entre las personas y las máquinas.

El principal medio de expresión de los humanos es el lenguaje, ya sea oral o escrito. Por tanto, las técnicas de procesamiento del lenguaje natural forman un papel esencial aquí.

Para comprender el mensaje emitido, las técnicas de procesamiento del lenguaje natural deben considerar el momento o fecha en la que se emite el mensaje, identificar al emisor, detectar los pronombres y reconocer a quién se están refiriendo, quién habla de quién, etc.

Es preciso catalogar correctamente los diferentes conceptos (personas, lugares, cosas) y la relación que guardan entre ellos. El orden de las palabras, la propia sintaxis, el uso de sinónimos y antónimos, frases hechas..., producen variaciones y particularizaciones del significado que es preciso aprehender.

La ambigüedad y el uso de palabras como los conectores contribuyen a añadir una capa adicional de complejidad al proceso. El análisis probabilístico de las palabras que aparecen (y el orden en el que lo hacen) en los textos empleados durante el proceso de aprendizaje puede añadir algo de claridad a la tarea.

Las cadenas de Márkov son ampliamente utilizadas para el análisis probabilístico de cadenas de texto. En la teoría de la probabilidad se conoce como cadena de Márkov o modelo de Márkov a un tipo especial de proceso estocástico discreto en el que la probabilidad de que ocurra un evento depende solamente del evento inmediatamente anterior.

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

Esta característica de falta de memoria recibe el nombre de propiedad de Markov: https://es.wikipedia.org/wiki/Cadena_de_M%C3%A1rkov

El lenguaje hablado o escrito constituye un ejemplo de dato no estructurado. Interpretar correctamente mensajes lingüísticos es una tarea nada trivial debido a la importancia del contexto. El significado de una expresión concreta puede variar en función de la situación y la entonación. Por ejemplo, imaginemos el siguiente diálogo:

—Buenas tardes, Sr. Martín. Le llamamos del servicio de atención al cliente para hacerle una pregunta rápida que nos ayuda a mejorar: ¿está satisfecho con nuestros servicios?

—Sí, mucho.

¿Qué ha interpretado la operadora ante la respuesta del cliente? Leyendo el texto sin disponer de más información, parece simple deducir que la respuesta del cliente es positiva. Por tanto, un punto extra para la compañía y su impecable servicio. No obstante, un mensaje oral viene acompañado de una entonación concreta. El tono del mensaje forma parte del mensaje al igual que los gestos del emisor. El tono del mensaje puede transmitir sarcasmo, ironía, alegría y un sinfín de connotaciones que complementan el mensaje.

Las técnicas de deep learning han permitido evolucionar las técnicas de procesamiento del lenguaje gracias a su potencia para representar el proceso de aprendizaje y el propio conocimiento. En este ámbito, una de las mayores innovaciones ha sido considerar el vecindario de una palabra como fuente muy

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

relevant para determinar el significado concreto de esa palabra. De esta forma, gracias al deep learning se ha conseguido crear redes que son capaces de categorizar una palabra por proximidad, usando redes de reducción de dimensionalidad con algoritmos no supervisados. Estos algoritmos se conocen con el nombre de **embeding** y permiten comprimir una red de palabras representada como vectores equidistantes de un espacio multidimensional K (por ejemplo, usando one-hot encoding) a un espacio multidimensional N menor que K que representa la distancia semántica entre diferentes palabras. Una de las principales herramientas para conseguir esto es **Word2vec**. Word2Vec es una red preentrenada que agrupa palabras de forma compacta.

![img-1.jpeg](img-1.jpeg)
Figura 5. Ejemplo de uso de Word2vec con ciertas palabras. Fuente: https://www.springboard.com/blog/introduction-word-embeddings/

Usando este tipo de herramientas se consigue codificar palabras que, usando redes de neuronas profundas, son capaces de realizar multitud de tareas.

De forma concreta, se han mostrado aplicaciones muy relevantes en campos como:

- Clasificación de texto y documentos: incluyendo clasificar mensajes según la tonalidad positiva o negativa mostrada, filtrado de correo electrónico no deseado, clasificación automática de noticias, sentencias, informes, según su categoría, etc.

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

Ideas clave

- Modelado del lenguaje: con el objetivo de sugerir correcciones gramaticales, sugerencias de palabras, etc.
- Reconocimiento del habla: posibilitando, por ejemplo, generar de forma automática los subtítulos de un vídeo.
- Descripción automática: posibilitando describir una imagen, vídeo... de forma automática.
- Traducción automática.
- Resumen automático de documentos: lo que permitiría, por ejemplo, resumir de forma automática una sentencia judicial.
- Respuesta automática: faculta a la máquina para interactuar con el humano proporcionando de forma directa la pregunta a una pregunta formulada.
- Generación automática de texto (GPT 2/3).

Investigación y Gestión de Proyectos en Inteligencia Artificial
Tema 10. Ideas clave
© Universidad Internacional de La Rioja (UNIR)

Ideas clave

# 10.7. Proyectos de investigación sobre sistemas cognitivos

A nivel empresarial, el objetivo principal de la computación cognitiva es apoyar el proceso de toma de decisiones presentando el conocimiento necesario en el momento oportuno de la forma adecuada. Gracias a estas aplicaciones, las compañías pueden diferenciar sus productos y servicios y obtener ventaja sobre sus competidores.

© Universidad Internacional de La Rioja (UNIR)

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

Ideas clave

# 10.8. Referencias bibliográficas

Hurwitz, J., Kaufman, M. y Bowles, A. (2015). Cognitive Computing and Big Data Analytics. Estados Unidos: Wiley.

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. Ideas clave

© Universidad Internacional de La Rioja (UNIR)

A fondo

# The rise of cognitive computing

Dickinson, M. (9 de noviembre de 2016). The rise of cognitive computing. BBC Future. Recuperado de http://www.bbc.com/storyworks/future/an-intelligent-future/the-rise-of-cognitive-computing

Reportaje de la BBC sobre la computación cognitiva, aplicaciones y futuro.

Investigación y Gestión de Proyectos en Inteligencia Artificial

© Universidad Internacional de La Rioja (UNIR)

Tema 10. A fondo

A fondo

# Watson and the Jeopardy! Challenge

IBM Research (6 de noviembre de 2013). Watson and the Jeopardy! Challenge [Vídeo]. YouTube. Recuperado de https://youtu.be/P18EdAKuC1U

Este vídeo nos permite conocer un poco más a fondo la historia de Watson y su participación en el programa Jeopardy.

Investigación y Gestión de Proyectos en Inteligencia Artificial

Tema 10. A fondo

© Universidad Internacional de La Rioja (UNIR)

Test

1. En lo que se refiere a la relación entre big data y computación cognitiva:
A. Las soluciones cognitivas ayudan a que las tecnologías big data sean más eficientes.
B. Los sistemas cognitivos se alimentan de información big data para tomar las mejores decisiones.
C. Ambos usan las mismas tecnologías.
D. La computación cognitiva abarata los costes de las tecnologías big data.

2. Los tres principios fundamentales que componen un sistema cognitivo son:
A. Aprendizaje, modelado y análisis estadístico.
B. Inferencia, modelado y módulo de procesamiento de lenguaje natural.
C. Aprendizaje, modelado y módulo de procesamiento de lenguaje natural.
D. Aprendizaje, modelado y generación de hipótesis.

3. Son elementos de un sistema cognitivo:
A. Una infraestructura de almacenamiento.
B. Una capa de servicios analíticos.
C. Una capa de servicios de visualización.
D. Todos los anteriores.

4. Las ontologías sirven para:
A. Representar formalmente el conocimiento asociado a un dominio con las relaciones entre conceptos.
B. Analizar grafos.
C. Acceder a datos big data.
D. Ninguno de los anteriores.

Investigación y Gestión de Proyectos en Inteligencia Artificial
Tema 10. Test
© Universidad Internacional de La Rioja (UNIR)

Test

5. Para diseñar un sistema cognitivo se debe tener en cuenta:
A. Organizar los datos de forma eficiente.
B. Permitir la ingesta de todos los datos necesarios.
C. Asegurar el cumplimiento de la normativa vigente.
D. Todas las anteriores.

6. ¿Qué es el embedding?
A. Usar tecnologías deep learning para clasificar palabras en grupos gramaticales.
B. El uso de deep learning para agrupar texto como vectores de distancia de forma compacta.
C. Emplear deep learning para generar texto de forma automática.
D. Ninguna de las anteriores.

7. Las bases de datos NoSQL:
A. Son adecuadas para datos estructurados.
B. Son las más lentas de todas.
C. Son adecuadas para datos no estructurados.
D. Prohíben el uso de SQL o variantes parecidas.

8. Los sistemas de archivos distribuidos para el big data:
A. No replican los datos, pues es ineficiente.
B. Replican la información para agilizar el acceso.
C. Tienen un tamaño de bloque similar a los sistemas operativos básicos.
D. Todas la anteriores son ciertas.

Investigación y Gestión de Proyectos en Inteligencia Artificial
Tema 10. Test
© Universidad Internacional de La Rioja (UNIR)

Test

9. El sistema de IBM Watson:

A. Es un ejemplo muy primitivo de lo que se puede conseguir con la computación cognitiva.
B. Es una innovación total que ya está preparado para usarse a gran escala independientemente del dominio en multitud de entornos, aunque todavía hay un campo grande de mejora e investigación.
C. Ha resultado un fracaso total.
D. No tiene aplicaciones comerciales.

10. Los sistemas de percepción computacional han mejorado mucho en los últimos años principalmente debido a:

A. Al descubrimiento de nuevos algoritmos de filtrado de imagen.
B. A la mejora de los modelos basados en *deep learning* y el aumento de la capacidad computacional.
C. A un aumento de la capacidad de las cámaras y sensores disponibles.
D. Ninguna de las anteriores.

Investigación y Gestión de Proyectos en Inteligencia Artificial
Tema 10. Test
© Universidad Internacional de La Rioja (UNIR)