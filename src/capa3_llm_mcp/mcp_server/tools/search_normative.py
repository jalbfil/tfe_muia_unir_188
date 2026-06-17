"""T075 — Tool `search_normative`: búsqueda semántica en corpus normativo CyL.

Entrada:  query (str), n (int, por defecto 5)
Salida:   lista de chunks con texto + metadata {norma_id, articulo, año, jerarquia}

Usa el índice ChromaDB construido por scripts/build_rag_index.py.
Si el índice no existe, devuelve lista vacía (no falla — modo degradado soportado).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[4]
_CHROMA_DIR = REPO_ROOT / "artifacts" / "rag" / "chroma"
_COLLECTION = "normativa_cyl_v010"
_EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# Caché module-level para no recargar en cada llamada
_collection: Any = None
_embedder: Any = None


def _load_rag() -> tuple[Any, Any]:
    """Carga ChromaDB + embedder (lazy, cacheado)."""
    global _collection, _embedder  # noqa: PLW0603

    if _collection is not None and _embedder is not None:
        return _collection, _embedder

    try:
        import chromadb  # type: ignore[import-untyped]
        from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError("pip install chromadb sentence-transformers") from exc

    if not _CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"Índice RAG no encontrado: {_CHROMA_DIR}\n"
            "Ejecuta: python scripts/build_rag_index.py"
        )

    client = chromadb.PersistentClient(path=str(_CHROMA_DIR))
    _collection = client.get_collection(_COLLECTION)
    _embedder = SentenceTransformer(_EMBED_MODEL)
    return _collection, _embedder


def search_normative(query: str, n: int = 5) -> list[dict]:
    """Busca fragmentos del corpus normativo CyL relevantes para `query`.

    Args:
        query:  Texto en español (descripción del incidente o pregunta normativa).
        n:      Número de fragmentos a devolver (1–20).

    Returns:
        Lista de dicts con keys: ``norma_id``, ``articulo``, ``año``,
        ``jerarquia``, ``chunk_index``, ``excerpt``, ``text``, ``score``.
        ``excerpt`` es un fragmento limpio y recortado, citable para el operador;
        ``text`` es el chunk completo ya saneado de ruido de maquetación.
        Lista vacía si el índice no está disponible.
    """
    n = max(1, min(n, 20))

    try:
        collection, embedder = _load_rag()
    except (FileNotFoundError, ImportError):
        return []

    # El RAG es complementario: si el embedding o ChromaDB fallan (p. ej. por
    # incompatibilidad de versiones de sentence-transformers/chromadb), se
    # degrada SOLO el RAG devolviendo [], sin arrastrar la explicación LLM
    # completa a modo degradado.
    try:
        vec = embedder.encode([query]).tolist()
        results = collection.query(
            query_embeddings=vec,
            n_results=n,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("RAG no disponible (search_normative degradado): %s", exc)
        return []

    try:
        from capa3_llm_mcp.rag.ingestion import citable_excerpt, clean_normative_text
    except ImportError:  # pragma: no cover - fallback if ingestion unavailable
        def clean_normative_text(text: str) -> str:  # type: ignore[misc]
            return text

        def citable_excerpt(text: str, max_chars: int = 280) -> str:  # type: ignore[misc]
            return text[:max_chars]

    chunks: list[dict] = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, distances, strict=False):
        clean_text = clean_normative_text(doc)
        chunks.append(
            {
                "norma_id": meta.get("norma_id", ""),
                "articulo": meta.get("articulo", ""),
                "año": meta.get("año", ""),
                "jerarquia": meta.get("jerarquia", ""),
                "chunk_index": meta.get("chunk_index", 0),
                "excerpt": citable_excerpt(clean_text),
                "text": clean_text,
                "score": round(1.0 - dist, 4),  # cosine similarity
            }
        )
    return chunks


def reset_rag_cache() -> None:
    """Restablece la caché global de la colección y embedder (crucial para evitar corrupción de hilos en tests)."""
    global _collection, _embedder  # noqa: PLW0603
    _collection = None
    _embedder = None
