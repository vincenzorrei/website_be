from .llm import get_llm
from .prompts import SYSTEM_PROMPT
from .retriever import build_retriever
from .memory import get_history, append_turn

def answer_question(question: str, tenant_id: str = "default", session_id: str = "default", filters: dict | None = None):
    try:
        llm = get_llm()
    except Exception:
        return ("Backend ready. Configure OPENAI_API_KEY to enable AI answers. Your question was: " + question, [])

    retriever = build_retriever(tenant_id, filters)
    try:
        docs = retriever.invoke(question)
    except Exception:
        docs = []

    # 1) recupera memoria per-sessione
    history = get_history(tenant_id, session_id)
    history_text = "\n".join(f"{r.upper()}: {c}" for r,c in history[-12:]) if history else "None"

    # 2) prepara contesto RAG
    context = "\n\n".join(d.page_content for d in docs[:4]) if docs else "No context."

    messages = [
        {"role":"system","content": SYSTEM_PROMPT},
        {"role":"user","content": f"""Conversation history:
        {history_text}

        Question: {question}

        Context:
        {context}"""}
    ]
    resp = llm.invoke(messages)

    # 3) aggiorna memoria (salva turno corrente)
    append_turn(tenant_id, session_id, "user", question)
    append_turn(tenant_id, session_id, "assistant", resp.content)

    sources = [{"source_id": d.metadata.get("source_id",""), "title": d.metadata.get("title","")} for d in docs[:4]]
    return (resp.content, sources)
