# KSP Crime Intelligence Platform - Qdrant Vector Indexing Pipeline
# Vectorizes CaseMaster facts and populates Qdrant collection

import os
import sys
import psycopg2
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# Database credentials
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_NAME = os.environ.get("DB_NAME", "ksp_db")

# Qdrant credentials
QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))

COLLECTION_NAME = "ksp_fir_briefs"
EMBEDDING_DIM = 384  # Matches sentence-transformers 'all-MiniLM-L6-v2' dimensions

def index_case_facts():
    print("Initializing SentenceTransformer local embeddings model...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
    except ImportError:
        print("[ERROR] sentence-transformers package not installed. Run pip install sentence-transformers.")
        sys.exit(1)
        
    print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
    try:
        q_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    except Exception as e:
        print(f"[ERROR] Could not connect to Qdrant: {e}")
        sys.exit(1)
        
    # Recreate Qdrant Collection
    print(f"Checking/Recreating Qdrant collection '{COLLECTION_NAME}'...")
    try:
        q_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )
    except Exception as e:
        print(f"[ERROR] Failed to setup Qdrant collection: {e}")
        sys.exit(1)

    print(f"Connecting to PostgreSQL database '{DB_NAME}'...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cursor = conn.cursor()
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        sys.exit(1)

    print("Fetching CaseMaster facts...")
    cursor.execute("SELECT CaseMasterID, CrimeNo, BriefFacts, CrimeMajorHeadID, CrimeRegisteredDate FROM CaseMaster WHERE BriefFacts IS NOT NULL;")
    cases = cursor.fetchall()
    print(f"Found {len(cases)} cases to vectorize.")

    points = []
    batch_size = 100
    
    for idx, (case_id, crime_no, facts, major_head_id, reg_date) in enumerate(cases):
        if not facts.strip():
            continue
            
        # Generate embedding vector locally
        vector = model.encode(facts).tolist()
        
        # Prepare point structure
        points.append(
            PointStruct(
                id=case_id,
                vector=vector,
                payload={
                    "case_master_id": case_id,
                    "crime_no": crime_no,
                    "major_head_id": major_head_id,
                    "registered_date": str(reg_date),
                    "brief_facts": facts
                }
            )
        )
        
        # Upload in batches
        if len(points) >= batch_size:
            q_client.upsert(collection_name=COLLECTION_NAME, points=points)
            print(f"  -> Uploaded batch of {len(points)} vectors (Progress: {idx+1}/{len(cases)})...")
            points = []
            
    # Upload any trailing points
    if points:
        q_client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"  -> Uploaded trailing batch of {len(points)} vectors.")
        
    print(f"[SUCCESS] Successfully indexed {len(cases)} case briefs in Qdrant.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    index_case_facts()
