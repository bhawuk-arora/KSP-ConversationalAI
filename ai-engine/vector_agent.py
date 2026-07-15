# ai-engine/vector_agent.py
import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient

# Qdrant credentials
QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
COLLECTION_NAME = "ksp_fir_briefs"

def search_vector_briefs(query_text: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Vectorizes query and searches Qdrant COLLECTION_NAME for matching FIR briefs.
    Falls back to empty list on connection failures.
    """
    try:
        from sentence_transformers import SentenceTransformer
        # Load local lightweight model
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_vector = model.encode(query_text).tolist()
    except Exception as e:
        print(f"[VECTOR WARNING] Could not import/initialize SentenceTransformer: {e}")
        return []

    try:
        q_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=2.0)
        
        # Check if collection exists before querying
        collections = q_client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)
        
        if not exists:
            print(f"[VECTOR WARNING] Qdrant collection '{COLLECTION_NAME}' does not exist.")
            return []
            
        search_result = q_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit
        )
        
        results = []
        for hit in search_result:
            results.append({
                "case_master_id": hit.payload.get("case_master_id"),
                "crime_no": hit.payload.get("crime_no"),
                "brief_facts": hit.payload.get("brief_facts"),
                "score": hit.score
            })
        return results
        
    except Exception as e:
        print(f"[VECTOR WARNING] Qdrant connection/query failed: {e}")
        return []
