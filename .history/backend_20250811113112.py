# backend.py

import os
import shutil
from typing import List, Optional
from document_loader import load_documents_from_folder, split_documents
from embedding_store import store_embeddings, get_vectorstore
from qa_chain import get_qa_chain
from retriever import get_all_metadata

UPLOAD_FOLDER = "docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def process_upload_files(uploaded_files):
    uploaded_filenames = []
    for file in uploaded_files:
        file_location = os.path.join(UPLOAD_FOLDER, file.name)
        with open(file_location, "wb") as buffer:
            buffer.write(file.getbuffer())
        uploaded_filenames.append(file.name)

    docs = load_documents_from_folder(UPLOAD_FOLDER)
    chunks = split_documents(docs)
    store_embeddings(chunks)

    return {"message": "✅ Files uploaded and processed successfully.", "files": uploaded_filenames}

def ask_questions_local(questions: List[str], source_file: Optional[str] = None):
    chain = get_qa_chain(source_file)
    responses = []
    for q in questions:
        result = chain({"query": q})
        responses.append({"question": q, "answer": result["result"]})
    return responses

def get_uploaded_files_local():
    return get_all_metadata()

def clear_all_data_local():
    # Delete all files in upload folder
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Clear embeddings from vectorstore
    db = get_vectorstore()
    db.delete_collection()

    return {"message": "🗑️ All files and embeddings cleared successfully."}
