Anexo A. Taxonomía completa de incidentes
A.1. Finalidad del anexo
Este anexo despliega con mayor detalle la taxonomía operativa de incidentes del sistema, cuya presentación resumida se realiza en el apartado 3.4 del Capítulo 3. La taxonomía no es un catálogo administrativo con fines clasificatorios abstractos, sino un mecanismo funcional que permite al motor de priorización decidir qué variables contextuales deben activarse, qué comprobaciones conviene realizar y qué reglas de priorización son potencialmente aplicables a cada incidente.
El anexo cumple tres finalidades. En primer lugar, documenta la estructura completa de la taxonomía en dos niveles, asignando códigos, descripciones operativas y justificaciones a cada categoría. En segundo lugar, establece la relación explícita entre cada tipo de incidente y la lógica del motor: qué variables contextuales se consultan, qué reglas duras pueden activarse y qué planes o contextos normativos son relevantes. En tercer lugar, proporciona una referencia de implementación para la variable V04 (tipo de incidente) del motor, documentada en el Anexo B.
El contenido de este anexo es coherente con los apartados 3.4.1 a 3.4.3 del Capítulo 3, con la variable V04 del Capítulo 6, con la distribución tipológica del dataset piloto (Tabla 7.3 del Capítulo 7) y con los Anexos B y E. No introduce familias nuevas, no modifica la lógica del motor y no amplía el alcance del sistema.
A.2. Criterios de construcción de la taxonomía
La taxonomía operativa del sistema se ha construido aplicando cuatro criterios complementarios, coherentes con los establecidos en el apartado 3.4 del Capítulo 3:
Alineación con el catálogo de riesgos oficial. Las familias del Nivel 1 se corresponden con las categorías de riesgo reconocidas en la Norma Básica de Protección Civil (RD 524/2023) y con los planes especiales de Aragón (PROCINFO, PROCINAR, PROCIFEMAR, PROCIMER). El Nivel 2 se inspira en la tipología operativa habitual de los centros 112, utilizando como referencia estructural el dataset abierto del CAT112 y las memorias del 112 Aragón.
Funcionalidad para el motor. Cada categoría debe activar un perfil de contexto diferenciado. Un incendio forestal y una emergencia sanitaria no comparten las mismas variables contextuales ni las mismas reglas potenciales. La taxonomía garantiza que el motor consulte el contexto pertinente y no aplique indiscriminadamente todas las comprobaciones.
Granularidad operativa viable. La taxonomía no pretende reproducir la totalidad de la tipificación interna del 112 Aragón (a la que no se tiene acceso detallado), sino establecer un nivel de granularidad suficiente para que el motor discrimine entre tipos de incidente operativamente distintos dentro del alcance del TFM.
Compatibilidad con el dataset piloto. Las categorías de la taxonomía deben poder instanciarse en casos simulados plausibles conforme a la distribución tipológica orientativa de la Tabla 7.3 del Capítulo 7.

A.3. Taxonomía completa: Nivel 1 — Emergencias de protección civil
El Nivel 1 agrupa incidentes con potencial de activar lógica de protección civil o de requerir un tratamiento reforzado de coordinación y contexto. Se organiza en cuatro familias, coherentes con el apartado 3.4.1 del Capítulo 3.
Tabla A.1. Taxonomía Nivel 1: Emergencias de protección civil
Código
Familia
Descripción operativa
Justificación normativa
N1.1
Riesgos naturales
Incidentes de origen natural con potencial de afectación colectiva: inundaciones, fenómenos meteorológicos adversos, incendios forestales y eventos sísmicos o geológicos. Especialmente sensibles al enriquecimiento contextual mediante AEMET, SNCZI y cartografía territorial.
Catálogo de riesgos de la Norma Básica (RD 524/2023). Planes especiales: PROCINAR, PROCIFEMAR, PROCINFO. Directrices básicas de inundaciones e incendios forestales.
N1.2
Riesgos tecnológicos e industriales
Accidentes con mercancías peligrosas, incidentes en instalaciones industriales sujetas a normativa Seveso y situaciones vinculadas a infraestructuras energéticas o químicas. La localización, el tipo de sustancia y el entorno sensible alteran fuertemente la prioridad.
RD 840/2015 (Seveso III). Planes especiales: PROCIMER, PROCIGO. PLATEAR: procedimientos para emergencias industriales.
N1.3
Grandes accidentes y eventos antrópicos de alta complejidad
Accidentes de transporte con múltiples afectados, derrumbes, incendios de gran entidad en entornos urbanos o incidentes con afectación crítica de infraestructuras o servicios esenciales. Alta exigencia de coordinación y potencial de escalado.
PLATEAR: criterios de activación por magnitud y coordinación. Ley 4/2024: emergencias de protección civil por afectación colectiva.
N1.4
Escenarios multirriesgo
Situaciones en las que concurren simultáneamente varias amenazas o en las que la complejidad del entorno convierte el incidente en un problema de coordinación superior. Categoría especialmente útil para la lógica de explicación del sistema.
PLEGEM: emergencias multirriesgo. PLATEAR: coordinación en escenarios complejos. Ley 17/2015: emergencias de interés nacional.

