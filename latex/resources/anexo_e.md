Anexo E. Tabla de reglas y pesos del baseline
E.1. Finalidad del anexo
Este anexo constituye la especificación técnica completa del razonamiento del motor de priorización. Su función es documentar, con el nivel de detalle necesario para la implementación y la defensa ante tribunal, la lógica interna del baseline interpretable de tres capas diseñado en el Capítulo 6.
El anexo cumple cuatro finalidades complementarias. En primer lugar, especifica la tabla ampliada de reglas duras, detallando para cada regla su condición exacta de activación, las variables implicadas, la prioridad resultante, la base normativa orientativa, la justificación operativa y las observaciones de implementación. En segundo lugar, desarrolla los pesos del scoring por grupos funcionales, haciendo explícita la lógica de ponderación y su fundamentación en la jerarquía normativa y operativa del dominio. En tercer lugar, documenta los umbrales iniciales de corte que traducen la puntuación del scoring a la escala P1–P4, dejando constancia de su carácter calibrable. Y en cuarto lugar, formaliza las reglas de combinación entre las tres capas del baseline —reglas duras, scoring y confianza— y describe la lógica de precedencia que gobierna la interacción entre ellas.
El contenido de este anexo no introduce decisiones nuevas, sino que expande con precisión técnica las decisiones cerradas en los apartados 6.6.2, 6.7.1, 6.7.2, 6.7.3, Tabla 6.3, Tabla 6.4 y Tabla 6.5 del Capítulo 6. La calibración definitiva de pesos y umbrales se realiza en la fase de evaluación (Capítulo 9).

E.2. Tabla ampliada de reglas duras
E.2.1. Naturaleza y función de las reglas duras
Las reglas duras son condiciones deterministas que fijan o limitan la prioridad del incidente sin necesidad de aplicar la capa de scoring. Constituyen la primera línea de evaluación del motor y su función principal es actuar como red de seguridad: garantizar que los escenarios más críticos no queden infraestimados por un promedio ponderado que podría diluir la urgencia real.
Las reglas duras se evalúan secuencialmente. Si una regla se activa, fija una prioridad mínima o absoluta según el caso. Solo después de esta evaluación el incidente pasa a la segunda capa (scoring), que puede mantener o elevar la prioridad resultante, pero nunca rebajarla por debajo del mínimo establecido por una regla dura.
Existen dos tipos de asignación:
Prioridad fija. La regla establece una prioridad inamovible. El scoring se calcula igualmente —para alimentar la explicación y la confianza—, pero no puede alterar el nivel de prioridad asignado. Es el caso de RD1 (riesgo vital confirmado) y RD7 (inundación con personas aisladas o atrapadas).
Prioridad mínima. La regla establece un suelo que el scoring no puede perforar. Si el scoring produce una prioridad igual o superior al mínimo, prevalece el scoring. Si produce una prioridad inferior, prevalece el mínimo de la regla dura. Es el caso de RD2, RD3, RD4, RD5, RD6 y RD8.
E.2.2. Regla de precedencia entre reglas duras
Cuando múltiples reglas duras se activan simultáneamente sobre un mismo incidente, prevalece la regla que asigne la prioridad más alta. Así, si un incidente activa RD2 (P2 mínima) y también RD5 (P1 mínima), la prioridad resultante de la capa de reglas duras es P1 mínima. Si además se activa RD1 (P1 fija), la prioridad queda fijada en P1 sin posibilidad de modificación.
Esta regla de precedencia es coherente con el criterio de resolución de conflictos del apartado 6.6.3 del Capítulo 6: cuando diferentes variables apuntan hacia prioridades distintas, prevalece la señal de mayor urgencia compatible con la información disponible.
E.2.3. Fichas detalladas de las reglas duras
A continuación se presenta la ficha ampliada de cada una de las ocho reglas duras del baseline. Las reglas se evalúan en el orden RD1–RD8, aunque la precedencia final viene determinada por la prioridad más alta activada, no por el orden de evaluación.
RD1. Riesgo vital inmediato confirmado
ID de regla
RD1
Condición de activación
V01 = Sí (riesgo vital inmediato confirmado o altamente probable según la comunicación del alertante o información de servicios intervinientes)
Variables implicadas
V01 (Riesgo vital inmediato)
Prioridad resultante
P1
Tipo de asignación
Fija (inamovible). El scoring se calcula para la explicación, pero no altera la prioridad.
Orden de evaluación
Evaluada en primer lugar. Si se activa, la prioridad queda determinada de forma definitiva.
Base normativa orientativa
Principio de protección de la vida (Ley 17/2015 art. 1; Ley 4/2024 art. 3). La vida humana constituye el bien jurídico supremo en todo el sistema de protección civil.
Justificación operativa
Un incidente con riesgo vital confirmado exige atención inmediata sin excepción. Ninguna combinación de factores secundarios puede justificar una rebaja de prioridad cuando la vida está en peligro inminente.
Interacción con otras reglas
Prevalece sobre cualquier otra regla. Si RD1 se activa, las demás reglas duras se registran para la explicación, pero no modifican la prioridad.
Observaciones
Esta es la regla con mayor impacto del sistema. Su carácter fijo (no solo mínimo) refleja la no negociabilidad del riesgo vital en el dominio de emergencias.


