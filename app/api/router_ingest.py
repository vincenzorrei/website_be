from fastapi import APIRouter, Depends, HTTPException
from ..models.ingest import IngestTextRequest, IngestResponse
from .deps import require_token
from ..ingestion.pipeline import ingest_text

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestTextRequest, _auth=Depends(require_token)):
    if not req.text or not req.source_id:
        raise HTTPException(status_code=400, detail="Missing text or source_id")
    res = ingest_text(req)
    return IngestResponse(**res)
