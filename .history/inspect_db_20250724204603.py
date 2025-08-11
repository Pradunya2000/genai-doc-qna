from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# Using your embedding model
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(persist_directory="chroma_db", embedding_function=embedding)

# Get all stored documents & metadata
results = db.get(include=["documents", "metadatas"])

for i, meta in enumerate(results["metadatas"]):
    print(f"\n🔹 Document Chunk {i+1}:")
    print("🧾 Text:", results["documents"][i][:100], "...")
    print("🗂 Metadata:", meta)
