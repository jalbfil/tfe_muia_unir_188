"""T020 — Gate CI: schemas commiteados DEBEN coincidir con regenerados.

Si difieren sin bump de versión, falla el build. Forzar regeneración con:
    python scripts/export_schemas.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import export_schemas


def test_committed_schemas_match_regenerated() -> None:
    diffs = export_schemas.check_all(export_schemas.SCHEMAS_DIR)
    if diffs:
        pytest.fail(
            "Schemas commiteados divergen del código:\n  - "
            + "\n  - ".join(diffs)
            + "\nRegenera con `python scripts/export_schemas.py` y commitea los .schema.json."
        )


def test_all_public_models_have_a_schema_file_on_disk() -> None:
    for model in export_schemas.PUBLIC_MODELS:
        fname = f"{model.__name__}.schema.json"
        path = export_schemas.SCHEMAS_DIR / fname
        assert path.exists(), f"Falta schema commiteado: {fname}"
