"""E-02 — `IncidentFeatures`: salida estructurada de Capa 1, entrada determinista de Capa 2.

V01–V07 y V12–V15 activos en v0.1.0. V08–V11 reservados (DIFERIDA v0.2.0 — R-13).
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from .enums import Accesibilidad, AvisoAEMET, CategoriaPreliminar, GravedadLesiones
from .primitives import BoolWithConfidence, Confidence, IntWithConfidence

_SEMVER_RX = r"^\d+\.\d+\.\d+$"


class IncidentFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    incident_id: Annotated[str, Field(min_length=1, max_length=64)]

    # ── V01–V07 (activos v0.1.0) ─────────────────────────────────────────
    riesgo_vital: BoolWithConfidence  # V01
    numero_victimas_estimado: IntWithConfidence  # V02 (-1 = desconocido; 0..50 esperado)
    gravedad_lesiones: GravedadLesiones  # V03
    gravedad_lesiones_confidence: Confidence
    tipo_incidente_normalizado: CategoriaPreliminar  # V04
    poblacion_vulnerable: BoolWithConfidence  # V05
    numero_llamadas: Annotated[int, Field(ge=1)]  # V06
    emplazamiento_critico: BoolWithConfidence  # V07

    # ── V08–V11 (DIFERIDOS v0.2.0 — R-13) ────────────────────────────────
    aviso_aemet_nivel: AvisoAEMET = AvisoAEMET.NO_DISPONIBLE  # V08
    condicion_meteorologica_adversa: BoolWithConfidence | None = None  # V09
    en_zona_inundable_snczi: bool | None = None  # V10
    proximo_instalacion_seveso_km: Annotated[float, Field(ge=0.0)] | None = None  # V11

    # ── V12–V15 (activos v0.1.0) ─────────────────────────────────────────
    riesgo_propagacion: BoolWithConfidence  # V12
    multirriesgo: BoolWithConfidence  # V13
    avisos_simultaneos_zona: Annotated[int, Field(ge=0)]  # V14
    accesibilidad_recursos: Accesibilidad  # V15

    # ── Signals léxicos (10) ─────────────────────────────────────────────
    signal_fallecido: BoolWithConfidence
    signal_herido_grave: BoolWithConfidence
    signal_atrapado: BoolWithConfidence
    signal_intoxicacion: BoolWithConfidence
    signal_varias_llamadas: BoolWithConfidence
    signal_incendio: BoolWithConfidence
    signal_accidente_trafico: BoolWithConfidence
    signal_rescate: BoolWithConfidence
    signal_meteo_inundacion: BoolWithConfidence
    riesgo_vital_textual: BoolWithConfidence

    # ── Metadatos de extracción ──────────────────────────────────────────
    model_version_capa1: Annotated[str, Field(pattern=_SEMVER_RX)]
    inference_timestamp: datetime
    inference_latency_ms: Annotated[float, Field(ge=0.0)]
    extractor_warnings: list[Annotated[str, Field(max_length=200)]] = Field(default_factory=list)
