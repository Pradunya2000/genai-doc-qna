# qa_chain.py
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from retriever import get_retriever
from config import A4F_API_KEY, A4F_BASE_URL, LLM_MODEL_NAME

def get_qa_chain(source_file=None):
    retriever = get_retriever(source_file)  # ✅ apply file filter
    llm = ChatOpenAI(
        openai_api_key=A4F_API_KEY,
        openai_api_base=A4F_BASE_URL,
        model_name=LLM_MODEL_NAME,
        temperature=0
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="map_reduce",
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain
