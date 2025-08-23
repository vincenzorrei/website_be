# app/rag/chains.py
import asyncio
import time

from .llm import get_llm
from .memory import append_turn, get_history
from .prompts import SYSTEM_PROMPT
from .retriever import build_retriever


def _build_context_and_history(
    question: str, tenant_id: str, session_id: str, filters: dict | None
):
    """Recupera docs e history e costruisce il prompt."""
    retriever = build_retriever(tenant_id, filters)
    try:
        docs = retriever.invoke(question)  # API nuova (niente deprecation)
    except Exception:
        docs = []

    context = "\n\n".join(d.page_content for d in docs[:4]) if docs else "No context."
    history = get_history(tenant_id, session_id)
    history_text = (
        "\n".join(f"{r.upper()}: {c}" for r, c in history[-12:]) if history else "None"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""Conversation history:
{history_text}

Question: {question}

Context:
{context}""",
        },
    ]

    # Mappa fonti
    sources = [
        {
            "source_id": d.metadata.get("source_id", ""),
            "title": d.metadata.get("title", ""),
        }
        for d in docs[:4]
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

    full_answer_parts: list[str] = []
    last_chunk_time = time.time()
    async for chunk in llm.astream(messages):
        part = getattr(chunk, "content", None)
        if not part:
            continue

        # Invia heartbeat se passati più di 10 secondi dall'ultimo chunk
        current_time = time.time()
        if current_time - last_chunk_time > 10:
            yield ": heartbeat\n\n"  # SSE comment per mantenere la connessione
            last_chunk_time = current_time

        full_answer_parts.append(part)
        yield f"data: {part}\n\n"

    final_answer = "".join(full_answer_parts).strip() or "(no content)"

    # Aggiorna memoria di sessione a fine stream
    try:
        append_turn(tenant_id, session_id, "user", question)
        append_turn(tenant_id, session_id, "assistant", final_answer)
    except Exception:
        pass

    # Evento di chiusura opzionale
    yield "event: end\ndata: [DONE]\n\n"
