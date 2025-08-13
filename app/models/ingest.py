from pydantic import BaseModel
from typing import List

class IngestTextRequest(BaseModel):
    tenant_id: str = "default"
    source_id: str
    text: str
    title: str | None = None
    tags: List[str] = []

class IngestResponse(BaseModel):
    chunks: int
    status: str
