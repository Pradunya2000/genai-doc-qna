# embedding_store.py

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from config import (
    A4F_API_KEY, A4F_BASE_URL, EMBEDDING_MODEL_NAME, 
    CHROMA_DB_DIR, COLLECTION_NAME
)

# ✅ Step 1: Create embedding function
def get_embedding_function():
    return OpenAIEmbeddings(
        openai_api_key=A4F_API_KEY,
        openai_api_base=A4F_BASE_URL,
        model=EMBEDDING_MODEL_NAME
    )

# ✅ Step 2: Store new documents into Chroma DB
from datetime import datetime
import os

def store_embeddings(documents, filename=None):
    embedding_function = get_embedding_function()
    db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_function,
        persist_directory=CHROMA_DB_DIR
    )

    # ✅ Attach metadata to each document chunk
    if filename:
        for doc in documents:
            doc.metadata["source"] = filename
            doc.metadata["upload_date"] = datetime.now().strftime("%Y-%m-%d")
            print(f"📦 Metadata for doc: {doc.metadata}")
            
    db.add_documents(documents)
    db.persist()
    return db


# ✅ Step 3: Get existing vectorstore for querying/filtering
def get_vectorstore():
    embedding_function = get_embedding_function()
    db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_function,
        persist_directory=CHROMA_DB_DIR
    )
    return db
