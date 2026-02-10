# app/api/router_chat.py
import re

from fastapi import APIRouter, Depends, HTTPException
from ..models.chat import ChatRequest, ChatResponse, Source
from .deps import require_token
from ..rag.chains import answer_question

router = APIRouter()

_MAX_INPUT_LENGTH = 2000

# Patterns that indicate prompt injection attempts
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|rules)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(a|an)\s+", re.IGNORECASE),
    re.compile(r"new\s+instructions?\s*:", re.IGNORECASE),
    re.compile(r"system\s*prompt\s*:", re.IGNORECASE),
    re.compile(r"forget\s+(everything|all|your)\s+(you|instructions|rules)", re.IGNORECASE),
    re.compile(r"override\s+(system|your)\s+(prompt|instructions|rules)", re.IGNORECASE),
    re.compile(r"disregard\s+(all|any|previous|your)\s+(previous\s+)?(instructions|rules|prompts)", re.IGNORECASE),
]


def _validate_input(text: str) -> str:
    """Validate and sanitize user input. Returns cleaned text or raises HTTPException."""
    if len(text) > _MAX_INPUT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Message too long. Maximum {_MAX_INPUT_LENGTH} characters allowed.",
        )

    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            raise HTTPException(
                status_code=400,
                detail="Your message was flagged by our safety filter. Please rephrase your question.",
            )

    return text.strip()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, _auth=Depends(require_token)):
    """
    Risponde alla domanda dell'utente usando la RAG chain LangChain.
    """
    # Estrai l'ultima domanda dell'utente
    question = ""
    for message in reversed(req.messages):
        if message.role == "user":
            question = message.content.strip()
            break

    if not question:
        raise HTTPException(status_code=400, detail="No user message found")

    # Prompt injection guard
    question = _validate_input(question)

    answer, sources = answer_question(
        question=question,
        tenant_id=req.tenant_id,
        session_id=req.session_id or "default",
        filters=req.filters,
    )

    return ChatResponse(
        answer=answer,
        sources=[Source(**s) for s in sources],
    )
