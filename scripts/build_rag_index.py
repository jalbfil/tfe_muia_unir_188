"""T062 — Construye el índice ChromaDB desde el corpus normativo CyL v0.1.0.

Uso:
    python scripts/build_rag_index.py                 # construye / actualiza
    python scripts/build_rag_index.py --reset         # borra y reconstruye
    python scripts/build_rag_index.py --dry-run       # cuenta chunks sin indexar

Dependencias:
    pip install pdfplumber sentence-transformers chromadb pyyaml

Salida:
    artifacts/rag/chroma/   (ChromaDB persistido en disco)

Colección: normativa_cyl_v010
Modelo:    paraphrase-multilingual-MiniLM-L12-v2
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# ─────────── rutas ───────────

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "resources" / "corpus_normativo" / "manifest.yaml"
CHROMA_DIR = REPO_ROOT / "artifacts" / "rag" / "chroma"
COLLECTION_NAME = "normativa_cyl_v010"
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# Añadir src/ al path para importar capa3_llm_mcp sin instalación editable
sys.path.insert(0, str(REPO_ROOT / "src"))


# ─────────── helpers ───────────

def _load_embedder():
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "sentence-transformers no instalado. Ejecuta: pip install sentence-transformers"
        ) from exc
    print(f"  Cargando modelo {EMBED_MODEL} …")
    return SentenceTransformer(EMBED_MODEL)


def _get_collection(*, reset: bool = False):
    try:
        import chromadb  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "chromadb no instalado. Ejecuta: pip install chromadb"
        ) from exc

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"  [reset] Colección '{COLLECTION_NAME}' eliminada.")
        except Exception:
            pass  # La colección no existía todavía

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


# ─────────── main ───────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="T062 — Construye el índice RAG del corpus normativo CyL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Borra la colección existente y la reconstruye desde cero.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Cuenta chunks disponibles sin indexar nada.",
    )
    args = parser.parse_args()

    from capa3_llm_mcp.rag.ingestion import chunk_pdf, iter_corpus  # type: ignore[import]

    if not MANIFEST.exists():
        print(f"ERROR: manifest no encontrado en {MANIFEST}", file=sys.stderr)
        return 1

    # ── dry-run ──────────────────────────────────────────────────
    if args.dry_run:
        total = 0
        print(f"\nDry-run — corpus en: {MANIFEST.parent}\n")
        for pdf_path, meta in iter_corpus(MANIFEST):
            n = len(chunk_pdf(pdf_path, meta))
            print(f"  {meta['norma_id']:35s}  {n:4d} chunks")
            total += n
        print(f"\n  TOTAL: {total} chunks  (modelo: {EMBED_MODEL})")
        return 0

    # ── indexación real ───────────────────────────────────────────
    embedder = _load_embedder()
    collection = _get_collection(reset=args.reset)

    added = 0
    skipped = 0

    for pdf_path, meta in iter_corpus(MANIFEST):
        nid: str = meta["norma_id"]

        # Comprobar qué chunks ya están indexados para esta norma
        existing = set(collection.get(where={"norma_id": nid})["ids"])
        chunks = chunk_pdf(pdf_path, meta)
        new_chunks = [c for c in chunks if c["id"] not in existing]

        if not new_chunks:
            print(f"  [skip]  {nid:35s}  ya indexado ({len(chunks)} chunks)")
            skipped += len(chunks)
            continue

        texts = [c["text"] for c in new_chunks]
        embeddings = embedder.encode(texts, batch_size=32, show_progress_bar=False).tolist()

        collection.add(
            ids=[c["id"] for c in new_chunks],
            documents=texts,
            embeddings=embeddings,
            metadatas=[c["metadata"] for c in new_chunks],
        )
        print(f"  [ok]    {nid:35s}  +{len(new_chunks)} chunks indexados")
        added += len(new_chunks)

    total_in_collection = collection.count()
    print(
        f"\n  Añadidos: {added}  |  Omitidos: {skipped}  |"
        f"  Total en '{COLLECTION_NAME}': {total_in_collection}"
    )
    print(f"  Índice guardado en: {CHROMA_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
