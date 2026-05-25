"""T078 — Tool `cite_legal_basis`: genera la cita canónica para un NormaID.

Devuelve un dict listo para construir `LegalCitation` (contrato E-04).
Las citas incluyen el artículo más relevante para el contexto de emergencias 112 CyL.
"""
from __future__ import annotations

# ── tabla estática de citas canónicas ──────────────────────────────────────────
# Clave: NormaID (str), Valor: {"articulo", "texto_relevante", "url_oficial"}
_CITAS: dict[str, dict] = {
    "LEY_17_2015": {
        "articulo": "art. 1",
        "texto_relevante": (
            "Objeto: regulación del Sistema Nacional de Protección Civil para la planificación, "
            "prevención, intervención de emergencia y recuperación ante situaciones de riesgo."
        ),
        "url_oficial": "https://www.boe.es/buscar/act.php?id=BOE-A-2015-7730",
    },
    "RD_524_2023": {
        "articulo": "art. 2",
        "texto_relevante": (
            "Norma Básica de Protección Civil: establece los requisitos mínimos de los planes "
            "de protección civil y los criterios de priorización de emergencias."
        ),
        "url_oficial": "https://www.boe.es/buscar/act.php?id=BOE-A-2023-14679",
    },
    "PLEGEM": {
        "articulo": "Capítulo II",
        "texto_relevante": (
            "Plan Estatal General de Emergencias: define los niveles de activación "
            "y la coordinación entre administraciones en emergencias de interés nacional."
        ),
        "url_oficial": "https://www.boe.es/buscar/act.php?id=BOE-A-2020-16349",
    },
    "LEY_4_2007_CYL": {
        "articulo": "art. 5",
        "texto_relevante": (
            "Ley 4/2007 de CyL: los municipios y diputaciones coordinarán con el 112 CyL "
            "la gestión de emergencias en su ámbito territorial."
        ),
        "url_oficial": "https://www.boe.es/buscar/act.php?id=BOE-A-2007-9097",
    },
    "PLANCAL_DEC_4_2019": {
        "articulo": "Título II",
        "texto_relevante": (
            "Plan de Protección Civil de CyL: establece los niveles de respuesta 1-4 "
            "y el protocolo de activación del CECOP ante emergencias."
        ),
        "url_oficial": "https://bocyl.jcyl.es/boletin.do?fechaBoletin=11/02/2019",
    },
    "INFOCAL_DEC_6_2025": {
        "articulo": "Capítulo III",
        "texto_relevante": (
            "Plan de Protección Civil ante Incendios Forestales en CyL: "
            "niveles de alerta y coordinación del 112 con medios aéreos y terrestres."
        ),
        "url_oficial": "https://bocyl.jcyl.es/boletin.do?fechaBoletin=31/03/2025",
    },
    "INUNCYL": {
        "articulo": "Capítulo II",
        "texto_relevante": (
            "Plan de Protección Civil ante Inundaciones en CyL: "
            "activación del CECOP ante avisos AEMET de nivel naranja/rojo en cuencas del Duero."
        ),
        "url_oficial": "https://bocyl.jcyl.es/boletines/2010/03/03/pdf/BOCYL-D-03032010-14.pdf",
    },
    "MPCYL_ACUERDO_3_2008": {
        "articulo": "art. 1",
        "texto_relevante": (
            "Plan de Protección Civil ante Transportes de Mercancías Peligrosas en CyL: "
            "protocolos de actuación ante derrames, fugas y explosiones en red viaria."
        ),
        "url_oficial": "https://bocyl.jcyl.es/boletines/2008/01/23/pdf/BOCYL-D-23012008-8.pdf",
    },
    "LEY_11_2022": {
        "articulo": "art. 76",
        "texto_relevante": (
            "Ley General de Telecomunicaciones: obligaciones del servicio 112 como servicio "
            "de llamadas de emergencia de acceso universal y gratuito."
        ),
        "url_oficial": "https://www.boe.es/buscar/act.php?id=BOE-A-2022-10757",
    },
    "RGPD": {
        "articulo": "art. 9",
        "texto_relevante": (
            "RGPD: tratamiento de datos especiales de salud en situaciones de emergencia "
            "justificado por interés vital del interesado (art. 9.2.c)."
        ),
        "url_oficial": "https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32016R0679",
    },
    "LOPDGDD": {
        "articulo": "art. 9",
        "texto_relevante": (
            "LOPDGDD: adecuación española del RGPD; el 112 puede tratar datos de salud "
            "en situaciones de emergencia sin consentimiento expreso."
        ),
        "url_oficial": "https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673",
    },
    "REG_UE_2024_1689": {
        "articulo": "Anexo III",
        "texto_relevante": (
            "Reglamento UE de IA: los sistemas de IA de apoyo a la decisión en servicios "
            "de emergencia son de alto riesgo (Anexo III) y requieren supervisión humana."
        ),
        "url_oficial": "https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689",
    },
}

_FALLBACK_CITA = {
    "articulo": None,
    "texto_relevante": "Norma de referencia en el ámbito de protección civil de CyL.",
    "url_oficial": None,
}


def cite_legal_basis(norma_id: str, articulo: str | None = None) -> dict:
    """Genera la cita canónica para un NormaID dado.

    Args:
        norma_id:  Identificador canónico (NormaID StrEnum como str).
        articulo:  Artículo específico a citar; si None, usa el predeterminado.

    Returns:
        Dict con keys: ``norma_id``, ``articulo_o_seccion``, ``texto_relevante``,
        ``url_oficial``.  Listo para construir ``LegalCitation``.
    """
    base = _CITAS.get(norma_id, _FALLBACK_CITA)
    return {
        "norma_id": norma_id,
        "articulo_o_seccion": articulo or base["articulo"],
        "texto_relevante": base["texto_relevante"],
        "url_oficial": base["url_oficial"],
    }
