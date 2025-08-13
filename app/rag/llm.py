from ..core.settings import settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

def get_llm():
    # If no API key, raise informative error
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing. Set it in the environment to enable LLM answers.")
    return ChatOpenAI(model=settings.CHAT_MODEL, temperature=settings.TEMPERATURE)

def get_embeddings():
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing. Set it in the environment to enable embeddings.")
    return OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)
