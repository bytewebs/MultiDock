from pinecone import Pinecone, ServerlessSpec
from embedder import embed_texts
from dotenv import load_dotenv
import os
import time

# ✅ Load environment variables from .env
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# ✅ Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# ✅ Recreate index with correct dimension and region
if pc.has_index(PINECONE_INDEX_NAME):
    print(f"🗑️ Deleting existing index: {PINECONE_INDEX_NAME}")
    pc.delete_index(PINECONE_INDEX_NAME)
    time.sleep(2)

print(f"🛠️ Creating new index: {PINECONE_INDEX_NAME}")
pc.create_index(
    name=PINECONE_INDEX_NAME,
    dimension=384,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")  # ✅ Region hardcoded
)

# ✅ Get index reference
index = pc.Index(PINECONE_INDEX_NAME)

# ✅ Push data in batches
def push_to_pinecone(chunks):
    BATCH_SIZE = 100
    print(f"🔄 Uploading {len(chunks)} chunks in batches of {BATCH_SIZE}...")

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        vectors = embed_texts([c["chunk_text"] for c in batch])

        index.upsert(
            vectors=[
                {
                    "id": c["chunk_id"],
                    "values": v,
                    "metadata": {
                        "chunk_text": c["chunk_text"],
                        "scheme_name": c["scheme_name"],
                        "field": c["field"],
                        "parent_doc_id": c["parent_doc_id"]
                    }
                }
                for c, v in zip(batch, vectors)
            ]
        )

        print(f"✅ Batch {i // BATCH_SIZE + 1} upserted")
        time.sleep(0.3)  # ⏱️ Gentle throttle
