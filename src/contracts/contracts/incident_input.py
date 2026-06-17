"""E-01 — `IncidentInput`: dato crudo del operador 112 antes de procesamiento."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .enums import CategoriaPreliminar, ProvinciaCyL


class IncidentInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    incident_id: Annotated[str, Field(min_length=1, max_length=64)]
    texto_titulo: Annotated[str, Field(min_length=1, max_length=200)]
    texto_descripcion: Annotated[str, Field(max_length=5000)] = ""
    categoria_preliminar: CategoriaPreliminar | None = None
    latitud: Annotated[float, Field(ge=-90.0, le=90.0)] | None = None
    longitud: Annotated[float, Field(ge=-180.0, le=180.0)] | None = None
    localidad: Annotated[str, Field(max_length=120)] | None = None
    provincia: ProvinciaCyL | None = None
    fecha_incidente: datetime
    operador_id: Annotated[str, Field(min_length=1, max_length=64)]

    @field_validator("fecha_incidente")
    @classmethod
    def _require_tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("fecha_incidente debe ser timezone-aware (TZ Europe/Madrid)")
        return v

    @model_validator(mode="after")
    def _coords_paired(self) -> IncidentInput:
        if (self.latitud is None) != (self.longitud is None):
            raise ValueError("latitud y longitud deben definirse juntas o ambas ser None")
        return self

    @model_validator(mode="after")
    def _text_has_alphabetic(self) -> IncidentInput:
        merged = self.texto_titulo + self.texto_descripcion
        if not any(c.isalpha() for c in merged):
            raise ValueError(
                "texto_titulo o texto_descripcion debe contener al menos un carácter alfabético"
            )
        return self