Fuente: elaboración propia. Coherente con el apartado 3.4.1 del Capítulo 3.
A.3.1. Subcategorías del Nivel 1
Cada familia del Nivel 1 se descompone en subcategorías operativas que determinan con mayor precisión qué contexto activa el motor y qué reglas duras pueden aplicarse.
Tabla A.2. Subcategorías operativas del Nivel 1
Código
Subcategoría
Descripción operativa
Variables contextuales
Reglas duras potenciales
Plan/contexto
N1.1.1
Inundación fluvial o pluvial
Crecida de ríos, desbordamientos, lluvias torrenciales con acumulación de agua en zonas habitadas o infraestructuras.
V08, V09, V10
RD3, RD7
PROCINAR
N1.1.2
Fenómeno meteorológico adverso
Viento extremo, nieve, heladas, temperaturas extremas, tormentas severas, aludes.
V08, V09
RD3
PROCIFEMAR
N1.1.3
Incendio forestal
Fuego en masa forestal. Incluye incendio forestal puro y en interfaz urbano-forestal (IUF).
V08, V09
RD8 (si IUF)
PROCINFO
N1.1.4
Evento sísmico o geológico
Terremoto, deslizamiento de tierras, hundimiento de terreno.
(contexto específico)
(no aplica regla específica)
Plan Sísmico Aragón
N1.2.1
Accidente con mercancías peligrosas
Incidentes durante transporte por carretera o ferrocarril de sustancias catalogadas como peligrosas.
V11
RD4 (si Seveso)
PROCIMER
N1.2.2
Incidente industrial Seveso
Accidente en instalación sujeta a RD 840/2015 con potencial de emisión de sustancias peligrosas.
V11
RD4
RD 840/2015; PLATEAR
N1.2.3
Incidente en infraestructura energética
Fugas en gasoductos, oleoductos o instalaciones eléctricas de alta tensión con riesgo de afectación.
V11
(potencial RD4)
PROCIGO
N1.3.1
Accidente de transporte con múltiples víctimas
Accidentes de tráfico, ferroviarios o aéreos con múltiples heridos o fallecidos.
(contexto general)
RD2, RD5
PLATEAR
N1.3.2
Derrumbe o colapso estructural
Hundimiento parcial o total de edificio, puente u otra estructura con posible atrapamiento de personas.
V15
RD1 (si atrapados)
PLATEAR
N1.3.3
Incendio urbano de gran entidad
Incendio en edificio o zona urbana con afectación extensa, propagación significativa o riesgo para múltiples personas.
(contexto general)
RD1 (si atrapados), RD2
PLATEAR
N1.4.1
Escenario multirriesgo concurrente
Combinación simultánea de amenazas (p. ej., inundación + vertido industrial; terremoto + incendio).
V08-V11
Múltiples potenciales
PLATEAR; planes específicos según riesgos

Fuente: elaboración propia. Coherente con los planes especiales de Aragón (apartado 3.2.5) y con las reglas duras del Anexo E.

