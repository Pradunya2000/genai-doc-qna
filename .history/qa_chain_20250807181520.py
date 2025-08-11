# qa_chain.py

from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

from retriever import get_retriever
from config import A4F_API_KEY, A4F_BASE_URL, LLM_MODEL_NAME


from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from retriever import get_retriever
from config import A4F_API_KEY, A4F_BASE_URL, LLM_MODEL_NAME

from langchain.vectorstores import Chroma
from embedding_store import get_embedding_function
from config import CHROMA_DB_DIR, COLLECTION_NAME

def get_retriever(source_file=None):
    embedding_function = get_embedding_function()
    db = Chroma(
        persist_directory=CHROMA_DB_DIR,
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )

    # ✅ Only apply filter if source_file is provided
    if source_file:
        retriever = db.as_retriever(
            search_kwargs={"filter": {"source": source_file}}
        )
    else:
        retriever = db.as_retriever()

    return retriever

