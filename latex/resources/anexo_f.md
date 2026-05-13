Anexo F. Esquema de datos del sistema
F.1. Finalidad del anexo
Este anexo documenta la especificación estructural completa del esquema de datos del sistema de priorización. El apartado 7.2 del Capítulo 7 presenta el esquema de forma resumida (Tabla 7.1); este anexo lo expande con el nivel de detalle necesario para la implementación del prototipo, la trazabilidad metodológica y la defensa ante tribunal.
El anexo especifica los cinco bloques funcionales del esquema, define un diccionario de datos con tipo, obligatoriedad, origen, descripción y ejemplo para cada campo, y establece las reglas de integridad y consistencia que el sistema debe respetar. El contenido es coherente con las variables del Capítulo 6, con la Tabla 7.1 del Capítulo 7, con el Anexo B (matriz de variables) y con la plantilla del Anexo D.
F.2. Principios del esquema de datos
Separación funcional. El esquema distingue cinco bloques con funciones diferenciadas: datos observados del incidente, evidencias asociadas, contexto oficial, salidas calculadas y decisión humana. Esta separación impide que las salidas del motor contaminen las entradas y garantiza la reproducibilidad del cálculo.
Incidente consolidado como unidad de análisis. La unidad de análisis es el incidente operativo consolidado, no la llamada individual. Un mismo suceso puede generar múltiples comunicaciones; el sistema trabaja sobre el incidente resultante, no sobre llamadas aisladas.
Distinción explícita entre dato informado y dato ausente. Cada variable de entrada admite tres estados: valor informado, valor ausente (sin información) y no aplica. Esta distinción evita confundir la ausencia de dato con un valor negativo, lo cual es crítico para el cálculo de la confianza (Anexo E).
Trazabilidad completa. El esquema registra no solo la recomendación del motor, sino también la decisión final del operador y la justificación del cambio. Esto permite la evaluación posterior (Capítulo 9) y cumple el requisito RF9 (trazabilidad) del Capítulo 5.
Diseño estructural, no implementación final. Este esquema define la estructura lógica de los datos. La implementación concreta (modelo de base de datos, ORM, formato de persistencia) se documenta en el Capítulo 8. El esquema es independiente de la tecnología de almacenamiento.

F.3. Esquema lógico por bloques
El esquema se organiza en cinco bloques funcionales, coherentes con los apartados 7.2.1 a 7.2.5 del Capítulo 7. A continuación se describe la función de cada bloque y se anticipa su contenido, que se detalla en el diccionario de datos (F.4).
Tabla F.1. Bloques funcionales del esquema de datos
N.º
Bloque
Función
Referencia en Cap. 7
1
Estructura del incidente
Datos observados: identificación, localización, descripción, taxonomía y las 15 variables de entrada del motor.
Apartado 7.2.1
2
Evidencias y señales
Señales asociadas al incidente: llamadas, partes, alertas, con trazabilidad de fuente y momento.
Apartado 7.2.2
3
Contexto territorial y meteorológico
Datos de fuentes oficiales externas: AEMET, SNCZI, INE, ICEARAGON, registro Seveso.
Apartado 7.2.3
4
Variables calculadas y salidas
Resultados del motor: variables derivadas (D01–D04), prioridad, scoring, confianza, reglas activadas, explicación.
Apartado 7.2.4
5
Decisión humana y trazabilidad
Interacción del operador: prioridad final, acción, justificación y marca temporal.
Apartado 7.2.5

Fuente: elaboración propia. Coherente con la Tabla 7.1 del Capítulo 7.
La relación entre bloques es unidireccional: el bloque 1 alimenta al motor junto con el bloque 3; el bloque 2 aporta contexto de evidencias; el bloque 4 recoge las salidas del motor; y el bloque 5 registra la respuesta humana. Las variables del bloque 3 que coinciden con variables de entrada del motor (V08, V09, V10, V11, V15) reflejan su doble naturaleza: son datos de contexto que, una vez incorporados, se utilizan como entradas operativas.

F.4. Diccionario de datos
A continuación se presenta el diccionario de datos completo, organizado por bloques. Cada campo incluye nombre, tipo de dato, obligatoriedad, origen, descripción y ejemplo.
F.4.1. Bloque 1: Estructura del incidente
Campo
Tipo
Oblig.
Origen
Descripción
Ejemplo
id_incidente
Texto (UUID)
Sí
Generado
Identificador único del incidente consolidado.
INC-2024-00142
fecha_hora_recepcion
Datetime
Sí
Sistema
Marca temporal de la primera comunicación recibida.
2024-10-15 16:30
latitud
Float
Sí*
Operador/GPS
Coordenada geográfica. *Obligatoria si está disponible.
41.8102
longitud
Float
Sí*
Operador/GPS
Coordenada geográfica.
−1.1375
municipio
Texto
Sí
Operador/cart.
Municipio de Aragón.
Ejea de los Caballeros
comarca
Texto
Sí
Derivado/cart.
Comarca aragonesa.
Cinco Villas
provincia
Texto
Sí
Derivado
Provincia.
Zaragoza
descripcion_textual
Texto libre
Sí
Informante
Descripción inicial del suceso.
Crecida del río Arba con agua en calles...
tipo_incidente_n1
Categórica
Sí
Operador/NLP
Código Nivel 1 de la taxonomía (Anexo A).
N1.1
tipo_incidente_n2
Categórica
Recom.
Operador/NLP
Código Nivel 2 de la taxonomía.
N1.1.1
fuente_primer_aviso
Categórica
Sí
Sistema
Ciudadano / servicio / organismo / automático.
Ciudadano
V01_riesgo_vital
Binaria / Ausente
Sí
Comunicación
Sí / No / Ausente.
Sí
V02_victimas
Ordinal / Ausente
Sí
Comunicación
0 / 1–2 / 3–10 / >10 / Ausente.
0
V03_tipo_dano
Categ. / Ausente
Sí
Comunicación
Personas / Bienes / Medioamb. / Sin daño / Ausente.
Personas
V04_tipo_incidente
Categórica
Sí
Estructuración
Código completo de taxonomía.
N1.1.1
V05_pob_vulnerable
Binaria / Ausente
Sí
Comunicación/ctx.
Sí / No / Ausente.
No
V06_personas_riesgo
Ordinal / Ausente
Sí
Comunicación/ctx.
0 / 1–10 / 11–100 / >100 / Ausente.
>100
V07_emplaz_critico
Categ. / Ausente
Sí
Comunicación/cart.
Sanitario/Educativo/Residencia/Infraestr./Otro/No/Ausente.
No
V08_aemet
Ordinal / Ausente
Sí
AEMET
Verde / Amarillo / Naranja / Rojo / Ausente.
Naranja
V09_fenomeno_meteo
Categ. / Ausente
Sí
AEMET
Viento/Lluvia/Nieve/Temp./Tormenta/Ninguno/Ausente.
Lluvia
V10_inundacion
Binaria / Ausente
Sí
SNCZI
Sí / No / Ausente.
Sí
V11_seveso
Binaria / Ausente
Sí
Registro Seveso
Sí / No / Ausente.
No
V12_tendencia
Ordinal / Ausente
Sí
Comunicación
Mejoría / Estable / Agravamiento / Desconocida / Ausente.
Agravamiento
V13_fiabilidad
Ordinal / Ausente
Sí
Operador
Alta / Media / Baja / Ausente.
Alta
V14_avisos
Num. agrupada / Aus.
Sí
Sistema
1 / 2–3 / >3 / Ausente.
>3
V15_accesibilidad
Ordinal / Ausente
Sí
Comunicación/cart.
Fácil / Moderada / Difícil / Muy difícil / Ausente.
Difícil

Los campos V01–V15 corresponden a las 15 variables de entrada del motor (Cap. 6, Anexo B). El estado «Ausente» activa los valores por defecto del Anexo B.

F.4.2. Bloque 2: Evidencias y señales asociadas
Campo
Tipo
Oblig.
Origen
Descripción
Ejemplo
id_evidencia
Texto
Sí
Generado
Identificador único de la señal.
EV-001
id_incidente_ref
Texto (FK)
Sí
Referencia
Incidente al que se asocia la señal.
INC-2024-00142
fuente_senal
Categórica
Sí
Sistema
Origen: ciudadano / servicio / AEMET / SNCZI / otro.
Ciudadano
tipo_senal
Categórica
Sí
Sistema
Llamada / alerta automática / parte de servicio / aviso institucional.
Llamada
contenido_relevante
Texto
Recom.
Extracción
Resumen del contenido útil de la señal.
Agua a nivel rodilla en calle Mayor
marca_temporal
Datetime
Sí
Sistema
Momento de recepción de la señal.
2024-10-15 16:35
relacion_info_previa
Categórica
Recom.
Motor/operador
Confirma / contradice / complementa la información previa.
Confirma

En el dataset piloto, este bloque se simplifica. Se mantiene en el esquema porque forma parte de la lógica completa del sistema (apartado 7.2.2).
F.4.3. Bloque 3: Contexto territorial y meteorológico
Campo
Tipo
Oblig.
Origen
Descripción
Ejemplo
nivel_aviso_aemet
Ordinal
Recom.
AEMET OpenData
Verde / Amarillo / Naranja / Rojo. Alimenta V08.
Naranja
fenomeno_meteo_activo
Categórica
Recom.
AEMET OpenData
Tipo de fenómeno. Alimenta V09.
Lluvia
peligrosidad_inundacion
Binaria
Recom.
SNCZI/MITECO
Zona inundable cartografiada. Alimenta V10.
Sí
proximidad_seveso
Binaria
Recom.
Registro Seveso
Instalación Seveso en radio de influencia. Alimenta V11.
No
poblacion_municipio
Numérica
Opcional
INE
Población total del municipio. Apoyo a V06.
16.870
pct_mayor_65
Float
Opcional
INE
Proporción de población >65 años. Apoyo a V05.
22,3 %
accesibilidad_punto
Ordinal
Recom.
Cart. oficial/operador
Fácil / Moderada / Difícil / Muy difícil. Alimenta V15.
Difícil

Las variables V08, V09, V10, V11 y V15 se alimentan desde este bloque. Su aparición en bloques 1 y 3 no es duplicación (apartado 7.2.3, Cap. 7).
F.4.4. Bloque 4: Variables calculadas y salidas del motor
Campo
Tipo
Oblig.
Origen
Descripción
Ejemplo
D01_coord_multiagencia
Binaria
Sí
Motor
Necesidad estimada de coordinación multiagencia (Cap. 6, 6.4.1).
Sí
D02_necesidad_pma
Binaria
Sí
Motor
Necesidad estimada de PMA (Cap. 6, 6.4.2).
Sí
D03_sit_operativa
Ordinal
Sí
Motor
Situación operativa sugerida: 0/1/2/3. Orientativa, no vinculante.
1
D04_plan_activable
Categórica
Sí
Motor
Plan activable recomendado. Orientativo.
PROCINAR
prioridad_recomendada
Ordinal
Sí
Motor
P1 / P2 / P3 / P4.
P1
puntuacion_scoring
Float [0–100]
Sí
Motor
Puntuación del scoring ponderado.
82,5
nivel_confianza
Float [0–1]
Sí
Motor
Solidez de la recomendación (0=mínima, 1=máxima).
0,85
reglas_duras_activadas
Lista texto
Sí
Motor
Reglas duras activadas (lista vacía si ninguna).
[RD1, RD7]
explicacion_textual
Texto
Sí
Motor
Justificación automática de la recomendación.
Riesgo vital: personas aisladas...
marca_temporal_calculo
Datetime
Sí
Sistema
Momento en que el motor produjo la recomendación.
2024-10-15 16:31:05

D01–D04 son variables derivadas, no inputs. El campo explicacion_textual cumple el requisito RF7 (Cap. 5).

F.4.5. Bloque 5: Decisión humana y trazabilidad
Campo
Tipo
Oblig.
Origen
Descripción
Ejemplo
prioridad_final_operador
Ordinal
Sí
Operador
P1 / P2 / P3 / P4. Prioridad definitiva tras validación humana.
P1
marca_temporal_validacion
Datetime
Sí
Sistema
Momento de la validación por el operador.
2024-10-15 16:32:10
accion_operador
Categórica
Sí
Operador
Acepta / modifica / rechaza la recomendación.
Acepta
justificacion_cambio
Texto
Cond.
Operador
Obligatorio si accion_operador = modifica o rechaza. Motivo del cambio.
(vacío si acepta)
id_operador
Texto
Sí
Sistema
Identificador del operador que valida.
OP-003

Este bloque cumple los requisitos RF8 (validación humana) y RF9 (trazabilidad) del Capítulo 5.

F.5. Reglas de integridad y consistencia
El esquema de datos se rige por las siguientes reglas de integridad, que deben respetarse tanto en el dataset piloto como en el prototipo:
RI-1. Unicidad del incidente. Cada id_incidente es único. No pueden existir dos incidentes con el mismo identificador.
RI-2. Integridad referencial. Toda evidencia (bloque 2) debe referenciar un id_incidente existente en el bloque 1. No puede existir una evidencia huérfana.
RI-3. Obligatoriedad de variables críticas. Los campos V01, V02, V04 y fecha_hora_recepcion son obligatorios en todo caso. Su ausencia impide el cálculo mínimo del motor. Los demás campos de variables admiten estado «Ausente».
RI-4. No circularidad. Los campos del bloque 4 (salidas del motor) no pueden utilizarse como entradas para el cálculo del bloque 4. Las variables D01–D04 son derivadas, no inputs.
RI-5. Precedencia temporal. marca_temporal_calculo debe ser posterior a fecha_hora_recepcion. marca_temporal_validacion debe ser posterior o igual a marca_temporal_calculo.
RI-6. Consistencia de acción y justificación. Si accion_operador = «modifica» o «rechaza», el campo justificacion_cambio no puede estar vacío. Si accion_operador = «acepta», puede estar vacío.
RI-7. Coherencia de prioridad con reglas duras. Si alguna regla dura fija está activada (RD1, RD7), prioridad_recomendada debe ser P1. Si una regla mínima está activada, prioridad_recomendada no puede ser inferior al mínimo de la regla. Estas reglas se aplican al motor, no al operador (que puede decidir libremente).
RI-8. Valores válidos. Cada campo categórico u ordinal solo admite los valores definidos en su especificación. Valores fuera de rango se rechazan o se marcan como «Ausente».

F.6. Observaciones metodológicas
F.6.1. Esquema lógico vs. implementación física
Este anexo documenta el esquema lógico de datos. La implementación física (modelo de base de datos, ORM, formato de archivos) se detalla en el Capítulo 8 (apartado 8.5.1). El esquema lógico es independiente de la tecnología: podría implementarse en una base de datos relacional, en documentos JSON o en archivos CSV, sin alterar la estructura funcional.
F.6.2. Simplificación en el dataset piloto
En el dataset piloto, el bloque 2 (evidencias) se simplifica: cada caso incluye una o pocas evidencias resumidas, no el historial completo de comunicaciones. Esta simplificación es coherente con el enfoque de instantáneas de decisión del apartado 7.3.2 y no afecta a la evaluación del baseline.
F.6.3. Doble naturaleza de variables contextuales
Las variables V08, V09, V10, V11 y V15 aparecen tanto en el bloque 1 (como entradas del motor) como en el bloque 3 (como datos de contexto oficial). Esto no implica duplicación: el bloque 3 registra el dato en su forma original de fuente; el bloque 1 lo incorpora como variable operativa del motor. Esta distinción facilita la trazabilidad del origen del dato.
F.6.4. Extensibilidad del esquema
El esquema admite extensión futura. Podrían añadirse campos adicionales en cualquier bloque (por ejemplo, coordenadas de evacuación, estado de recursos movilizados o feedback de servicios intervinientes) sin alterar la estructura de los bloques existentes. La modularidad es coherente con el requisito RNF3 (modularidad) del Capítulo 5.


