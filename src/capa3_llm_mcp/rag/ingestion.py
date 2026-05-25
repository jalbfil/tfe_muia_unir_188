"""T061 — Ingesta de PDFs normativos: parse → chunk → metadata.

Uso típico (desde build_rag_index.py):

    from capa3_llm_mcp.rag.ingestion import chunk_pdf, iter_corpus

Dependencias:
    pip install pdfplumber pyyaml

Parámetros de chunking:
    _WORDS_PER_CHUNK ≈ 350 palabras  → ≈ 400 tokens con el modelo MiniLM-L12-v2
    _WORDS_OVERLAP   ≈ 50  palabras  → ventana deslizante con solapamiento
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Generator

import yaml  # pyyaml

# ─────────── constantes ───────────

_WORDS_PER_CHUNK = 350   # ≈ 400 tokens a ~1.15 tok/word
_WORDS_OVERLAP = 50

# Detecta "Artículo 1", "Artículo 1.", "Art. 1", "ARTÍCULO 1", "Artículo único"
_ARTICULO_RE = re.compile(
    r'\b(?:Artículo|ARTÍCULO|Art\.)\s+(\d+|[Úú]nico)',
    re.IGNORECASE,
)


# ─────────── extracción PDF ───────────

def _extract_text(pdf_path: Path) -> str:
    """Extrae texto completo del PDF con pdfplumber, página a página."""
    try:
        import pdfplumber  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "pdfplumber no instalado. Ejecuta: pip install pdfplumber"
        ) from exc

    pages: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n".join(pages)


# ─────────── chunking ───────────

def _sliding_chunks(
    words: list[str], size: int, overlap: int
) -> Generator[list[str], None, None]:
    """Ventana deslizante sobre lista de palabras con solapamiento."""
    step = max(1, size - overlap)
    start = 0
    while start < len(words):
        yield words[start : start + size]
        if start + size >= len(words):
            break
        start += step


def _last_article_in(text: str, previous: str) -> str:
    """Devuelve el último artículo mencionado en el texto, o el anterior si no hay."""
    matches = _ARTICULO_RE.findall(text)
    return f"art.{matches[-1]}" if matches else previous


# ─────────── API pública ───────────

def chunk_pdf(pdf_path: Path, norma_meta: dict) -> list[dict]:
    """Parsea un PDF y devuelve chunks listos para ChromaDB.

    Args:
        pdf_path:    Ruta absoluta al PDF.
        norma_meta:  Entrada del manifest.yaml (con norma_id, ano, jerarquia…).

    Returns:
        Lista de {"id": str, "text": str, "metadata": dict}.
        Lista vacía si el PDF no contiene texto extraíble.
    """
    raw = _extract_text(pdf_path)
    if not raw.strip():
        return []

    words = raw.split()
    chunks: list[dict] = []
    last_art = "preambulo"

    for i, word_list in enumerate(
        _sliding_chunks(words, _WORDS_PER_CHUNK, _WORDS_OVERLAP)
    ):
        text = " ".join(word_list)
        last_art = _last_article_in(text, last_art)
        chunks.append(
            {
                "id": f"{norma_meta['norma_id']}_{i:04d}",
                "text": text,
                "metadata": {
                    "norma_id": norma_meta["norma_id"],
                    "articulo": last_art,
                    "año": str(norma_meta.get("ano", "")),
                    "jerarquia": norma_meta.get("jerarquia", ""),
                    "chunk_index": i,
                },
            }
        )
    return chunks


def iter_corpus(
    manifest_path: Path,
) -> Generator[tuple[Path, dict], None, None]:
    """Itera sobre todas las normas activas del manifest que tienen PDF descargado.

    Omite las normas marcadas en ``defer_to_v020`` y las que no tienen PDF.

    Yields:
        (pdf_path, norma_meta)  para cada norma disponible.
    """
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    deferred: set[str] = set(manifest.get("defer_to_v020", []))
    corpus_dir = manifest_path.parent

    for norma in manifest["normas"]:
        nid: str = norma["norma_id"]
        if nid in deferred:
            continue
        pdf_path = corpus_dir / nid / f"{nid}.pdf"
        if not pdf_path.exists():
            continue
        yield pdf_path, norma
