"""T021 — Gate CI Principio V: ninguna columna prohibida puede ser referenciada
en código de Capa 1 o Capa 2.

Escanea texto plano por nombre de columna (case-sensitive) en:
    - src/capa1_nlp/**/*.py
    - src/capa2_rulefit/**/*.py

Allowlist explícita: tests bajo `tests/` y módulos cuyo nombre incluya
`leakage`/`prohibit`, donde mencionar las columnas ES el propósito.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from contracts import PROHIBITED_FEATURE_COLUMNS

REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [
    REPO_ROOT / "src" / "capa1_nlp",
    REPO_ROOT / "src" / "capa2_rulefit",
]
ALLOWED_FILE_KEYWORDS = ("leakage", "prohibit", "test_")


def _is_allowed(path: Path) -> bool:
    name = path.name.lower()
    return any(k in name for k in ALLOWED_FILE_KEYWORDS)


def _iter_python_sources() -> list[Path]:
    sources: list[Path] = []
    for root in SCAN_DIRS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if _is_allowed(path):
                continue
            sources.append(path)
    return sources


def test_no_prohibited_column_referenced_in_capa1_or_capa2() -> None:
    offenders: list[str] = []
    for src in _iter_python_sources():
        try:
            text = src.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for col in PROHIBITED_FEATURE_COLUMNS:
            if col in text:
                offenders.append(f"{src.relative_to(REPO_ROOT)} → {col!r}")
    if offenders:
        pytest.fail(
            "Principio V violado — columnas prohibidas referenciadas:\n  - "
            + "\n  - ".join(offenders)
            + "\nRevisa data-model.md §'Columnas prohibidas'."
        )


def test_prohibited_columns_list_is_non_empty() -> None:
    assert len(PROHIBITED_FEATURE_COLUMNS) >= 8
