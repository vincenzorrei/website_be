from fastapi import APIRouter, Depends, HTTPException
from ..models.chat import ChatRequest, ChatResponse
from .deps import require_token
from ..rag.chains import answer_question

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, _auth=Depends(require_token)):
    question = next((m.content for m in reversed(req.messages) if m.role == "user"), "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="No user message provided.")
    answer, sources = answer_question(
        question,
        tenant_id=req.tenant_id,
        session_id=req.session_id,
        filters=req.filters
    )
    return ChatResponse(answer=answer, sources=sources)
