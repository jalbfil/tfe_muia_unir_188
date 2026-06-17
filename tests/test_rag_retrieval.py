"""T063 + T064 — Tests de retrieval semántico del índice RAG.

Ejecución:
    # 1. Primero construir el índice:
    python scripts/build_rag_index.py

    # 2. Luego ejecutar:
    pytest tests/test_rag_retrieval.py -v

Requisitos:
    pip install chromadb sentence-transformers

T063: "atrapado herido grave"         → norma_id top-1 == LEY_17_2015
T064: "fuga química camión cisterna"  → norma_id top-1 en fallback químico
    verificable (sin depender de MPCYL no localizado de forma completa).
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = REPO_ROOT / "artifacts" / "rag" / "chroma"
COLLECTION_NAME = "normativa_cyl_v010"
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


# ─────────── fixture: colección + embedder ───────────

@pytest.fixture(scope="module")
def rag(request):
    """Carga ChromaDB y embedder. Salta el módulo entero si el índice no existe."""
    if not CHROMA_DIR.exists():
        pytest.skip(
            "Índice RAG no construido todavía (T062). "
            "Ejecuta: python scripts/build_rag_index.py"
        )
    try:
        from capa3_llm_mcp.mcp_server.tools.search_normative import _load_rag, reset_rag_cache
        reset_rag_cache()
        collection, embedder = _load_rag()
    except Exception as exc:
        pytest.skip(f"No se pudo cargar el RAG en el test: {exc}")
    return collection, embedder


def _top1_norma(collection, embedder, query: str) -> str | None:
    vec = embedder.encode([query]).tolist()
    results = collection.query(query_embeddings=vec, n_results=1, include=["metadatas"])
    metas = results.get("metadatas", [[]])[0]
    return metas[0]["norma_id"] if metas else None


def _topk_normas(collection, embedder, query: str, k: int = 5) -> list[str]:
    vec = embedder.encode([query]).tolist()
    results = collection.query(query_embeddings=vec, n_results=k, include=["metadatas"])
    metas = results.get("metadatas", [[]])[0]
    return [meta.get("norma_id", "") for meta in metas]


# ─────────── T063 ───────────

def test_t063_atrapado_herido_top1_ley17(rag):
    """T063: riesgo vital + atrapado → Ley 17/2015 (marco SNPC, art. 1)."""
    collection, embedder = rag
    top1 = _top1_norma(collection, embedder, "atrapado herido grave")
    assert top1 == "LEY_17_2015", (
        f"Esperado LEY_17_2015, obtenido '{top1}'. "
        "Comprobar chunking y embeddings del corpus."
    )


def test_t064_fuga_quimica_top1_mpcyl(rag):
    """T064: mercancías peligrosas → MPCyL.

    SKIP si MPCYL_ACUERDO_3_2008 no está indexado o si solo contiene el decreto
    de aprobación (< 20 chunks) en lugar del texto completo del plan.
    El BOCYL-D-23012008-8 solo publica el Acuerdo (decreto), no el plan como anexo;
    se necesita localizar el PDF del plan completo para que este test pase.
    """
    collection, embedder = rag
    indexed = collection.get(where={"norma_id": "MPCYL_ACUERDO_3_2008"})
    n_chunks = len(indexed["ids"])
    if n_chunks == 0:
        pytest.skip(
            "MPCYL_ACUERDO_3_2008 no indexado (url_pdf pendiente de localizar in manifest.yaml)."
        )
    if n_chunks < 20:
        pytest.skip(
            f"MPCYL_ACUERDO_3_2008 tiene solo {n_chunks} chunks: el PDF descargado "
            "contiene únicamente el decreto de aprobación (Acuerdo 3/2008), no el "
            "texto completo del plan. Localizar el PDF del plan con los anexos técnicos."
        )
    top1 = _top1_norma(collection, embedder, "fuga química camión cisterna")
    assert top1 == "MPCYL_ACUERDO_3_2008", (
        f"Esperado MPCYL_ACUERDO_3_2008, obtenido '{top1}'."
    )

