import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = REPO_ROOT / "artifacts" / "rag" / "chroma"
COLLECTION_NAME = "normativa_cyl_v010"
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_collection(COLLECTION_NAME)
embedder = SentenceTransformer(EMBED_MODEL)

query = "fuga química camión cisterna"
vec = embedder.encode([query]).tolist()
results = collection.query(query_embeddings=vec, n_results=5, include=["metadatas", "documents", "distances"])

print("=== TOP 5 RAG RESULTS ===")
for i in range(len(results["documents"][0])):
    print(f"[{i+1}] Distance: {results['distances'][0][i]:.4f}")
    print(f"    Norma ID: {results['metadatas'][0][i]['norma_id']}")
    print(f"    Articulo: {results['metadatas'][0][i].get('articulo')}")
    print(f"    Doc Snippet: {results['documents'][0][i][:200]}")
    print("-" * 50)
