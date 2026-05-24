"""Enumeraciones canónicas. Fuente única de verdad para valores categóricos del sistema."""

from __future__ import annotations

from enum import StrEnum


class Priority(StrEnum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class ConfidenceLevel(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class ModelUsed(StrEnum):
    RULEFIT = "RULEFIT"
    BASELINE_EXPERT = "BASELINE_EXPERT"
    FALLBACK = "FALLBACK"


class VariableSource(StrEnum):
    EXPERT_BASELINE = "EXPERT_BASELINE"
    RULEFIT_LEARNED = "RULEFIT_LEARNED"


class ProvinciaCyL(StrEnum):
    AVILA = "AVILA"
    BURGOS = "BURGOS"
    LEON = "LEON"
    PALENCIA = "PALENCIA"
    SALAMANCA = "SALAMANCA"
    SEGOVIA = "SEGOVIA"
    SORIA = "SORIA"
    VALLADOLID = "VALLADOLID"
    ZAMORA = "ZAMORA"


class CategoriaPreliminar(StrEnum):
    # Taxonomía preliminar derivada de TipoIncidente del 112 CyL. Refinada en T031.
    ACCIDENTE_TRAFICO = "ACCIDENTE_TRAFICO"
    INCENDIO_FORESTAL = "INCENDIO_FORESTAL"
    INCENDIO_URBANO = "INCENDIO_URBANO"
    INCIDENCIA_VIA = "INCIDENCIA_VIA"
    METEOROLOGIA = "METEOROLOGIA"
    QUIMICO_NRBQ = "QUIMICO_NRBQ"
    RESCATE = "RESCATE"
    SANITARIO = "SANITARIO"
    SEGURIDAD_CIUDADANA = "SEGURIDAD_CIUDADANA"
    SUMINISTROS = "SUMINISTROS"
    OTROS = "OTROS"
    DESCONOCIDA = "DESCONOCIDA"


class GravedadLesiones(StrEnum):
    NINGUNA = "NINGUNA"
    LEVE = "LEVE"
    MODERADA = "MODERADA"
    GRAVE = "GRAVE"
    CRITICA = "CRITICA"
    DESCONOCIDA = "DESCONOCIDA"


class AvisoAEMET(StrEnum):
    # V08 — DIFERIDO v0.2.0 (R-13). En v0.1.0 siempre NO_DISPONIBLE.
    VERDE = "VERDE"
    AMARILLO = "AMARILLO"
    NARANJA = "NARANJA"
    ROJO = "ROJO"
    NO_DISPONIBLE = "NO_DISPONIBLE"


class Accesibilidad(StrEnum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"
    DESCONOCIDA = "DESCONOCIDA"


class NormaID(StrEnum):
    # 13 normas activas v0.1.0 + Seveso reservada para v0.2.0 (ver corpus_normativo/README.md).
    LEY_17_2015 = "LEY_17_2015"
    RD_524_2023 = "RD_524_2023"
    PLEGEM = "PLEGEM"
    LEY_4_2007_CYL = "LEY_4_2007_CYL"
    PLANCAL_DEC_4_2019 = "PLANCAL_DEC_4_2019"
    INFOCAL_DEC_6_2025 = "INFOCAL_DEC_6_2025"
    INUNCYL = "INUNCYL"
    MPCYL_ACUERDO_3_2008 = "MPCYL_ACUERDO_3_2008"
    LEY_11_2022 = "LEY_11_2022"
    REGISTRO_112_CYL = "REGISTRO_112_CYL"
    RGPD = "RGPD"
    LOPDGDD = "LOPDGDD"
    REG_UE_2024_1689 = "REG_UE_2024_1689"
    RD_840_2015_SEVESO = "RD_840_2015_SEVESO"  # reservada v0.2.0
