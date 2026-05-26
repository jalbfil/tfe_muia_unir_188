# Protocolo de validacion interna v0.1.0

Este protocolo documenta como revisar las recomendaciones del sistema antes de
considerar congelada la Capa 2 / RuleFit-lite. La validacion externa con personal del
112 queda fuera del alcance v0.1.0 y se declara como trabajo futuro.

## Objetivo

Comprobar que las recomendaciones P1--P4 son revisables, trazables y coherentes con
las evidencias disponibles en el Registro 112 CyL, especialmente en los casos de mayor
riesgo: falsos negativos P1, saltos de dos o mas niveles y baja confianza del modelo.

## Seleccion minima de casos

La muestra interna debe contener al menos 30 casos:

- todos los falsos negativos P1 detectados por `scripts/run_evaluation.py`, si son 30 o
  menos;
- una muestra estratificada por P1--P4 cuando los falsos negativos P1 no alcancen 30;
- casos frontera P1/P2 y P2/P3 con confianza baja o desacuerdo entre fuentes debiles;
- representacion de varias provincias, anos y categorias operativas.

## Evidencias que debe ver cada revisor

Cada ficha de revision debe mostrar:

- identificador del incidente, fecha, provincia y categoria preliminar;
- texto operativo anonimizado o minimizado;
- etiqueta academica P1--P4 y grado de acuerdo de weak supervision;
- prioridad recomendada por Capa 2, confianza y probabilidades P1--P4;
- reglas RuleFit activadas o, si se revisa el baseline, regla experta aplicada;
- senales V01--V15 disponibles y features permitidas usadas por la Capa 2;
- columnas excluidas por anti-leakage;
- explicacion normativa generada por Capa 3 cuando este disponible;
- version de modelo, hash de entrada y marca temporal del log de inferencia.

## Registro de feedback

El revisor debe registrar una de tres acciones:

- aceptar: la prioridad del sistema se considera adecuada;
- modificar: se asigna otra prioridad P1--P4 y se justifica el motivo;
- rechazar: la recomendacion no es util para el caso y debe revisarse el criterio.

El feedback se persiste mediante el contrato `OperatorDecision` y el endpoint
`POST /feedback`. La decision queda asociada al `InferenceLog` del caso, junto con el
`incident_id`, la prioridad recomendada, la prioridad asignada por el operador, el
motivo de divergencia, el identificador del revisor y la marca temporal. Si la
divergencia entre sistema y revisor es de dos o mas niveles, el contrato marca el caso
para auditoria especial.

## Criterios de analisis

La revision interna debe reportar:

- tasa de aceptacion directa;
- distribucion de cambios por prioridad;
- numero de divergencias de dos o mas niveles;
- patrones repetidos en falsos negativos P1;
- posibles sesgos por provincia, ano o categoria;
- reglas candidatas a ajuste o eliminacion;
- limitaciones observadas por ausencia de validacion externa 112.

## Limitaciones

Esta validacion es una revision academica interna. No sustituye a la validacion externa
con operadores reales del 112, no certifica despliegue operativo y no convierte la
etiqueta debil P1--P4 en verdad oficial. Su valor es garantizar trazabilidad,
detectar errores criticos antes de la defensa y documentar un procedimiento claro para
una evaluacion externa posterior.
