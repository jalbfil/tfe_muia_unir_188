"""T076 — Tool `get_rule_details`: detalle enriquecido de una regla activada.

Recibe rule_id + los datos de la regla (human_text, peso, anchors) y devuelve
un dict con contexto adicional: descripción expandida, nivel de evidencia
y los NormaID referenciados con sus URL oficiales.

Nota: los datos de la regla se pasan como parámetros (la tool es stateless).
"""
from __future__ import annotations

# Mapeo NormaID → URL oficial (misma fuente que manifest.yaml)
_NORMA_URLS: dict[str, str] = {
    "LEY_17_2015": "https://www.boe.es/buscar/act.php?id=BOE-A-2015-7730",
    "RD_524_2023": "https://www.boe.es/buscar/act.php?id=BOE-A-2023-14679",
    "PLEGEM": "https://www.boe.es/buscar/act.php?id=BOE-A-2020-16349",
    "LEY_4_2007_CYL": "https://www.boe.es/buscar/act.php?id=BOE-A-2007-9097",
    "PLANCAL_DEC_4_2019": "https://bocyl.jcyl.es/boletin.do?fechaBoletin=11/02/2019",
    "INFOCAL_DEC_6_2025": "https://bocyl.jcyl.es/boletin.do?fechaBoletin=31/03/2025",
    "INUNCYL": "https://bocyl.jcyl.es/boletines/2010/03/03/pdf/BOCYL-D-03032010-14.pdf",
    "MPCYL_ACUERDO_3_2008": "https://bocyl.jcyl.es/boletines/2008/01/23/pdf/BOCYL-D-23012008-8.pdf",
    "LEY_11_2022": "https://www.boe.es/buscar/act.php?id=BOE-A-2022-10757",
    "REGISTRO_112_CYL": "https://datosabiertos.jcyl.es/web/jcyl/set/es/sector-publico/emergencias-ultimo-ano/1285074931225",
    "RGPD": "https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32016R0679",
    "LOPDGDD": "https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673",
    "REG_UE_2024_1689": "https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689",
}


def get_rule_details(
    rule_id: str,
    human_text: str,
    weight: float,
    normative_anchors: list[str],
) -> dict:
    """Devuelve el detalle enriquecido de una regla activada.

    Args:
        rule_id:            Identificador de la regla (e.g. "RD-01").
        human_text:         Descripción legible de la regla.
        weight:             Peso de la regla en la predicción (float).
        normative_anchors:  Lista de NormaID (str) referenciados por la regla.

    Returns:
        Dict con: rule_id, human_text, weight, anchors (NormaID + url).
    """
    anchors_detail = [
        {
            "norma_id": nid,
            "url": _NORMA_URLS.get(nid, ""),
        }
        for nid in normative_anchors
    ]
    return {
        "rule_id": rule_id,
        "human_text": human_text,
        "weight": weight,
        "normative_anchors": anchors_detail,
        "evidence_level": "normative" if normative_anchors else "heuristic",
    }
