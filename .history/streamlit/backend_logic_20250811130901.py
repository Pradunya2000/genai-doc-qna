# backend_logic.py

import os
import shutil
from dotenv import load_dotenv
from typing import List, Optional

from document_loader import load_documents_from_folder, split_documents
from embedding_store import store_embeddings, get_vectorstore
from qa_chain import get_qa_chain
from retriever import get_all_metadata

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE", "https://api.a4f.co/v1")

# Folder to store uploaded documents
UPLOAD_FOLDER = "docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_uploaded_files(uploaded_files) -> List[str]:
    """
    Save uploaded files (Streamlit's file_uploader output) to UPLOAD_FOLDER.
    """
    filenames = []
    for file in uploaded_files:
        filepath = os.path.join(UPLOAD_FOLDER, file.name)
        with open(filepath, "wb") as f:
            f.write(file.getbuffer())
        filenames.append(file.name)
    return filenames


def process_documents():
    """
    Load, split, and store embeddings for all documents in UPLOAD_FOLDER.
    """
    docs = load_documents_from_folder(UPLOAD_FOLDER)
    chunks = split_documents(docs)
    store_embeddings(chunks)


def ask_questions(questions: List[str], source_file: Optional[str] = None):
    """
    Run Q&A on uploaded documents.
    """
    chain = get_qa_chain(source_file)
    results = []
    for q in questions:
        res = chain({"query": q})
        results.append({
            "question": q,
            "answer": res["result"],
            "sources": [doc.metadata.get("source") for doc in res.get("source_documents", [])]
        })
    return results


def list_uploaded_files():
    """
    Get metadata of all uploaded documents.
    """
    return get_all_metadata()


def clear_all_data():
    """
    Remove all uploaded documents and clear embeddings.
    """
    # Delete local docs
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Delete embeddings
    db = get_vectorstore()
    db.delete_collection()
