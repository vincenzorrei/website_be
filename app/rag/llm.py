from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from ..core.settings import settings


def get_llm():
    # If no API key, raise informative error
    if not settings.OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY missing. Set it in the environment to enable LLM answers."
        )

    # GPT-5 only accepts temperature=1 and does NOT support max_tokens.
    # It uses reasoning_effort and max_completion_tokens instead.
    if "gpt-5" in settings.CHAT_MODEL.lower():
        return ChatOpenAI(
            model=settings.CHAT_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=1,
            request_timeout=60,
            reasoning_effort=settings.REASONING_EFFORT,
            max_completion_tokens=settings.MAX_TOKENS,
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
