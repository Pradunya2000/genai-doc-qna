# retriever.py

from langchain.vectorstores import Chroma
from embedding_store import get_embedding_function
from config import CHROMA_DB_DIR, COLLECTION_NAME

# ✅ Used by the Q&A chain with optional file filtering
def get_retriever(source_file: str = None):
    db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        persist_directory=CHROMA_DB_DIR
    )

    # ✅ If a file is specified, apply metadata filter
    if source_file:
        search_kwargs = {
            "k": 8,
            "filter": {"source": source_file}
        }
    else:
        search_kwargs = {"k": 8}

    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs=search_kwargs
    )
    return retriever

# ✅ Used by /files/ endpoint to show metadata of uploaded files
def get_all_metadata():
    db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        persist_directory=CHROMA_DB_DIR
    )
    
    results = db.get(include=["metadatas"])
    
    files = {}
    for metadata in results["metadatas"]:
        file = metadata.get("source", "Unknown")
        date = metadata.get("upload_date", "Unknown")
        files[file] = date

    return [{"file": f, "upload_date": d} for f, d in files.items()]
