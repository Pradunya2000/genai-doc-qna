# document_loader.py

import os
from langchain.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from datetime import datetime
from config import CHUNK_SIZE, CHUNK_OVERLAP

def load_documents_from_folder(folder_path, metadata=None):
    all_documents = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if file_name.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_name.lower().endswith(".txt"):
            loader = TextLoader(file_path)
        elif file_name.lower().endswith((".docx", ".doc")):
            loader = UnstructuredWordDocumentLoader(file_path)
        else:
            continue  # Skip unsupported files

        documents = loader.load()
        for doc in documents:
            doc.metadata["source"] = file_name
            if metadata:
                doc.metadata.update(metadata)
            doc.metadata["upload_date"] = str(datetime.now())  # Auto-timestamp

        all_documents.extend(documents)

    return all_documents

from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return text_splitter.split_documents(documents)
