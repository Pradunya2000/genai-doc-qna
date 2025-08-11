# api_app.py

import os
from dotenv import load_dotenv

load_dotenv()  # loads .env into environment variables

# Ensure OpenAI-compatible env vars exist for LangChain
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE", "https://api.a4f.co/v1")


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
    print(f"🔍 File filter applied: {source_file}")
    chain = get_qa_chain(source_file)
    responses = []

    for q in req.questions:
        result = chain({"query": q})
        answer_text = result["result"].strip().lower()

        # ✅ Fallback if model says it doesn't know
        if answer_text in ["i don't know", "i dont know", "unknown", "not sure", ""]:
            print("⚠️ Detected vague/empty answer, generating summary fallback...")
            
            # Get all docs from retriever and make a manual summary
            retriever = chain.retriever
            docs = retriever.get_relevant_documents(q)
            combined_text = "\n".join([doc.page_content for doc in docs])

            # Simple summarization using same model (single call)
            from langchain.prompts import PromptTemplate
            from langchain.chains import LLMChain
            from langchain.chat_models import ChatOpenAI

            llm = ChatOpenAI(
                openai_api_key=A4F_API_KEY,
                openai_api_base=A4F_BASE_URL,
                model_name=LLM_MODEL_NAME,
                temperature=0
            )

            summary_prompt = PromptTemplate(
                input_variables=["text"],
                template="Summarize the following document content briefly:\n\n{text}"
            )
            summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
            answer_text = summary_chain.run(combined_text)

        responses.append({
            "question": q,
            "answer": answer_text
        })

    return {"responses": responses}


@app.get("/files/")
async def list_uploaded_files():
    return get_all_metadata()


# We have added a clear endpoint to delete all files and embeddings on 06/08/2025
from embedding_store import get_vectorstore

@app.delete("/clear/")
async def clear_all_uploaded_files():
    # 1. Delete all files from docs/
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # 2. Delete all embeddings from vectorstore (by recreating empty one)
    db = get_vectorstore()
    db.delete_collection()  # Fully clears the collection

    return {"message": "🗑️ All files and embeddings cleared successfully."}


