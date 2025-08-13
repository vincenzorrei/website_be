from pydantic import BaseModel
from typing import Literal, List, Optional

Role = Literal["user","assistant","system"]

class Message(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    tenant_id: str = "default"
    session_id: str
    messages: List[Message]
    filters: Optional[dict] = None

class Source(BaseModel):
    source_id: str
    title: str | None = None

class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = []
