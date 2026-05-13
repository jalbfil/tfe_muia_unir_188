Anexo D. Plantilla de etiquetado y casos piloto
D.1. Finalidad del anexo
Este anexo materializa la guía de etiquetado (Anexo C) en dos instrumentos concretos: una plantilla maestra reutilizable para documentar cada caso del dataset piloto y un conjunto representativo de fichas de casos piloto que ilustran cómo se aplica la guía en la práctica.
La plantilla maestra define los campos que debe contener cada ficha de caso, garantizando la homogeneidad del dataset y la trazabilidad de cada etiqueta. Las fichas de casos piloto demuestran cómo se asigna la prioridad, cómo se justifica y cómo se documenta la confianza en escenarios claros y en escenarios de frontera.
El contenido de este anexo es coherente con el esquema de datos del apartado 7.2 del Capítulo 7, con los controles de plausibilidad del apartado 7.3.2, con la guía de etiquetado del Anexo C, con la matriz de variables del Anexo B y con las reglas duras del Anexo E. Los casos presentados son representativos del tipo de escenarios que componen el dataset piloto, pero no constituyen el dataset completo.

D.2. Plantilla maestra de etiquetado
Cada caso del dataset piloto se documenta mediante la siguiente plantilla. Los campos se organizan en cinco bloques, coherentes con el esquema de datos del apartado 7.2 del Capítulo 7.
Tabla D.1. Plantilla maestra de etiquetado de casos
BLOQUE 1: IDENTIFICACIÓN
ID del caso
Código único (formato: CASO-NNN)
Fecha/hora simulada
Fecha y hora ficticias del incidente (YYYY-MM-DD HH:MM)
Localización
Municipio, comarca y provincia de Aragón
Descripción textual
Relato breve del incidente tal como lo comunicaría el alertante
Tipo de incidente (V04)
Código de la taxonomía operativa (Anexo A)
Fuente del aviso
Ciudadano / testigo / agente / servicio / institucional
BLOQUE 2: VARIABLES DE ENTRADA
V01 Riesgo vital inmediato
Sí / No
V02 Víctimas confirmadas
0 / 1–2 / 3–10 / >10
V03 Tipo de daño principal
Personas / Bienes / Medioambiente / Sin daño
V05 Población vulnerable
Sí / No
V06 Personas en riesgo estimadas
0 / 1–10 / 11–100 / >100
V07 Emplazamiento crítico
Sanitario / Educativo / Residencia / Infraestructura / Otro / No
V08 Nivel aviso AEMET
Verde / Amarillo / Naranja / Rojo
V09 Fenómeno meteorológico
Viento / Lluvia / Nieve / Temperatura / Tormenta / Ninguno
V10 Peligrosidad inundación
Sí / No
V11 Instalación Seveso
Sí / No
V12 Tendencia incidente
Mejoría / Estable / Agravamiento / Desconocida
V13 Fiabilidad informador
Alta / Media / Baja
V14 Avisos simultáneos
1 / 2–3 / >3
V15 Accesibilidad al punto
Fácil / Moderada / Difícil / Muy difícil
BLOQUE 3: ETIQUETADO
Reglas duras activadas
Lista de reglas (RD1–RD8) o «ninguna»
Prioridad de referencia
P1 / P2 / P3 / P4
Nivel de confianza
Alto / Medio / Bajo
Justificación
1–3 frases: variables y criterios determinantes
BLOQUE 4: CONTROL DE PLAUSIBILIDAD
Coherencia geográfica
¿El tipo de incidente es compatible con la localización?
Coherencia temporal
¿La fecha/hora es coherente con la época del año?
Coherencia meteorológica
¿El aviso AEMET es coherente con el fenómeno y la fecha?
Coherencia interna
¿Los valores de variables son mutuamente compatibles?
Coherencia con etiquetado
¿La prioridad es coherente con la guía (Anexo C)?
BLOQUE 5: METADATOS
Etiquetador
Iniciales del miembro del equipo
Revisor
Iniciales del revisor cruzado
Discrepancia
Sí / No. Si sí, resolución y criterio aplicado

Fuente: elaboración propia. Coherente con el esquema de datos (Cap. 7, apartado 7.2) y la guía de etiquetado (Anexo C).

