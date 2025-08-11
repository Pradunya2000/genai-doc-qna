#model.py
from langchain.chat_models import ChatOpenAI
from config import A4F_API_KEY, A4F_BASE_URL, LLM_MODEL_NAME

# Initialize the LLM object with your a4f API
llm = ChatOpenAI(
    openai_api_key=A4F_API_KEY,
    openai_api_base=A4F_BASE_URL,
    model_name=LLM_MODEL_NAME,
    temperature=0
)

# Test it
response = llm.invoke("Hello! How are you?")
print(response.content)
