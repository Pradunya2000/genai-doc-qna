# config.py

import os
from dotenv import load_dotenv

# load local .env in development (pip install python-dotenv)
load_dotenv()

A4F_API_KEY = os.getenv("A4F_API_KEY", "")
A4F_BASE_URL = os.getenv("A4F_BASE_URL", "https://api.a4f.co/v1")

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "provider-3/gpt-4o-mini")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "provider-2/text-embedding-3-small")

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "pdf_documents")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
