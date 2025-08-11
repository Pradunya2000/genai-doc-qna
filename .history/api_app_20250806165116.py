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



from fastapi.responses import JSONResponse
import os
import shutil
from embedding_store import get_vectorstore

@app.delete("/clear-files/")
async def clear_uploaded_files():
    try:
        # 1. Delete uploaded files
        folder = UPLOAD_FOLDER
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        # 2. Delete all ChromaDB documents safely
        vectorstore = get_vectorstore()
        vectorstore._collection.delete(where={})  # Delete all embeddings

        return JSONResponse(
            status_code=200,
            content={"message": "✅ All uploaded files and embeddings have been cleared."}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"❌ Failed to clear files. Reason: {str(e)}"}
        )
