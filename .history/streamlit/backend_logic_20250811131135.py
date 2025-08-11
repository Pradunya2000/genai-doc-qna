# backend_logic.py
import os
import shutil
import glob
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

UPLOAD_FOLDER = "docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

VECTOR_DB_PATH = "vector_db"

def load_documents_from_folder(folder_path):
    docs = []
    for file in glob.glob(os.path.join(folder_path, "*")):
        if file.lower().endswith(".pdf"):
            docs.extend(PyPDFLoader(file).load())
        elif file.lower().endswith(".txt"):
            docs.extend(TextLoader(file).load())
        elif file.lower().endswith(".docx"):
            docs.extend(Docx2txtLoader(file).load())
    return docs

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)

def store_embeddings(docs):
    embeddings = OpenAIEmbeddings()
    Chroma.from_documents(docs, embeddings, persist_directory=VECTOR_DB_PATH).persist()

def get_vectorstore():
    embeddings = OpenAIEmbeddings()
    return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)

def get_qa_chain(source_file=None):
    retriever = get_vectorstore().as_retriever()
    return RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-4"),
        retriever=retriever
    )

# UI-facing functions
def save_uploaded_files(uploaded_files):
    filenames = []
    for file in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, file.name)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file, f)
        filenames.append(file.name)
    return filenames

def process_documents():
    docs = load_documents_from_folder(UPLOAD_FOLDER)
    chunks = split_documents(docs)
    store_embeddings(chunks)

def ask_questions(questions, source_file=None):
    chain = get_qa_chain(source_file)
    return [{"question": q, "answer": chain.run(q)} for q in questions]

def list_uploaded_files():
    return [{"file": f} for f in os.listdir(UPLOAD_FOLDER)]

def clear_all_data():
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
    shutil.rmtree(VECTOR_DB_PATH, ignore_errors=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
