# Auditoria del dataset limpio 112 CyL

- Fichero: `resources\dataset\processed\emergencias_112_cyl_2008_2022_clean.csv`
- Registros: 9380
- Columnas: 41
- Rango temporal valido: 2008-07-28 a 2022-12-31
- Fechas invalidas: 0
- Identificadores duplicados: 0
- Cobertura de coordenadas: 99.24%

## Distribucion por anio

- 2008: 92
- 2009: 398
- 2010: 344
- 2011: 404
- 2012: 685
- 2013: 669
- 2014: 675
- 2015: 745
- 2016: 874
- 2017: 897
- 2018: 753
- 2019: 768
- 2020: 631
- 2021: 710
- 2022: 735

## Distribucion por provincia inferida

- Avila: 875
- Burgos: 1549
- Leon: 3231
- NO_INFERIDA: 14
- Palencia: 453
- Salamanca: 840
- Segovia: 558
- Soria: 364
- Valladolid: 852
- Zamora: 644

## Categorias operativas preliminares

- trafico: 6782
- sanitario: 1710
- incendio: 798
- rescate_salvamento: 69
- meteorologico_inundacion: 15
- otros_no_clasificado: 6

## Seniales textuales

- signal_accidente_trafico: 6471
- signal_atrapado: 2810
- signal_fallecido: 1397
- signal_herido_grave: 1585
- signal_incendio: 1115
- signal_intoxicacion: 1178
- signal_meteo_inundacion: 710
- signal_rescate: 3524
- signal_varias_llamadas: 1712

## Columnas prohibidas por leakage

Se documentan para auditoria, pero quedan excluidas de weak labels y training.
- Enlace al contenido: 9380 valores no vacios
- IncidenteCerrado: 9266 valores no vacios
- MediosMov: 8440 valores no vacios
- PacientesAten: 83 valores no vacios
- medios_mov_limpio: 8434 valores no vacios
- medios_mov_uso_recomendado: 9380 valores no vacios
- pacientes_aten_limpio: 59 valores no vacios
- ultimaActualizacion: 9380 valores no vacios