D.3. Casos piloto representativos
A continuación se presentan ocho fichas de casos piloto representativos. El conjunto incluye al menos un caso claro de cada nivel de prioridad (P1, P2, P3, P4) y cuatro casos de frontera o con características especiales. Todos los casos están localizados en Aragón y superan los cinco controles de plausibilidad definidos en el apartado 7.3.2 del Capítulo 7.
Caso CASO-001: Inundación con personas aisladas (P1)
ID
CASO-001
Fecha/hora
2024-10-15 16:30
Localización
Ejea de los Caballeros, Cinco Villas, Zaragoza
Descripción
Llamada de vecinos reportando crecida del río Arba con agua entrando en calles del casco urbano. Varias personas en tejados solicitan ayuda. Bomberos aún no han llegado.
V04
N1.1.1 — Inundación fluvial
Fuente
Múltiples ciudadanos (>3 llamadas)
V01
Sí (personas aisladas por agua = riesgo vital)
V02
0 (sin víctimas confirmadas aún)
V03
Personas (potencial)
V05
Desconocido
V06
>100 (zona urbana inundada)
V07
No
V08
Naranja (lluvia)
V09
Lluvia
V10
Sí (zona SNCZI)
V11
No
V12
Agravamiento
V13
Alta (múltiples alertantes independientes)
V14
>3
V15
Difícil (calles anegadas)
Reglas duras
RD1 (V01=Sí → P1 fija); RD7 (inundación + personas aisladas → P1 fija)
Prioridad
P1
Confianza
Alto
Justificación
Riesgo vital confirmado por personas aisladas en tejados. Reglas RD1 y RD7 activadas. Contexto hidrológico coherente (zona SNCZI, AEMET naranja por lluvia, tendencia de agravamiento). Múltiples fuentes confirman el evento. Sin ambigüedad.


Caso CASO-002: Incendio forestal IUF con AEMET naranja (P2)
ID
CASO-002
Fecha/hora
2024-07-22 14:15
Localización
Zuera, Comarca Central, Zaragoza
Descripción
Columna de humo visible desde urbanización próxima a masa forestal. Viento fuerte del noroeste. Sin víctimas reportadas. Aviso AEMET naranja por temperaturas extremas.
V04
N1.1.3 — Incendio forestal (IUF)
Fuente
Vecino de urbanización (testigo directo)
V01
No
V02
0
V03
Bienes (potencial personas si propaga)
V05
Sí (urbanización con familias)
V06
11–100
V07
No
V08
Naranja (temperatura)
V09
Temperatura
V10
No
V11
No
V12
Agravamiento (viento fuerte)
V13
Media (testigo directo)
V14
2–3
V15
Moderada
Reglas duras
RD8 (incendio IUF + AEMET ≥ naranja → P2 mínima)
Prioridad
P2
Confianza
Alto
Justificación
Regla RD8 activada: incendio en interfaz urbano-forestal con aviso AEMET naranja. Tendencia de agravamiento por viento fuerte. Población vulnerable en urbanización próxima. El scoring confirma P2 por acumulación de factores contextuales sin alcanzar umbral P1.



Caso CASO-003: Accidente de tráfico leve (P3)
ID
CASO-003
Fecha/hora
2024-03-10 09:45
Localización
A-2, km 315, Comarca Comunidad de Calatayud, Zaragoza
Descripción
Colisión por alcance entre dos turismos en autovía. Un herido leve consciente y orientado. Sin atrapamiento. Tráfico ralentizado en un carril.
V04
N2.2.1 — Tráfico con víctimas
Fuente
Conductor implicado
V01
No
V02
1–2
V03
Personas
V05
No
V06
0
V07
No
V08
Verde
V09
Ninguno
V10
No
V11
No
V12
Estable
V13
Media (conductor implicado)
V14
1
V15
Fácil
Reglas duras
Ninguna
Prioridad
P3
Confianza
Alto
Justificación
Sin riesgo vital, sin atrapamiento, un herido leve. Sin factores agravantes contextuales. Gestión activa sin urgencia vital. P3 claro.


Caso CASO-004: Consulta informativa (P4)
ID
CASO-004
Fecha/hora
2024-01-20 11:00
Localización
Huesca capital, Hoya de Huesca, Huesca
Descripción
Ciudadano llama al 112 para preguntar si la carretera A-136 está cortada por nieve. No reporta ningún incidente ni situación de emergencia.
V04
N2.6.3 — Consulta informativa
Fuente
Ciudadano
V01
No
V02
0
V03
Sin daño
V05
No
V06
0
V07
No
V08
Amarillo (nieve)
V09
Nieve
V10
No
V11
No
V12
No aplica
V13
Media
V14
1
V15
No aplica
Reglas duras
Ninguna
Prioridad
P4
Confianza
Alto
Justificación
No hay incidente activo. Consulta informativa sin urgencia operativa. P4 sin ambigüedad.



