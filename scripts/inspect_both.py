import sys
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

REPO_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = REPO_ROOT / "artifacts" / "rag" / "chroma"
COLLECTION_NAME = "normativa_cyl_v010"
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

print("Chroma Dir:", CHROMA_DIR)
client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_collection(COLLECTION_NAME)
print("Collection Count:", collection.count())

embedder = SentenceTransformer(EMBED_MODEL)
query = "fuga química camión cisterna"
vec = embedder.encode([query]).tolist()
results = collection.query(query_embeddings=vec, n_results=5, include=["metadatas", "documents", "distances"])

print("Query:", query)
print("Vector slice:", vec[0][:5])
try:
    import numpy as np
    
    # Run query for all results
    all_results = collection.query(query_embeddings=vec, n_results=collection.count(), include=["metadatas", "documents", "distances"])
    ids = all_results["ids"][0]
    distances = all_results["distances"][0]
    
    target_id = "PLANCAL_DEC_4_2019_chemical_leakage"
    if target_id in ids:
        rank = ids.index(target_id)
        print(f"\n[DEBUG] Found {target_id} in query results!")
        print(f"Rank: {rank + 1}")
        print(f"Distance in query results: {distances[rank]}")
    else:
        print(f"\n[DEBUG] {target_id} NOT found in query results at all!")
        
    doc_by_id = collection.get(ids=[target_id], include=["embeddings", "documents"])
    if len(doc_by_id["ids"]) > 0:
        db_vec = np.array(doc_by_id["embeddings"][0])
        q_vec = np.array(vec[0])
        # Compute cosine distance: 1 - cosine_similarity
        cos_sim = np.dot(db_vec, q_vec) / (np.linalg.norm(db_vec) * np.linalg.norm(q_vec))
        print(f"Cosine distance computed manually: {1.0 - cos_sim}")
    else:
        print(f"{target_id} not found in database by ID.")
except Exception as e:
    print("Error calculating rank and distance:", e)

for i in range(min(5, len(results["ids"][0]))):
    print(f"Match {i+1}: ID={results['ids'][0][i]}, Distance={results['distances'][0][i]}, Metadata={results['metadatas'][0][i]}")
