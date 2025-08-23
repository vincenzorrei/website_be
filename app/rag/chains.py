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
    start_time = time.time()
    print(f"Starting stream at {start_time}")

    # Invia un heartbeat immediato all'inizio
    yield ": initial heartbeat\n\n"

    # We'll create an async generator for the LLM
    llm_stream = llm.astream(messages)



    # Time of last data (or heartbeat) we sent
    last_sent_time = time.time()
    # We'll set the heartbeat interval to 25 seconds to stay under Railway's 30s timeout
    heartbeat_interval = 25

    while True:
        # Check if it's time to send a heartbeat
        current_time = time.time()
        if current_time - last_sent_time > heartbeat_interval:
            # Send a heartbeat
            yield ": heartbeat\n\n"
            last_sent_time = current_time

        try:
            # Wait for the next chunk with a short timeout so we can break to check for heartbeats
            # We use a timeout of 1 second to not delay the tokens too much
            chunk = await asyncio.wait_for(llm_stream.__anext__(), timeout=1.0)
            part = getattr(chunk, "content", None)
            if part:
                yield f"data: {part}\n\n"
                last_sent_time = current_time  # update the time since we sent data
        except asyncio.TimeoutError:
            # Timeout waiting for chunk, we'll go back and check if we need to send a heartbeat
            pass
        except StopAsyncIteration:
            # The stream is done
            break
        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"
            break

    # Update session history at the end of the stream
    final_answer = "".join(full_answer_parts).strip() or "(no content)"
    try:
        append_turn(tenant_id, session_id, "user", question)
        append_turn(tenant_id, session_id, "assistant", final_answer)
    except Exception:
        pass

    # Final event
    yield "event: end\ndata: [DONE]\n\n"