Caso CASO-005: Incidente industrial con proximidad Seveso (Frontera P1/P2)
ID
CASO-005
Fecha/hora
2024-06-05 08:20
Localización
Polígono industrial Malpica, Zaragoza capital
Descripción
Alerta de fuga de producto químico en nave industrial próxima a instalación Seveso. Olor fuerte reportado por trabajadores de naves contiguas. Sin víctimas confirmadas. No se ha determinado aún si la instalación Seveso está directamente afectada.
V04
N1.2.2 — Incidente industrial Seveso
Fuente
Trabajadores (testigos directos)
V01
No confirmado
V02
0
V03
Personas (potencial)
V05
No
V06
11–100 (trabajadores naves contiguas)
V07
No
V08
Verde
V09
Ninguno
V10
No
V11
Sí (instalación Seveso en proximidad)
V12
Desconocida
V13
Media (testigos directos)
V14
2–3
V15
Fácil
Reglas duras
RD4 no activada (afectación directa no confirmada). Ninguna regla fija activada.
Prioridad
P2
Confianza
Medio
Justificación
Frontera P1/P2. RD4 exige afectación directa confirmada a la instalación Seveso, que aún no está determinada. Proximidad Seveso con fuga química y personas potencialmente expuestas justifican P2 por scoring (amenaza contextual + exposición). Confianza media por tendencia desconocida y afectación Seveso pendiente de confirmar. Si se confirma afectación directa, se activaría RD4 → P1 mínima.


Caso CASO-006: Incendio urbano con persona mayor no localizada (Frontera P2/P3)
ID
CASO-006
Fecha/hora
2024-11-18 21:30
Localización
Teruel capital, Comunidad de Teruel, Teruel
Descripción
Humo visible en escalera de edificio residencial de 4 plantas. Un vecino informa de que una persona mayor que vive sola en el 3.º no responde al timbre. No hay confirmación de atrapamiento.
V04
N2.3.1 — Incendio vivienda/local
Fuente
Vecino (testigo directo)
V01
No confirmado
V02
0
V03
Personas (potencial)
V05
Sí (persona mayor)
V06
1–10 (residentes edificio)
V07
Residencia
V08
Verde
V09
Ninguno
V10
No
V11
No
V12
Desconocida
V13
Media (vecino testigo directo)
V14
1
V15
Fácil
Reglas duras
Ninguna activada (V01=No, V02=0)
Prioridad
P2
Confianza
Medio
Justificación
Frontera P2/P3. No se activa ninguna regla dura. Sin embargo, presencia de humo en escalera + persona mayor no localizada + tendencia desconocida configuran escenario con potencial de escalado y vulnerabilidad. Criterio de desempate P2/P3 del Anexo C: dos factores significativos empujan a P2. Principio de precaución razonable aplicado.



Caso CASO-007: Corte de suministro eléctrico (Frontera P3/P4)
ID
CASO-007
Fecha/hora
2024-12-08 19:00
Localización
Jaca, La Jacetania, Huesca
Descripción
Corte de electricidad en barrio residencial de Jaca. Temperatura exterior bajo cero. Varias familias con menores y personas mayores afectadas. Compañía eléctrica estima reparación en 4–6 horas.
V04
N2.6.1 — Corte suministro esencial
Fuente
Ciudadanos y compañía eléctrica
V01
No
V02
0
V03
Sin daño (disconfort)
V05
Sí (menores y mayores)
V06
11–100
V07
Residencia
V08
Amarillo (nieve/helada)
V09
Temperatura
V10
No
V11
No
V12
Estable
V13
Alta (compañía + vecinos)
V14
2–3
V15
Moderada
Reglas duras
Ninguna
Prioridad
P3
Confianza
Alto
Justificación
Frontera P3/P4. El corte de suministro por sí solo sería P4, pero la combinación de temperatura bajo cero, población vulnerable (menores y mayores) y duración estimada de 4–6 horas eleva a P3. Requiere gestión activa (coordinación con compañía, posible habilitación de albergue municipal) sin urgencia vital.