A.4. Taxonomía completa: Nivel 2 — Emergencias operativas ordinarias (112)
El Nivel 2 agrupa las emergencias que forman parte de la gestión ordinaria del 112 y que, aun sin activar necesariamente un plan de protección civil, deben ser priorizadas de forma relativa porque compiten por atención operativa. Su inclusión es necesaria porque el sistema no puede reservar la priorización solo para grandes emergencias; su valor añadido reside precisamente en la gestión simultánea de incidentes heterogéneos.
Tabla A.3. Taxonomía Nivel 2: Emergencias operativas ordinarias
Código
Familia
Descripción operativa
Justificación normativa
N2.1
Emergencias sanitarias
Urgencias médicas que no constituyen por sí mismas una emergencia de protección civil: paradas cardiacas, traumatismos, intoxicaciones, urgencias psiquiátricas y otros eventos sanitarios que requieren movilización del 112.
Ley 4/2024: funciones del servicio 112 (identificación, evaluación, movilización). Memorias del 112 Aragón: categoría sanitaria como familia de mayor volumen.
N2.2
Tráfico y transporte
Accidentes de tráfico leves o moderados, incidencias viales (vehículos averiados, obstáculos, animales en calzada) y otros eventos de movilidad sin dimensión extraordinaria.
PLATEAR: infraestructuras viarias relevantes. Memorias 112 Aragón: tráfico como segunda categoría por volumen.
N2.3
Incendios urbanos y de vehículos
Incendios en viviendas, locales, contenedores, vehículos y otros escenarios urbanos que no presentan de entrada una dimensión extraordinaria.
Ley 1/2013 de SPEIS de Aragón: tipología de intervenciones de bomberos.
N2.4
Rescates y salvamentos
Rescates en montaña, medio acuático, espacios confinados, ascensores u otros entornos de difícil acceso. Incluye búsqueda de personas desaparecidas.
PLATEAR: procedimientos de búsqueda y rescate. Ley 4/2024 art. 6.2: protección de colectivos vulnerables.
N2.5
Seguridad y personas
Incidentes con componente de seguridad que generan una derivada operativa de emergencia: violencia con riesgo para terceros, personas en crisis, amenazas graves.
Ley 4/2024: coordinación con fuerzas de seguridad. Funciones del 112 como centro integrado.
N2.6
Asistencia técnica y servicios esenciales
Cortes de suministro, averías en infraestructuras básicas, incidencias con impacto en la operativa cotidiana que requieren coordinación.
Ley 4/2024: protección de servicios esenciales. PLATEAR: infraestructuras relevantes.

Fuente: elaboración propia. Coherente con el apartado 3.4.2 del Capítulo 3.
A.4.1. Subcategorías del Nivel 2
Tabla A.4. Subcategorías operativas del Nivel 2
Código
Subcategoría
Descripción operativa
Variables contextuales
Reglas duras potenciales
Servicios / contexto
N2.1.1
Emergencia vital
Parada cardiaca, hemorragia masiva, reacción anafiláctica, ahogamiento, electrocución u otro evento con riesgo vital inmediato.
(general)
RD1
Servicios sanitarios
N2.1.2
Urgencia sanitaria no vital
Traumatismo moderado, intoxicación, crisis psiquiátrica, urgencia pediátrica sin riesgo vital.
(general)
(no aplica)
Servicios sanitarios
N2.1.3
Accidente con múltiples víctimas (AMV)
Evento sanitario con múltiples personas afectadas simultáneamente.
(general)
RD2, RD5
PLATEAR; servicios sanitarios
N2.2.1
Accidente de tráfico con víctimas
Colisión, salida de vía u otro accidente vial con personas heridas.
V15
RD1 (si atrapados), RD2
Servicios de emergencia
N2.2.2
Incidencia vial sin víctimas
Vehículo averiado, obstáculo en calzada, animal en vía, corte de tráfico.
V15
(no aplica)
Tráfico; asistencia
N2.3.1
Incendio en vivienda o local
Fuego en interior de edificio residencial, comercial o de servicios.
(general)
RD1 (si atrapados)
Bomberos / SPEIS
N2.3.2
Incendio de vehículo o contenedor
Fuego en vehículo, contenedor u otro elemento aislado sin propagación a estructura.
(general)
(no aplica)
Bomberos / SPEIS
N2.4.1
Rescate en montaña
Persona accidentada, perdida o aislada en entorno de montaña.
V15
RD6 (si vulnerable)
GREIM; Bomberos
N2.4.2
Rescate acuático
Persona en peligro en río, embalse, piscina u otro medio acuático.
(general)
RD1 (si riesgo vital)
Servicios rescate
N2.4.3
Búsqueda de persona desaparecida
Búsqueda activa de persona cuyo paradero se desconoce.
(general)
RD6 (si menor/vulnerable)
FCSE; Protección Civil
N2.4.4
Rescate en espacio confinado o ascensor
Persona atrapada en ascensor, sótano u otro espacio de difícil acceso.
V15
RD1 (si riesgo vital)
Bomberos / SPEIS
N2.5.1
Incidente de seguridad con riesgo
Violencia activa, amenaza grave, persona en crisis con riesgo para sí misma o terceros.
(general)
RD1 (si riesgo vital)
FCSE; 112
N2.5.2
Incidente de convivencia o seguridad menor
Conflicto vecinal, molestias, incidencias sin riesgo operativo significativo.
(general)
(no aplica)
FCSE; 112
N2.6.1
Corte de suministro esencial
Interrupción de electricidad, agua o gas con afectación a población.
(general)
(no aplica)
Compañías; Protección Civil
N2.6.2
Avería en infraestructura pública
Semáforo, alumbrado, mobiliario urbano, incidencia en red viaria menor.
(general)
(no aplica)
Servicios municipales
N2.6.3
Consulta informativa o verificación
Llamada sin incidente activo: consulta, verificación de estado, solicitud de información.
(general)
(no aplica)
112

