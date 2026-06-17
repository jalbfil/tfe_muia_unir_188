"""T043: Test de anti-leakage específico para la Capa 1 NLP (Principio V)."""

from __future__ import annotations

from pathlib import Path
import pytest

from contracts import PROHIBITED_FEATURE_COLUMNS

CAPA1_SRC_DIR = Path(__file__).resolve().parents[1]


def test_capa1_no_prohibited_columns_in_source_code() -> None:
    """Verifica estáticamente que ningún código productivo de Capa 1 referencie columnas prohibidas."""
    python_files = list(CAPA1_SRC_DIR.rglob("*.py"))
    assert len(python_files) > 0, "No se encontraron archivos de Python en Capa 1"

    offending_references: list[str] = []

    for file_path in python_files:
        # Excluir la carpeta de pruebas (tests) para evitar falsos positivos
        if "tests" in file_path.parts:
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            pytest.fail(f"No se pudo leer el archivo {file_path}: {e}")

        for col in PROHIBITED_FEATURE_COLUMNS:
            if col in content:
                offending_references.append(f"{file_path.name} referenca '{col}'")

    if offending_references:
        pytest.fail(
            "Violación del Principio V (no-leakage) detectada en Capa 1 NLP:\n"
            + "\n".join(offending_references)
        )
