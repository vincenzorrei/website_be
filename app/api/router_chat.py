# app/api/router_chat.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from ..models.chat import ChatRequest, ChatResponse
from .deps import require_token
from ..rag.chains import answer_question, stream_answer

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, _auth=Depends(require_token)):
    # Estrai l'ultima domanda dell'utente
    question = next((m.content for m in reversed(req.messages) if m.role == "user"), "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="No user message provided.")

    # Invoca la catena sincrona (risposta "non stream")
    answer, sources = answer_question(
        question,
        tenant_id=req.tenant_id,
        session_id=req.session_id,
        filters=req.filters,
    )

    # Fallback difensivo: garantire sempre answer
    if not isinstance(answer, str) or not answer.strip():
        answer = "Temporary issue. Please try again."
    return ChatResponse(answer=answer, sources=sources or [])


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, _auth=Depends(require_token)):
    # Estrai l'ultima domanda dell'utente
    question = next((m.content for m in reversed(req.messages) if m.role == "user"), "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="No user message provided.")

    async def sse_generator():
        try:
            async for evt in stream_answer(
                question,
                tenant_id=req.tenant_id,
                session_id=req.session_id,
                filters=req.filters,
            ):
                # evt è già una riga SSE (es. "data: ...\n\n" oppure "event: end\n...")
                yield evt
        except Exception as e:
            # Invia errore via SSE e chiudi
            yield f"event: error\ndata: {str(e)}\n\n"

    # Importante: content-type SSE
    return StreamingResponse(sse_generator(), media_type="text/event-stream")