RD2. Víctimas confirmadas ≥ 3
ID de regla
RD2
Condición de activación
V02 ≥ 3 (rango 3–10 o superior). El alertante reporta tres o más personas con daño físico confirmado o altamente probable.
Variables implicadas
V02 (Víctimas confirmadas o probables)
Prioridad resultante
P2 mínima
Tipo de asignación
Mínima. El scoring puede elevar a P1 si otros factores lo justifican, pero no puede asignar P3 o P4.
Orden de evaluación
Evaluada tras RD1.
Base normativa orientativa
Lógica de activación por múltiples víctimas coherente con los umbrales de accidente con múltiples víctimas (AMV) y con los criterios de escalado del PLATEAR.
Justificación operativa
Tres o más víctimas simultáneas implican necesidad de coordinación reforzada y movilización de recursos adicionales, lo que excluye una prioridad media o baja.
Interacción con otras reglas
Si V02 > 10, se activa también RD5 (P1 mínima), que prevalece por tener prioridad superior.
Observaciones
El umbral de 3 víctimas es una decisión de diseño del prototipo basada en la experiencia operativa de coordinación. No constituye una cifra normativa oficial.



RD3. Aviso AEMET rojo con coherencia de incidente
ID de regla
RD3
Condición de activación
V08 = Rojo Y existe coherencia entre el fenómeno meteorológico (V09) y el tipo de incidente (V04). La coherencia exige que el fenómeno meteorológico sea pertinente para la naturaleza del incidente (por ejemplo, aviso rojo por lluvia en un incidente de inundación, o aviso rojo por viento en un incendio forestal).
Variables implicadas
V08 (Nivel de aviso AEMET), V09 (Fenómeno meteorológico activo), V04 (Tipo de incidente)
Prioridad resultante
P2 mínima
Tipo de asignación
Mínima. El scoring puede elevar a P1 si la combinación con otras variables lo justifica.
Orden de evaluación
Evaluada tras RD2.
Base normativa orientativa
PROCIFEMAR: vincula niveles de aviso AEMET con fases de emergencia. Directriz Básica de Inundaciones: umbrales de activación. PROCINFO: condiciones meteorológicas extremas como factor de riesgo de propagación.
Justificación operativa
Un aviso AEMET rojo indica riesgo extremo con potencial de agravamiento rápido. Cuando el fenómeno es coherente con el tipo de incidente, el contexto meteorológico agrava significativamente la situación.
Interacción con otras reglas
La condición de coherencia evita que un aviso rojo genérico (por ejemplo, por temperatura extrema) eleve artificialmente la prioridad de un incidente no relacionado (por ejemplo, un accidente de tráfico sin componente meteorológico).
Observaciones
La verificación de coherencia entre V08/V09 y V04 es una decisión de diseño que prioriza la precisión contextual frente a la activación indiscriminada.


RD4. Incidente Seveso con afectación directa confirmada
ID de regla
RD4
Condición de activación
V11 = Sí Y existe afectación directa confirmada al establecimiento Seveso. No basta la mera proximidad geográfica: debe haber evidencia de que el incidente involucra o amenaza directamente a la instalación industrial.
Variables implicadas
V11 (Presencia de instalación Seveso), contexto de afectación derivado de V04 y la comunicación del incidente
Prioridad resultante
P1 mínima
Tipo de asignación
Mínima. El scoring podría confirmar P1, pero no puede rebajar a P2 o inferior.
Orden de evaluación
Evaluada tras RD3.
Base normativa orientativa
RD 840/2015 (transposición de la Directiva Seveso III). Norma Básica de Protección Civil: riesgo químico como riesgo catalogado. PLATEAR: procedimientos específicos para emergencias en establecimientos afectados.
Justificación operativa
Un incidente con afectación directa a una instalación Seveso tiene un potencial catastrófico elevado que justifica la máxima prioridad desde el primer momento. La naturaleza de las sustancias involucradas puede producir efectos irreversibles en muy corto plazo.
Interacción con otras reglas
La proximidad sin afectación directa no activa esta regla, pero sí contribuye al scoring contextual con un incremento moderado.
Observaciones
La distinción entre proximidad y afectación directa es crítica para evitar falsos positivos. El registro público de establecimientos Seveso (datos.gob.es) permite el cruce geoespacial.



RD5. Víctimas confirmadas > 10
ID de regla
RD5
Condición de activación
V02 > 10. El alertante o los servicios intervinientes reportan más de diez personas con daño físico confirmado o altamente probable.
Variables implicadas
V02 (Víctimas confirmadas o probables)
Prioridad resultante
P1 mínima
Tipo de asignación
Mínima. Dado que P1 es el nivel máximo, en la práctica el efecto es equivalente a prioridad P1 asegurada.
Orden de evaluación
Evaluada tras RD4. Si RD1 también está activa, RD1 fija P1 de forma absoluta.
Base normativa orientativa
Escenario compatible con accidente con múltiples víctimas (AMV) de alta entidad. Lógica de escalado del PLATEAR y del PLEGEM para emergencias de gran magnitud.
Justificación operativa
Más de diez víctimas simultáneas representan una magnitud incompatible con cualquier prioridad media o baja. Requieren movilización masiva y coordinación multiagencia inmediata.
Interacción con otras reglas
Subsume a RD2 (que fija P2 mínima para ≥3 víctimas). Ambas pueden activarse simultáneamente, pero RD5 prevalece por asignar prioridad superior.
Observaciones
El umbral de 10 víctimas es una decisión de diseño del prototipo coherente con los escenarios de AMV de alta entidad descritos en la literatura operativa.


RD6. Búsqueda de persona menor o vulnerable
ID de regla
RD6
Condición de activación
V04 corresponde a un incidente de búsqueda de persona Y (V05 = Sí O la persona buscada es menor de edad según la comunicación del alertante).
Variables implicadas
V04 (Tipo de incidente), V05 (Población vulnerable)
Prioridad resultante
P2 mínima
Tipo de asignación
Mínima. El scoring puede elevar a P1 si concurren factores agravantes (condiciones meteorológicas adversas, terreno de difícil acceso, horas de oscuridad, etc.).
Orden de evaluación
Evaluada tras RD5.
Base normativa orientativa
Protección reforzada de colectivos vulnerables (Ley 4/2024 art. 6.2; Ley 17/2015). Especial sensibilidad operativa y mediática de la búsqueda de menores.
Justificación operativa
La búsqueda de una persona menor o vulnerable tiene una sensibilidad operativa especial que justifica una prioridad mínima alta, incluso cuando no exista evidencia inmediata de riesgo vital.
Interacción con otras reglas
No se activa para búsquedas de adultos sin indicadores de vulnerabilidad, que se evalúan exclusivamente por el scoring.
Observaciones
La condición combina el tipo de incidente (búsqueda) con la vulnerabilidad del sujeto. No basta la vulnerabilidad genérica si el tipo de incidente no es una búsqueda.



RD7. Inundación con personas aisladas o atrapadas
ID de regla
RD7
Condición de activación
V04 corresponde a un incidente de inundación Y existen personas aisladas o atrapadas por el agua según la comunicación del alertante o información de servicios intervinientes.
Variables implicadas
V04 (Tipo de incidente), información contextual de la comunicación (personas aisladas/atrapadas)
Prioridad resultante
P1 fija
Tipo de asignación
Fija (inamovible). Al igual que RD1, el scoring se calcula para la explicación, pero no altera la prioridad.
Orden de evaluación
Evaluada tras RD6.
Base normativa orientativa
Directriz Básica ante Riesgo de Inundaciones. PROCINAR: riesgo hidrológico con afectación directa a personas como escenario de máxima urgencia.
Justificación operativa
Personas aisladas o atrapadas por una inundación se encuentran en riesgo vital inmediato por ahogamiento, hipotermia o arrastre. La intervención no admite demora.
Interacción con otras reglas
Conceptualmente vinculada a RD1 (riesgo vital), pero formulada como regla independiente para garantizar su activación explícita en el contexto hidrológico, incluso si la comunicación no emplea explícitamente el término «riesgo vital».
Observaciones
La condición «personas aisladas o atrapadas» se extrae de la comunicación del alertante. En caso de duda, el principio de precaución razonable orienta hacia la activación.


