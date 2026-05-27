# Corpus normativo CyL — fuentes oficiales (PDF/HTML) consumidas por la Capa 3 RAG

Este directorio contiene los textos legales y técnicos que alimentan la indexación RAG
(Capa 3) y las citas legales (`LegalCitation`) que el sistema devuelve al operador.

## Estructura

- [`manifest.yaml`](manifest.yaml) — fuente única de verdad. Cada entrada referencia
  un `NormaID` del enum `contracts.enums.NormaID`.
- Un subdirectorio por norma:
  - `<NORMA_ID>/<NORMA_ID>.pdf` — texto consolidado (se rellena al descargar).
  - `<NORMA_ID>/metadata.json` — copia de la entrada del manifest.
- [`../../scripts/download_corpus.py`](../../scripts/download_corpus.py) — descargador.

## Uso

```bash
# Verifica que todas las URLs responden 200 sin descargar:
python scripts/download_corpus.py --check

# Descarga el corpus completo (13 normas activas; Seveso diferida a v0.2.0):
python scripts/download_corpus.py

# Descarga una sola norma:
python scripts/download_corpus.py --norma PLANCAL_DEC_4_2019
```

Requisitos: `PyYAML` (`pip install pyyaml`, import `yaml`) y conexión a
`boe.es`, `bocyl.jcyl.es`, `eur-lex.europa.eu`, `datos.gob.es`.

## Normas activas en v0.1.0 (13)

| # | `NormaID` | Fuente | Estado URL |
|---|---|---|---|
| 1 | `LEY_17_2015` | BOE | verified |
| 2 | `RD_524_2023` | BOE | TBD verificar |
| 3 | `PLEGEM` | BOE (anexo RD 524/2023) | TBD verificar |
| 4 | `LEY_4_2007_CYL` | BOE | TBD verificar |
| 5 | `PLANCAL_DEC_4_2019` | BOCYL | TBD verificar |
| 6 | `INFOCAL_DEC_6_2025` | BOCYL | **TBD localizar** |
| 7 | `INUNCYL` | BOCYL | **TBD localizar** |
| 8 | `MPCYL_ACUERDO_3_2008` | BOCYL | **TBD localizar** |
| 9 | `LEY_11_2022` | BOE | verified |
| 10 | `REGISTRO_112_CYL` | datos.gob.es | TBD verificar |
| 11 | `RGPD` | DOUE (EUR-Lex) | verified |
| 12 | `LOPDGDD` | BOE | verified |
| 13 | `REG_UE_2024_1689` | DOUE (EUR-Lex) | verified |

## Diferidas a v0.2.0

- `RD_840_2015_SEVESO` — cartografía industrial CyL no consolidada (R-13).

## Procedimiento de actualización

1. Localizar la URL consolidada oficial.
2. Actualizar la entrada en [`manifest.yaml`](manifest.yaml) (`url_pdf`, `url_html`,
   `identificador`, `verified: true`).
3. Ejecutar `python scripts/download_corpus.py --norma <NORMA_ID>`.
4. Verificar que `resources/corpus_normativo/<NORMA_ID>/` contiene el PDF + metadata.
5. Lanzar `python scripts/build_rag_index.py` (T062) para re-indexar.
6. Commit con mensaje `corpus: refresh <NORMA_ID>`.

## Política de leakage

El corpus normativo es **lectura pura**: ninguna columna del dataset operativo entra
aquí. La política completa está en
[`../../src/contracts/docs/adr/0004-no-leakage-policy.md`](../../src/contracts/docs/adr/0004-no-leakage-policy.md).