Fuente: elaboración propia. Coherente con el apartado 3.4.2 del Capítulo 3 y con la distribución tipológica del dataset piloto (Tabla 7.3 del Capítulo 7).

A.5. Relación entre taxonomía y activación del motor
La relación entre la taxonomía y el motor de priorización es estructural. Conforme al apartado 3.4.3 del Capítulo 3, el tipo de incidente (V04) cumple tres funciones simultáneas dentro del motor:
Determina qué variables contextuales se activan. No todos los incidentes requieren consulta meteorológica, análisis de cartografía de inundación o comprobación de entorno industrial. La taxonomía permite decidir qué contexto es pertinente y evita ruido innecesario.
Condiciona la activación de reglas duras. Existen reglas transversales (como RD1, riesgo vital) y reglas dependientes del tipo de incidente (RD3 exige coherencia meteorológica; RD4 exige entorno Seveso; RD7 requiere inundación; RD8 requiere incendio en IUF).
Mejora la explicabilidad. Un sistema que justifica la prioridad con factores coherentes con la naturaleza del incidente resulta más comprensible para el operador. La explicación de una inundación no puede ser idéntica a la de un accidente múltiple.
Tabla A.5. Matriz de activación: tipo de incidente → contexto, reglas y planes
Tipo de incidente
Variables contextuales activadas
Reglas duras potenciales
Plan / contexto relevante
Observaciones
N1.1.1 Inundación
V08, V09, V10, V15
RD3 (si AEMET rojo), RD7 (si personas aisladas)
PROCINAR
Contexto hidrológico y meteorológico crítico. Cruce obligatorio con SNCZI y AEMET.
N1.1.2 FMA
V08, V09
RD3 (si AEMET rojo)
PROCIFEMAR
Activación condicionada a coherencia entre fenómeno y tipo de incidente.
N1.1.3 Incendio forestal
V08, V09, V15
RD8 (si IUF + AEMET ≥ naranja)
PROCINFO
Distinción clave entre incendio forestal puro e IUF para activación de RD8.
N1.1.4 Sísmico / geológico
V15
(transversales)
Plan Sísmico
Contexto específico: magnitud, profundidad, proximidad a población.
N1.2.1 MMPP
V11, V15
RD4 (si afectación Seveso directa)
PROCIMER
Consulta obligatoria a registro Seveso. Tipo de sustancia condiciona gravedad.
N1.2.2 Industrial Seveso
V11
RD4
RD 840/2015; PLATEAR
Escenario de máxima criticidad si afectación directa confirmada.
N1.2.3 Infraestructura energética
V11
(potencial RD4)
PROCIGO
Gasoductos, oleoductos, alta tensión.
N1.3.1 AMV transporte
V15
RD2 (≥3), RD5 (>10)
PLATEAR
Número de víctimas como factor determinante. Coordinación multiagencia.
N1.3.2 Derrumbe
V15
RD1 (si atrapados)
PLATEAR
Atrapamiento = riesgo vital. Accesibilidad crítica.
N1.3.3 Incendio urbano gran entidad
V15
RD1 (si atrapados), RD2
PLATEAR
Propagación y población expuesta como factores clave.
N1.4.1 Multirriesgo
V08–V11, V15
Múltiples potenciales
Planes según riesgos
Activación de múltiples perfiles de contexto simultáneamente.
N2.1.1 Emergencia vital
(general)
RD1
Sanitario
Riesgo vital directo. Prioridad crítica independiente del contexto.
N2.1.3 AMV sanitario
(general)
RD2, RD5
Sanitario; PLATEAR
Magnitud de víctimas como discriminador principal.
N2.2.1 Tráfico con víctimas
V15
RD1 (si atrapados), RD2
Emergencia
Atrapamiento y número de víctimas como factores clave.
N2.3.1 Incendio vivienda
(general)
RD1 (si atrapados)
Bomberos
Presencia de personas en interior como factor crítico.
N2.4.1 Rescate montaña
V15
RD6 (si vulnerable)
GREIM; Bomberos
Accesibilidad como factor determinante de urgencia operativa.
N2.4.3 Búsqueda persona
(general)
RD6 (si menor/vulnerable)
FCSE; PC
Vulnerabilidad del sujeto como criterio diferenciador.
N2.5.1 Seguridad con riesgo
(general)
RD1 (si riesgo vital)
FCSE
Riesgo vital determina prioridad. Coordinación con fuerzas de seguridad.
N2.6.3 Consulta informativa
(ninguna)
(ninguna)
112
Sin contexto activado. Prioridad P4 típica.

