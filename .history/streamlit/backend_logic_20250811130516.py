# backend_logic.py

import os
import shutil
from document_loader import load_documents_from_folder, split_documents
from embedding_store import store_embeddings, get_vectorstore
from qa_chain import get_qa_chain
from retriever import get_all_metadata

UPLOAD_FOLDER = "docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_uploaded_files(uploaded_files):
    filenames = []
    for file in uploaded_files:
        filepath = os.path.join(UPLOAD_FOLDER, file.name)
        with open(filepath, "wb") as f:
            f.write(file.getbuffer())
        filenames.append(file.name)
    return filenames

def process_documents():
    docs = load_documents_from_folder(UPLOAD_FOLDER)
    chunks = split_documents(docs)
    store_embeddings(chunks)

def ask_questions(questions, source_file=None):
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
    return get_all_metadata()

def clear_all_data():
    # Remove files
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    # Clear vectorstore
    db = get_vectorstore()
    db.delete_collection()