RD8. Incendio forestal en interfaz urbano-forestal con AEMET naranja o rojo
ID de regla
RD8
Condición de activación
V04 corresponde a incendio forestal en interfaz urbano-forestal Y V08 ≥ Naranja (naranja o rojo) para un fenómeno coherente (viento, temperatura extrema).
Variables implicadas
V04 (Tipo de incidente), V08 (Nivel de aviso AEMET), V09 (Fenómeno meteorológico activo)
Prioridad resultante
P2 mínima
Tipo de asignación
Mínima. El scoring puede elevar a P1 si concurren factores agravantes adicionales (población expuesta, accesibilidad difícil, tendencia de agravamiento).
Orden de evaluación
Evaluada en último lugar (tras RD7).
Base normativa orientativa
PROCINFO: condiciones meteorológicas adversas como factor de riesgo de propagación en incendios forestales. PROCIFEMAR: vinculación entre avisos AEMET y fases de emergencia.
Justificación operativa
Un incendio forestal en interfaz urbano-forestal con condiciones meteorológicas adversas presenta un riesgo plausible de escalada rápida hacia zona habitada. La prioridad mínima P2 garantiza una respuesta coordinada temprana.
Interacción con otras reglas
Si el incendio cursa con víctimas (≥3), RD2 o RD5 también se activarán. Si existe riesgo vital confirmado, RD1 prevalece con P1 fija.
Observaciones
La interfaz urbano-forestal es el factor clave: un incendio forestal en zona puramente forestal sin proximidad a población no activa esta regla, aunque se evalúa normalmente por el scoring.


E.2.4. Tabla resumen de reglas duras
Tabla E.1. Resumen de reglas duras del baseline interpretable
ID
Condición
Prioridad
Tipo
Base normativa
Variables
RD1
Riesgo vital inmediato confirmado (V01 = Sí)
P1
Fija
Principio de protección de la vida
V01
RD2
Víctimas confirmadas ≥ 3
P2 mín.
Mínima
Lógica de activación AMV
V02
RD3
Aviso AEMET rojo + coherencia con incidente
P2 mín.
Mínima
PROCIFEMAR; Directriz Inundaciones
V08, V09, V04
RD4
Incidente Seveso + afectación directa
P1 mín.
Mínima
RD 840/2015 (Seveso III)
V11, V04
RD5
Víctimas confirmadas > 10
P1 mín.
Mínima
Escenario AMV alta entidad
V02
RD6
Búsqueda menor o persona vulnerable
P2 mín.
Mínima
Protección colectivos vulnerables
V04, V05
RD7
Inundación con personas aisladas/atrapadas
P1
Fija
Directriz Inundaciones; PROCINAR
V04
RD8
Incendio IUF + AEMET ≥ naranja
P2 mín.
Mínima
PROCINFO; PROCIFEMAR
V04, V08, V09

Fuente: elaboración propia. Ampliación de la Tabla 6.3 del Capítulo 6. Estas reglas expresan condiciones funcionales del prototipo y no decisiones jurídicas automáticas de activación.

E.3. Pesos del scoring por grupos funcionales
E.3.1. Principios de diseño del scoring
La segunda capa del baseline calcula una puntuación de prioridad mediante una combinación ponderada de variables normalizadas. Esta capa no sustituye a las reglas duras: opera sobre los casos en los que no existe una condición determinista suficiente o en los que conviene modular la urgencia con mayor gradación. Los principios que gobiernan el diseño del scoring son los siguientes:
Ponderación por grupos funcionales. Los pesos se asignan a los seis grupos funcionales definidos en el Capítulo 6, no a variables individuales de forma aislada. Esto facilita la interpretabilidad y reduce la arbitrariedad en la asignación.
Jerarquía normativa. El peso de cada grupo refleja su posición en la jerarquía de protección civil: la gravedad inmediata (protección de la vida) recibe el mayor peso, seguida de la vulnerabilidad, la amenaza contextual, el escalado y el contexto operativo.
Carácter orientativo. Los pesos iniciales no son verdad empírica cerrada, sino punto de partida fundamentado que se calibrará en la fase de evaluación (Capítulo 9) mediante el contraste con el etiquetado humano del dataset piloto.
Exclusión de la calidad de información del scoring. Las variables V13 (fiabilidad del informador) y V14 (número de avisos simultáneos) no ponderan en el cálculo de urgencia. Modulan exclusivamente la confianza de la recomendación (capa 3). Esta decisión evita que un incidente grave reportado por fuente anónima vea reducida artificialmente su prioridad.
E.3.2. Tabla ampliada de pesos por grupo funcional
Tabla E.2. Pesos orientativos del scoring por grupo funcional: especificación ampliada
Grupo funcional
Variables
Peso orientativo
Justificación y observaciones
Gravedad inmediata
V01, V02, V03
0,30–0,40
Grupo con mayor peso. Refleja el principio de protección de la vida como prioridad absoluta del sistema de protección civil (Ley 17/2015 art. 1). Dentro del grupo, V01 tiene el mayor impacto unitario (pero su activación suele disparar RD1 antes de llegar al scoring), V02 modula en función del rango y V03 aplica la jerarquía Personas > Bienes > Medioambiente > Sin daño. El peso se distribuye internamente de forma proporcional al impacto sobre la urgencia operativa.
Vulnerabilidad y exposición
V05, V06, V07
0,15–0,20
Segundo grupo en importancia. Recoge la magnitud potencial del incidente y la sensibilidad de la población expuesta. V06 (personas en riesgo estimadas) aporta una dimensión prospectiva que complementa la gravedad actual de V02. V05 (población vulnerable) y V07 (emplazamiento crítico) añaden indicadores de sensibilidad territorial y humana. La Ley 4/2024 art. 6.2 refuerza la atención especial a colectivos vulnerables.
Amenaza contextual
V08, V09, V10, V11
0,15–0,20
Grupo que incorpora el contexto territorial y meteorológico oficial. Las variables de este grupo conectan directamente con la lógica de los planes especiales de Aragón: el nivel de aviso AEMET (PROCIFEMAR), la peligrosidad por inundación (PROCINAR) y la presencia Seveso (RD 840/2015). V09 pondera de forma condicionada: solo contribuye al scoring cuando el fenómeno es coherente con el tipo de incidente. El peso global del grupo es moderado porque su activación crítica se canaliza a través de las reglas duras (RD3, RD4, RD8).
Escalado y evolución
V04, V12
0,10–0,15
Recoge el potencial de agravamiento y la naturaleza del incidente. V04 (tipo de incidente) no puntúa gravedad directamente, sino que condiciona qué contexto se consulta y qué reglas pueden activarse; su peso en el scoring es moderado. V12 (tendencia) aporta información dinámica: un incidente en agravamiento recibe un incremento significativo, mientras que la tendencia desconocida recibe un tratamiento intermedio conforme al principio de precaución razonable.
Contexto operativo
V15
0,05–0,10
Grupo con menor peso en el scoring. La accesibilidad al punto no modifica la gravedad intrínseca del incidente, pero sí condiciona la urgencia práctica de la decisión: un incidente de difícil acceso requiere anticipar la movilización. Su peso limitado evita que factores logísticos desplacen la evaluación de gravedad real.
Calidad de la información
V13, V14
No pondera scoring
Exclusión deliberada del scoring. Estas variables modulan la confianza de la recomendación (capa 3), no la urgencia directa. Un incidente grave reportado por fuente anónima mantiene su prioridad; la confianza se reduce, pero la urgencia no. V14 (número de avisos) refuerza la verosimilitud sin alterar la prioridad. Esta decisión es coherente con la arquitectura de tres capas del Capítulo 6.

Fuente: elaboración propia. Ampliación de la Tabla 6.4 del Capítulo 6. Los valores definitivos se calibran en la fase de evaluación.

