Organización del trabajo en grupo
0.1. Introducción al trabajo grupal
El presente Trabajo Fin de Máster se ha desarrollado en modalidad grupal, de conformidad con el procedimiento establecido por la Universidad Internacional de La Rioja (UNIR) para la elaboración y defensa de Trabajos Fin de Estudios en grupo. Esta modalidad responde a la propia naturaleza del proyecto, que requiere combinar el diseño analítico del motor de priorización, la construcción del backend que lo sostiene y la interfaz que permite al operador interactuar con el sistema.
La organización se ha planteado de modo que cada integrante asuma un bloque de trabajo con entidad suficiente para constituir, por sí solo, un Trabajo Fin de Estudios individual. Al mismo tiempo, la coordinación entre los tres ejes garantiza que el prototipo resultante sea un producto coherente e integrado, y no la suma aislada de partes inconexas. A lo largo de las siguientes secciones se detallan los integrantes del equipo, sus roles, la distribución de responsabilidades técnicas y académicas, el reparto de capítulos de la memoria y los mecanismos de coordinación que han articulado el trabajo conjunto.
0.2. Integrantes del equipo y roles asignados
El equipo está formado por tres estudiantes del Máster Universitario en Inteligencia Artificial de la UNIR, bajo la dirección del Dr. Andrés Soto Villaverde. Cada integrante aporta un perfil profesional distinto.
0.2.1. Coordinación general, lógica funcional e integración
Responsable principal: Juan Carlos Albert Fillol.
Este eje abarca la definición y justificación del problema operativo desde la perspectiva del dominio de emergencias; el análisis del marco normativo estatal y autonómico aplicable; el diseño conceptual del motor de priorización, que incluye la taxonomía de incidentes, la matriz de variables, la escala de prioridad operativa P1–P4 y la guía de etiquetado; el diseño de la arquitectura lógica del baseline interpretable —con sus tres capas: reglas duras, scoring explicable y capa de confianza y explicación—; la coordinación general del proyecto en términos de planificación, seguimiento de entregas e integración de las contribuciones individuales; y la supervisión de la evaluación del sistema en escenarios simulados.
0.2.2. Desarrollo backend y lógica de servicios
Responsable principal: Brian Mathias Pesci Juliani.
Este eje comprende el diseño e implementación de la arquitectura backend del prototipo; la traducción a código de la lógica del motor de priorización a partir del diseño analítico definido por el equipo; el diseño del esquema de datos y los mecanismos de persistencia; el desarrollo de los servicios de integración con fuentes de datos contextuales —como AEMET OpenData o el Sistema Nacional de Cartografía de Zonas Inundables (SNCZI) del MITECO—; la implementación del pipeline de procesamiento de incidentes, desde la ingesta hasta el cálculo de prioridad; y el desarrollo de la API que conecta el backend con la interfaz de usuario.
0.2.3. Desarrollo frontend e interfaz de usuario
Responsable principal: Ancor González Carballo.
Este eje incluye el diseño e implementación de la interfaz de usuario del prototipo; los componentes de visualización de incidentes priorizados; la presentación al operador de la explicación que genera el sistema —factores determinantes, nivel de confianza y situación operativa sugerida—; los mecanismos de interacción que permiten revisar, validar, corregir o rechazar la recomendación del sistema; y los elementos de trazabilidad visual necesarios para garantizar la supervisión humana.
0.3. Distribución de capítulos y contribuciones individuales
La Tabla 1 presenta la distribución de responsabilidades sobre los capítulos y anexos de la memoria. Se ha buscado un reparto equilibrado de la carga, coherente con los perfiles y roles de cada integrante. El primer nombre indica el responsable principal; los Colaboradores participan en contenido parcial y en revisión cruzada.
Tabla 1. Distribución de capítulos, responsables y tipo de contribución.
Capítulo / Apartado
Responsable principal
Colaboradores
Tipo de contribución
Organización del trabajo en grupo
Juan Carlos (coord.)
Brian, Ancor
Redacción conjunta y validación
Cap. 1. Introducción
Juan Carlos
Brian, Ancor
Redacción principal, revisión cruzada
Cap. 2. Contexto y estado del arte
Juan Carlos
Brian, Ancor
Revisión bibliográfica y redacción
Cap. 3. Marco normativo y fuentes
Juan Carlos
Ancor
Análisis normativo y extracción de criterios
Cap. 4. Objetivos y metodología
Juan Carlos
Brian, Ancor
Formulación SMART y diseño metodológico
Cap. 5. Requisitos del sistema
Juan Carlos
Brian
Especificación funcional y no funcional
Cap. 6. Diseño del motor
Juan Carlos
Brian
Diseño analítico, variables, reglas, scoring
Cap. 7. Diseño de datos y dataset
Brian
Juan Carlos
Esquema de datos, dataset piloto
Cap. 8. Prototipo software
Brian (back), Ancor (front)
Juan Carlos
Implementación y documentación
Cap. 9. Evaluación
Juan Carlos
Brian, Ancor
Ejecución, análisis e interpretación
Cap. 10. Conclusiones
Juan Carlos
Brian, Ancor
Síntesis y líneas futuras
Anexos A–F
Juan Carlos (A,B,C,E), Brian (D,F)
Ancor
Especificación técnica de soporte
Anexo G. Capturas prototipo
Ancor
Brian
Capturas de interfaz y flujos
Anexo H. Evidencia uso de IA
Juan Carlos
Brian, Ancor
Documentación de transparencia

Fuente: elaboración propia.
El director del TFM podrá reorganizar y redistribuir tareas si lo considera oportuno, conforme a lo previsto en el procedimiento de TFE grupal de la UNIR.
0.4. Metodología de coordinación del grupo
0.4.1. Reuniones de seguimiento
El equipo ha mantenido reuniones periódicas de seguimiento con cadencia semanal durante las fases de desarrollo activo del trabajo, utilizando Discord como canal principal de comunicación diaria y Microsoft Teams para las reuniones formales de seguimiento y las sesiones con el director del TFM. Estas reuniones han servido para revisar el avance de cada eje funcional, identificar bloqueos, sincronizar decisiones de diseño y preparar las entregas parciales.
Además de la cadencia semanal, se han celebrado reuniones de coordinación específicas antes de cada hito de entrega —borrador inicial, borrador intermedio y predepósito— para verificar la coherencia y completitud del documento en cada fase.
0.4.2. Gestión documental y control de versiones
La gestión documental del proyecto se ha apoyado en tres mecanismos complementarios: un repositorio compartido de código fuente con control de versiones mediante Git, alojado en una plataforma en línea, que permite la trazabilidad de las contribuciones individuales al prototipo software; un documento maestro interno del proyecto que recoge las decisiones metodológicas cerradas y que ha funcionado como referencia de autoridad para todo el equipo a lo largo del desarrollo; y almacenamiento compartido en la nube mediante OneDrive y Google Drive para la gestión de la memoria, las entregas parciales, la documentación normativa y el material de apoyo.
Esta combinación de herramientas ha permitido mantener la trazabilidad tanto del código como de la documentación, facilitando que cada integrante pudiera trabajar de forma autónoma dentro de su eje funcional sin perder la visión de conjunto.