Fuente: elaboración propia. Coherente con el apartado 3.4.3 del Capítulo 3, la Tabla 6.3 (reglas duras) y el Anexo E.
Esta tabla no es exhaustiva —no incluye todas las subcategorías—, sino representativa: documenta los tipos de incidente con mayor impacto sobre la lógica del motor. Las subcategorías no representadas (N2.1.2, N2.2.2, N2.3.2, N2.4.2, N2.4.4, N2.5.2, N2.6.1, N2.6.2) siguen la lógica general del motor sin activación de contexto específico ni reglas duras propias.

A.6. Observaciones metodológicas
A.6.1. La taxonomía no es un catálogo jurídico
La taxonomía operativa del sistema es una herramienta funcional diseñada para el prototipo. No constituye una clasificación jurídica oficial, no sustituye la tipificación interna del 112 Aragón y no pretende agotar toda la casuística real del dominio de emergencias. Su valor reside en su capacidad para activar la lógica correcta del motor, no en su exhaustividad clasificatoria.
A.6.2. Frontera entre Nivel 1 y Nivel 2
La frontera entre ambos niveles no es rígida. Un incidente clasificado inicialmente como Nivel 2 puede escalar a Nivel 1 si su evolución lo justifica (por ejemplo, un incendio urbano menor que se propaga a un edificio residencial con múltiples pisos). El motor gestiona esta transición a través de la variable V12 (tendencia del incidente) y de la actualización de las variables de entrada, no mediante un cambio automático de categoría taxonómica. En el contexto del TFM, el dataset piloto trabaja con instantáneas de decisión, no con secuencias evolutivas completas.
A.6.3. Coherencia con el dataset piloto
La distribución tipológica orientativa del dataset piloto (Tabla 7.3 del Capítulo 7) es coherente con esta taxonomía: riesgos naturales (25–30 %), riesgos tecnológicos (8–12 %), riesgos antrópicos y accidentales (25–30 %), emergencias sanitarias (10–15 %), emergencias sociales y de seguridad (5–8 %) y emergencias operativas ordinarias (15–20 %). Cada subcategoría de la taxonomía puede instanciarse en al menos un caso plausible del dataset.
A.6.4. Extensibilidad
La taxonomía está diseñada para ser extensible. En líneas de trabajo futuro, podría ampliarse con subcategorías adicionales, refinarse con la tipificación interna del 112 Aragón (si se obtiene acceso) o adaptarse a otros territorios. La arquitectura modular del motor permite incorporar nuevas subcategorías sin alterar la lógica del baseline, siempre que cada nueva categoría defina su perfil de activación de contexto y su relación con las reglas existentes.


