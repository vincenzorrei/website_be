# app/rag/chains.py
import asyncio
import logging
import time

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .llm import get_llm
from .memory import append_turn, get_history
from .prompts import SYSTEM_PROMPT
from .retriever import build_retriever

logger = logging.getLogger(__name__)

# Minimum relevance score to consider a document useful
_RELEVANCE_THRESHOLD = 0.25


def _check_relevance(docs) -> list:
    """Filter docs by relevance score when available."""
    if not docs:
        return []
    relevant = []
    for d in docs:
        score = d.metadata.get("relevance_score")
        if score is not None and score < _RELEVANCE_THRESHOLD:
            continue
        relevant.append(d)
    return relevant


def _build_context_and_history(
    question: str, tenant_id: str, session_id: str, filters: dict | None
):
    """Recupera docs e history e costruisce il prompt con messaggi separati."""
    retriever = build_retriever(tenant_id, filters)
    try:
        docs = retriever.invoke(question)
    except Exception:
        docs = []

    # Apply relevance filtering
    relevant_docs = _check_relevance(docs) if docs else []

    # Build context string
    if relevant_docs:
        context = "\n\n".join(d.page_content for d in relevant_docs[:4])
    else:
        context = (
            "[NO RELEVANT CONTEXT FOUND] "
            "The knowledge base did not return useful information for this query. "
            "Answer based on your general expertise, and be transparent about it."
        )

    # Build message list with proper separation
    messages = []

    # 1. System prompt
    messages.append(SystemMessage(content=SYSTEM_PROMPT))

    # 2. RAG context as a dedicated system message
    messages.append(
        SystemMessage(
            content=(
                "Retrieved context from the knowledge base "
                "(use this to ground your answer):\n\n"
                f"{context}"
            )
        )
    )

    # 3. Conversation history as separate HumanMessage/AIMessage
    history = get_history(tenant_id, session_id)
    for role, content in history:
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    # 4. Current user question
    messages.append(HumanMessage(content=question))

    # Map sources
    source_docs = relevant_docs[:4] if relevant_docs else docs[:4]
    sources = [
        {
            "source_id": d.metadata.get("source_id", ""),
            "title": d.metadata.get("title", ""),
        }
        for d in source_docs
    ]
    return messages, sources


def answer_question(
    question: str,
    tenant_id: str = "default",
    session_id: str = "default",
    filters: dict | None = None,
):
    """
    Ritorna (answer, sources). Se manca OPENAI_API_KEY, restituisce un placeholder.
    """
    try:
        llm = get_llm()
    except Exception:
        # Placeholder utile per validare l'integrazione
        return (
            "Backend ready. Configure OPENAI_API_KEY to enable AI answers. Your question was: "
            + question,
            [],
        )

    messages, sources = _build_context_and_history(
        question, tenant_id, session_id, filters
    )
    resp = llm.invoke(messages)

    # Aggiorna memoria di sessione
    try:
        append_turn(tenant_id, session_id, "user", question)
        append_turn(tenant_id, session_id, "assistant", resp.content)
    except Exception:
        pass

    return resp.content, sources


async def stream_answer(
    question: str,
    tenant_id: str = "default",
    session_id: str = "default",
    filters: dict | None = None,
):
    """
    Streamma l'answer pezzo per pezzo via SSE. Emette frame 'data: <chunk>\\n\\n' e chiude con 'event: end'.
    """
    # LLM (LangChain OpenAI)
    llm = get_llm()

    messages, sources = _build_context_and_history(
        question, tenant_id, session_id, filters
    )

    # Invia heartbeat iniziale
    yield ": heartbeat\n\n"

    # Crea il task per lo streaming
    llm_task = asyncio.create_task(collect_stream_data(llm, messages))

    # Invia heartbeat ogni 10 secondi finché non arrivano dati
    last_heartbeat = time.time()
    full_answer_parts = []

    while not llm_task.done():
        try:
            # Aspetta i dati per max 1 secondo
            result = await asyncio.wait_for(llm_task, timeout=1.0)
            # Se arriviamo qui, abbiamo i dati
            for part in result:
                full_answer_parts.append(part)
                yield f"data: {part}\n\n"
            break
        except asyncio.TimeoutError:
            # Controlla se serve un heartbeat
            current_time = time.time()
            if current_time - last_heartbeat >= 10:
                yield ": heartbeat\n\n"
                last_heartbeat = current_time

    # Update session history at the end of the stream
    final_answer = "".join(full_answer_parts).strip() or "(no content)"
    try:
        append_turn(tenant_id, session_id, "user", question)
        append_turn(tenant_id, session_id, "assistant", final_answer)
    except Exception:
        pass

    # Final event
    yield "event: end\ndata: [DONE]\n\n"


async def collect_stream_data(llm, messages):
    """Raccoglie tutti i dati dallo stream"""
    parts = []
    async for chunk in llm.astream(messages):
        part = getattr(chunk, "content", None)
        if part:
            parts.append(part)
    return parts
