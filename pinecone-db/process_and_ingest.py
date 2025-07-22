from chunking import run_chunking
from pinecone_push import push_to_pinecone

chunks = run_chunking("data/schemes.json")
print(f"🔹 Total Chunks: {len(chunks)}")

push_to_pinecone(chunks)
print("✅ Data pushed to Pinecone with automatic embedding.")