E.3.3. Normalización de variables para el scoring
Para que la combinación ponderada sea coherente, cada variable de entrada debe normalizarse a un rango común antes de aplicar los pesos. La estrategia de normalización se adapta al tipo de dato de cada variable:
Variables binarias (V01, V05, V10, V11). Se codifican como 0 (No) o 1 (Sí). No requieren transformación adicional.
Variables ordinales (V02, V06, V08, V12, V13, V15). Se mapean a valores normalizados en el rango [0, 1] respetando el orden de sus categorías. Por ejemplo, V02: 0 → 0,0; 1–2 → 0,33; 3–10 → 0,67; >10 → 1,0. V08: verde → 0,0; amarillo → 0,33; naranja → 0,67; rojo → 1,0.
Variables categóricas (V03, V04, V07, V09). Se codifican mediante asignación ordinal basada en la jerarquía operativa. Por ejemplo, V03: Sin daño → 0,0; Medioambiente → 0,25; Bienes → 0,5; Personas → 1,0. V07: No → 0,0; Otro → 0,2; Infraestructura → 0,4; Residencia → 0,6; Educativo → 0,8; Sanitario → 1,0.
Variable numérica agrupada (V14). No participa en el scoring; se utiliza exclusivamente en la capa de confianza.
Los valores exactos de normalización son calibrables y su ajuste definitivo se realiza en la fase de evaluación. La lógica de normalización aquí descrita establece el punto de partida fundamentado.
E.3.4. Fórmula del scoring
La puntuación del scoring se calcula como una suma ponderada de los valores normalizados de las variables, agrupados por grupo funcional:
S = w₁ · G + w₂ · V + w₃ · A + w₄ · E + w₅ · C
Donde S es la puntuación de scoring (rango 0–100), G es la contribución normalizada del grupo de gravedad inmediata, V la de vulnerabilidad y exposición, A la de amenaza contextual, E la de escalado y evolución, y C la de contexto operativo. Los coeficientes w₁ a w₅ corresponden a los pesos orientativos de la Tabla E.2, normalizados para que sumen exactamente 1,0 antes de aplicar la fórmula. La normalización se realiza dividiendo cada peso por la suma de todos los pesos orientativos (0,92), obteniendo los pesos efectivos: w₁ = 0,380 (Gravedad), w₂ = 0,196 (Vulnerabilidad), w₃ = 0,196 (Amenaza), w₄ = 0,141 (Escalado), w₅ = 0,087 (Contexto operativo). Esta operación garantiza que la puntuación S permanezca siempre en el rango [0, 100] por construcción: el valor máximo teórico se obtiene cuando todas las variables normalizadas valen 1,0, produciendo S = (1,0 × w₁ + 1,0 × w₂ + 1,0 × w₃ + 1,0 × w₄ + 1,0 × w₅) × 100 = 1,0 × 100 = 100.
Cada contribución de grupo se calcula como el promedio ponderado de las variables normalizadas que lo componen. El resultado final se escala al rango 0–100 para facilitar la interpretación y la aplicación de los umbrales de corte.

E.4. Umbrales iniciales de corte P1–P4
La puntuación resultante del scoring se traduce a la escala de prioridad P1–P4 mediante umbrales de corte. Estos umbrales son iniciales y orientativos: su calibración definitiva se realiza en la fase de evaluación (Capítulo 9) mediante el contraste con el etiquetado humano del dataset piloto.
Tabla E.3. Umbrales indicativos de corte del scoring
Prioridad
Rango de puntuación
Interpretación
Observaciones
P1
≥ 75
Urgencia crítica. Incidente que requiere atención inmediata por gravedad extrema, riesgo vital probable o combinación de factores de máxima severidad.
En la práctica, muchos incidentes P1 son asignados directamente por reglas duras (RD1, RD4, RD5, RD7) antes de llegar al scoring. El umbral ≥75 captura los casos que alcanzan P1 exclusivamente por acumulación de factores en el scoring.
P2
50–74
Urgencia alta. Incidente con gravedad significativa o potencial de escalado relevante que requiere respuesta rápida coordinada.
Rango amplio que refleja la diversidad de escenarios P2: desde incidentes próximos a P1 por acumulación de factores hasta escenarios moderados elevados por contexto meteorológico o vulnerabilidad.
P3
25–49
Urgencia media. Incidente que requiere gestión activa sin urgencia vital. Controlable con medios ordinarios y admite demora razonable.
Rango esperado para la mayoría de incidentes del volumen operativo cotidiano del 112. La distribución del dataset piloto (35–40 % P3) refleja esta expectativa.
P4
< 25
Urgencia baja. Incidente menor, consulta informativa o verificación rutinaria sin componente de urgencia operativa.
Puntuaciones bajas por ausencia de factores de gravedad, exposición o amenaza contextual significativa.

Fuente: elaboración propia. Ampliación de la Tabla 6.5 del Capítulo 6. Estos umbrales son iniciales y su calibración definitiva se realiza en la fase de evaluación.
E.4.1. Criterios de calibración de los umbrales
La calibración de los umbrales en la fase de evaluación se guiará por los siguientes criterios:
Coherencia con el etiquetado humano. Los umbrales deben maximizar la concordancia entre la prioridad asignada por el motor y la prioridad de referencia asignada conforme a la guía de etiquetado. Las métricas principales son precisión, recall y F1 por nivel de prioridad.
Minimización de falsos negativos graves. Un incidente etiquetado como P1 que el motor clasifica como P3 o P4 es un error crítico. Los umbrales se ajustarán priorizando la sensibilidad en los niveles altos de la escala, asumiendo que es preferible un falso positivo moderado (elevar la prioridad de un incidente que resultó ser menos grave) a un falso negativo grave (infraestimar un incidente crítico).
Distribución razonable de prioridades. Los umbrales no deben producir una concentración artificial en un solo nivel de prioridad. Una distribución coherente con la Tabla 7.2 del Capítulo 7 (10–15 % P1, 20–25 % P2, 35–40 % P3, 20–25 % P4) indica un buen comportamiento discriminante.

