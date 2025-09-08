# app/api/router_chat.py - Versione semplificata per n8n AI Agent
from fastapi import APIRouter, Depends, HTTPException
import httpx
import asyncio
from ..models.chat import ChatRequest, ChatResponse
from .deps import require_token
from ..core.settings import settings

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_via_n8n(req: ChatRequest, _auth=Depends(require_token)):
    """
    Delega la chat all'AI Agent di n8n.
    Estrae l'ultima domanda e la invia a n8n.
    """
    
    # Estrai l'ultima domanda dell'utente
    question = ""
    for message in reversed(req.messages):
        if message.role == "user":
            question = message.content.strip()
            break
    
    if not question:
        raise HTTPException(status_code=400, detail="No user message found")
    
    if not settings.N8N_CHAT_WEBHOOK:
        # Fallback se n8n non configurato
        return ChatResponse(
            answer=f"Backend ready. Configure N8N_CHAT_WEBHOOK to enable AI. Your question: {question}",
            sources=[]
        )
    
    # Payload semplice per n8n AI Agent
    payload = {
        "chatInput": question,
        "sessionId": req.session_id or "default",
        "metadata": {
            "tenant_id": req.tenant_id,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.N8N_CHAT_WEBHOOK, 
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502, 
                    detail=f"n8n webhook failed with status {response.status_code}: {response.text}"
                )
            
            # n8n AI Agent dovrebbe restituire qualcosa come: {"output": "risposta..."}
            result = response.json()
            
            # Estrai la risposta dall'AI Agent
            answer = ""
            if isinstance(result, dict):
                answer = result.get("output", "") or result.get("response", "") or result.get("text", "")
            elif isinstance(result, str):
                answer = result
            
            if not answer.strip():
                answer = "Non ho ricevuto una risposta valida dall'AI. Riprova."
            
            return ChatResponse(
                answer=answer.strip(),
                sources=[]  # Per ora senza sources, li aggiungeremo dopo
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="n8n AI Agent timeout")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error connecting to n8n: {str(e)}")
    except Exception as e:
        # Fallback in caso di errore
        return ChatResponse(
            answer="Scusa, sto avendo problemi tecnici. Riprova tra un momento.",
            sources=[]
        )