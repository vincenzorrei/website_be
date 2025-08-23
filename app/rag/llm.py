from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from ..core.settings import settings


def get_llm():
    # If no API key, raise informative error
    if not settings.OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY missing. Set it in the environment to enable LLM answers."
        )

    # Gestione speciale per GPT-5
    if "gpt-5" in settings.CHAT_MODEL.lower():
        return ChatOpenAI(
            model=settings.CHAT_MODEL,
            api_key=settings.OPENAI_API_KEY,
            max_tokens=settings.MAX_TOKENS,
            temperature=1.0,  # Forziamo 1.0 come richiesto da GPT-5
        )
    else:
        return ChatOpenAI(
            model=settings.CHAT_MODEL,
            temperature=settings.TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
            max_tokens=settings.MAX_TOKENS,
        )


def get_embeddings():
    if not settings.OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY missing. Set it in the environment to enable embeddings."
        )
    return OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)
