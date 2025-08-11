# api_app.py

from fastapi import FastAPI, UploadFile, File, Query
from pydantic import BaseModel
from document_loader import load_documents_from_folder, split_documents
from embedding_store import store_embeddings
from qa_chain import get_qa_chain
import os
import shutil
from typing import List, Optional
from retriever import get_all_metadata

app = FastAPI(title="Private PDF Q&A API")

UPLOAD_FOLDER = "docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Request model: Always expect a list of questions (1 or many)
class QuestionRequest(BaseModel):
    questions: List[str]

# ✅ Upload Endpoint — Multiple Files
@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    uploaded_filenames = []

    for file in files:
        file_location = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_filenames.append(file.filename)

    # Ingest documents
    docs = load_documents_from_folder(UPLOAD_FOLDER)
    chunks = split_documents(docs)
    store_embeddings(chunks)

    return {
        "message": "✅ Files uploaded and processed successfully.",
        "files": uploaded_filenames
    }

# ✅ Unified Question Endpoint (1 or many questions) with optional file filter
@app.post("/ask/")
async def ask_questions(req: QuestionRequest, source_file: Optional[str] = Query(None)):
    chain = get_qa_chain(source_file)
    responses = []

    for q in req.questions:
        result = chain({"query": q})
        responses.append({
            "question": q,
            "answer": result["result"]
        })

    return {"responses": responses}


@app.get("/files/")
async def list_uploaded_files():
    return get_all_metadata()