Caso CASO-008: Búsqueda de menor desaparecido (P2)
ID
CASO-008
Fecha/hora
2024-08-12 18:45
Localización
Albarracín, Sierra de Albarracín, Teruel
Descripción
Familia reporta desaparición de niño de 7 años en zona de senderos. Lleva una hora sin localizarlo. Atardecer próximo. Terreno montañoso con barrancos.
V04
N2.4.3 — Búsqueda de persona
Fuente
Familia (testigos directos)
V01
No confirmado
V02
0
V03
Personas (potencial)
V05
Sí (menor de edad)
V06
1–10
V07
No
V08
Verde
V09
Ninguno
V10
No
V11
No
V12
Desconocida
V13
Alta (familia directa)
V14
1
V15
Difícil (montaña, senderos, barrancos)
Reglas duras
RD6 (búsqueda de menor → P2 mínima)
Prioridad
P2
Confianza
Alto
Justificación
Regla RD6 activada: búsqueda de persona menor. Factores agravantes: atardecer próximo, terreno difícil con barrancos. No se eleva a P1 porque no hay evidencia de riesgo vital inmediato, pero la combinación de vulnerabilidad + accesibilidad + hora podría justificar P1 si la búsqueda se prolonga sin resultado.


D.4. Criterios de plausibilidad de casos
Cada caso del dataset piloto debe superar cinco controles de plausibilidad antes de incorporarse al dataset, conforme al protocolo definido en el apartado 7.3.2 del Capítulo 7:
Coherencia geográfica. El tipo de incidente debe ser compatible con la localización aragonesa asignada. Una inundación fluvial en Ejea de los Caballeros es plausible (río Arba); una inundación marítima en Teruel no lo es.
Coherencia temporal. La fecha y hora deben ser coherentes con la época del año. Un incendio forestal en julio en Aragón es plausible; un incendio forestal en enero con nieve acumulada no lo es.
Coherencia meteorológica. El aviso AEMET asignado debe ser coherente con el fenómeno y con la época. Un aviso naranja por temperatura extrema en julio es plausible; en enero debería ser por nieve o helada, no por calor.
Coherencia interna de variables. Los valores de las quince variables deben ser mutuamente compatibles. Un caso con V01=Sí y V02=0 y V03=Sin daño sería incoherente: riesgo vital sin daño aparente es contradictorio.
Coherencia con el etiquetado. La prioridad asignada debe ser defendible mediante la guía del Anexo C. Un caso con riesgo vital confirmado etiquetado como P3 sería incoherente con la regla RD1.
Los ocho casos presentados en D.3 superan los cinco controles. Todas las localizaciones son municipios reales de Aragón; las fechas y condiciones meteorológicas son plausibles para la época; las variables son internamente coherentes; y las prioridades son defendibles conforme a la guía de etiquetado.

D.5. Observaciones metodológicas
D.5.1. Representatividad de los casos presentados
Los ocho casos de este anexo cubren cuatro niveles de prioridad (P1, P2, P3, P4), cuatro casos de frontera o con características especiales (Seveso, incendio urbano con vulnerable, corte suministro, búsqueda menor), seis de las diez familias de la taxonomía y cinco de las ocho reglas duras (RD1, RD6, RD7, RD8 y el análisis de no activación de RD4). Esta cobertura es representativa del tipo de escenarios del dataset piloto, pero no lo sustituye.
D.5.2. El dataset completo se construye con la misma plantilla
Los 120–150 casos del dataset piloto se documentan con la misma plantilla maestra (Tabla D.1). Cada caso supera los cinco controles de plausibilidad y se etiqueta conforme a la guía del Anexo C. El proceso incluye revisión cruzada por al menos dos miembros del equipo.
D.5.3. Variables ausentes en los casos
Algunos casos del dataset piloto tendrán variables ausentes de forma deliberada, para evaluar la robustez del motor ante información incompleta (requisito RNF5, Capítulo 5). En esos casos, la plantilla registra «ausente» en el campo correspondiente, el valor por defecto aplicado conforme al Anexo B se documenta en la justificación, y la confianza se reduce según la criticidad de la variable ausente.
D.5.4. Limitaciones
Los casos presentados son simulados, no reales. Sus localizaciones, fechas y descripciones son plausibles pero ficticias. El etiquetado es interno al equipo del TFM y no ha sido validado por un panel externo de operadores del 112. Estas limitaciones se reconocen explícitamente en el Capítulo 7 (apartado 7.3.3) y no invalidan el TFM, pero acotan el alcance de la evaluación.