E.5. Reglas de combinación entre reglas duras, scoring y confianza
E.5.1. Flujo de evaluación del motor
El motor evalúa cada incidente siguiendo un flujo secuencial de tres capas. El resultado final integra las salidas de las tres capas en una recomendación única que incluye prioridad, confianza y explicación. A continuación se formaliza la lógica de combinación:
Paso 1. Evaluación de reglas duras (Capa 1)
El motor evalúa secuencialmente las ocho reglas duras (RD1–RD8) sobre las variables de entrada del incidente. Se registran todas las reglas activadas, no solo la primera. La prioridad resultante de esta capa (P_RD) se determina por la regla activada que asigne la prioridad más alta:
Si alguna regla fija P1 (RD1, RD7): P_RD = P1 fija. La prioridad final es P1 independientemente del scoring.
Si alguna regla fija P1 mínima (RD4, RD5): P_RD = P1 mínima. El scoring solo puede confirmar P1.
Si alguna regla fija P2 mínima (RD2, RD3, RD6, RD8): P_RD = P2 mínima. El scoring puede asignar P1 o P2, pero no P3 ni P4.
Si ninguna regla se activa: P_RD = sin restricción. La prioridad se determina exclusivamente por el scoring.
Paso 2. Cálculo del scoring (Capa 2)
Independientemente de si se han activado reglas duras, el motor calcula la puntuación de scoring (S) según la fórmula descrita en E.3.4. La puntuación se traduce a una prioridad por scoring (P_S) mediante los umbrales de la Tabla E.3.
El scoring se calcula siempre, incluso cuando una regla dura fija ha determinado la prioridad. La razón es doble: la puntuación alimenta la explicación del motor (indicando qué factores contribuyen a la urgencia más allá de la regla dura activada) y permite evaluar en la fase de calibración si el scoring hubiera llegado a la misma conclusión que la regla dura.
Paso 3. Combinación de prioridades (Regla de integración)
La prioridad final recomendada (P_final) se determina según la siguiente lógica de precedencia:
Si P_RD es fija: P_final = P_RD. No hay negociación posible.
Si P_RD es mínima: P_final = max(P_RD, P_S). Es decir, la prioridad final es la más alta entre el mínimo de la regla dura y la prioridad del scoring. Si el scoring produce P1 y la regla dura solo fija P2 mínima, prevalece P1. Si el scoring produce P3 y la regla dura fija P2 mínima, prevalece P2.
Si no hay regla dura activa: P_final = P_S. La prioridad se determina exclusivamente por el scoring.
Paso 4. Cálculo de confianza (Capa 3)
El nivel de confianza de la recomendación se calcula a partir de tres factores:
Completitud de variables. Se evalúa qué proporción de las quince variables de entrada ha podido informarse efectivamente. Cada variable ausente reduce la confianza proporcionalmente a su criticidad (conforme a la tabla de ausencia de datos del Anexo B).
Fiabilidad del informador (V13). Una fuente oficial o agente (alta) mantiene la confianza; un testigo directo (media) la reduce ligeramente; una fuente indirecta o anónima (baja) la reduce significativamente.
Confirmación por múltiples avisos (V14). Múltiples avisos independientes sobre el mismo evento refuerzan la verosimilitud y elevan la confianza.
El resultado se expresa en una escala de tres niveles —alto, medio, bajo— conforme a lo definido en el apartado 6.7.3 del Capítulo 6. Esta escala es deliberadamente simple para facilitar su interpretación inmediata por el operador.
Tabla E.4. Umbrales orientativos del nivel de confianza
Nivel de confianza
Condición orientativa
Interpretación para el operador
Alto
Variables críticas informadas, V13 = Alta o Media, V14 ≥ 2
La recomendación se apoya en información suficiente y verificada. El operador puede confiar razonablemente en la prioridad sugerida.
Medio
Alguna variable relevante ausente, V13 = Media, V14 = 1
La recomendación es razonable pero se basa en información parcial. Se recomienda verificar los datos ausentes cuando sea posible.
Bajo
Variables críticas ausentes, V13 = Baja, información muy fragmentaria
La recomendación debe interpretarse con cautela. El operador debe priorizar la verificación de la información antes de tomar decisiones basadas exclusivamente en esta recomendación.

