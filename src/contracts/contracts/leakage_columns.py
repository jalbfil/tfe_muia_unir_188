"""Columnas prohibidas como features (Principio V: no leakage).

Fuente única consumida por `tests/test_leakage_gate.py` para escanear
`src/capa1_nlp/` y `src/capa2_rulefit/`. Ver `data-model.md` §"Columnas prohibidas".
"""

from __future__ import annotations

from typing import Final

PROHIBITED_FEATURE_COLUMNS: Final[frozenset[str]] = frozenset(
    {
        # Recursos movilizados — solo conocidos POST-decisión del operador
        "MediosMov",
        "medios_mov_limpio",
        "medios_mov_uso_recomendado",
        # Pacientes atendidos — solo conocido POST-incidente
        "PacientesAten",
        "pacientes_aten_limpio",
        # Cierre administrativo y enlaces — metadatos post-hoc
        "IncidenteCerrado",
        "ultimaActualizacion",
        "Enlace al contenido",
        # Artefacto de exportación
        "Unnamed: 13",
    }
)