Fuente: elaboración propia. Coherente con el apartado 6.7.3 y con el requisito RF5 del Capítulo 5.
Paso 5. Generación de la explicación
La explicación textual resume la lógica que ha producido la recomendación. Incluye los siguientes elementos:
Reglas duras activadas: si alguna regla se ha activado, se identifica cuál y se indica su efecto sobre la prioridad.
Variables de mayor impacto en el scoring: se identifican las dos o tres variables que más han contribuido a la puntuación, indicando su valor y su grupo funcional.
Señales contextuales relevantes: avisos meteorológicos, peligrosidad por inundación, proximidad Seveso u otras señales que hayan modulado la evaluación.
Información ausente: se explicita qué variables no han podido informarse y cómo afecta esto a la confianza.
La explicación no es un elemento decorativo, sino una parte de la salida funcional del motor (conforme al apartado 6.1 y al requisito RF7 del Capítulo 5). Su función es permitir al operador entender, cuestionar y, si procede, corregir la recomendación.

E.5.2. Tabla resumen del flujo de integración
Tabla E.5. Resumen del flujo de integración de las tres capas del baseline
Paso
Capa
Operación
Salida
1
Reglas duras
Evaluar RD1–RD8 secuencialmente. Registrar todas las activadas. Determinar P_RD como la prioridad más alta activada.
P_RD (fija o mínima) o sin restricción; lista de reglas activadas
2
Scoring explicable
Normalizar variables. Calcular S = suma ponderada por grupos. Traducir S a P_S mediante umbrales.
P_S (P1–P4); puntuación S (0–100)
3
Integración
Si P_RD fija: P_final = P_RD. Si P_RD mínima: P_final = max(P_RD, P_S). Si sin restricción: P_final = P_S.
P_final (P1–P4)
4
Confianza
Evaluar completitud de variables, V13 y V14. Calcular nivel de confianza.
Confianza (Alto / Medio / Bajo)
5
Explicación
Construir explicación textual con reglas activadas, variables de mayor impacto, señales contextuales e información ausente.
Texto de explicación

Fuente: elaboración propia. Coherente con la arquitectura de tres capas del apartado 6.7 del Capítulo 6.

E.6. Observaciones de calibración futura
Los pesos, umbrales y criterios documentados en este anexo constituyen el diseño inicial del baseline. Su calibración definitiva se realizará en la fase de evaluación (Capítulo 9) y se regirá por las siguientes consideraciones:
E.6.1. Calibración de pesos
Los pesos orientativos de la Tabla E.2 se ajustarán mediante el contraste entre las prioridades producidas por el motor y las prioridades de referencia asignadas conforme a la guía de etiquetado. El proceso de calibración buscará minimizar la discrepancia global sin comprometer la sensibilidad en los niveles críticos (P1 y P2).
La calibración respetará la jerarquía normativa: el grupo de gravedad inmediata mantendrá el mayor peso relativo, y los grupos de calidad de información permanecerán excluidos del scoring. La calibración no modificará la estructura del baseline ni introducirá nuevas variables o reglas.
E.6.2. Calibración de umbrales
Los umbrales de corte de la Tabla E.3 se ajustarán para optimizar la concordancia con el etiquetado humano, priorizando la minimización de falsos negativos graves (incidentes P1 clasificados como P3 o P4). El ajuste podrá mover los límites entre rangos (por ejemplo, modificar el umbral P1/P2 de 75 a 70 si se observa que incidentes críticos quedan sistemáticamente justo por debajo del límite), pero no alterará la escala P1–P4 ni su significado operativo.
E.6.3. Reglas duras: estabilidad del diseño
Las reglas duras (RD1–RD8) no están sujetas a calibración paramétrica. Su diseño responde a condiciones lógicas deterministas derivadas de la normativa y la lógica operativa, y no depende de umbrales numéricos ajustables. La evaluación verificará que las reglas se activan correctamente en los escenarios previstos del dataset piloto y que su interacción con el scoring produce resultados coherentes.
E.6.4. Registro de cambios
Cualquier modificación de pesos o umbrales respecto a los valores iniciales documentados en este anexo se registrará de forma explícita en el Capítulo 9, indicando el valor inicial, el valor calibrado, la justificación del cambio y el impacto observado sobre las métricas de evaluación. Este registro garantiza la trazabilidad completa del proceso de calibración.
E.6.5. Limitaciones del enfoque de calibración
La calibración se realizará sobre el dataset piloto híbrido descrito en el Capítulo 7, compuesto mayoritariamente por casos simulados controlados. Esta circunstancia introduce una limitación inherente: los pesos y umbrales calibrados reflejarán el comportamiento óptimo para ese dataset específico, que puede no coincidir con el comportamiento óptimo para datos operativos reales del 112 Aragón. Esta limitación se reconoce explícitamente y se aborda en las conclusiones del TFM como línea de trabajo futuro.

