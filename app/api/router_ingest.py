from fastapi import APIRouter, Depends, HTTPException
from ..models.ingest import IngestTextRequest, IngestResponse, DeleteResponse
from .deps import require_token
from ..ingestion.pipeline import ingest_text
from ..vectordb.utils import delete_by_source, delete_all

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestTextRequest, _auth=Depends(require_token)):
    if not req.text or not req.source_id:
        raise HTTPException(status_code=400, detail="Missing text or source_id")
    res = ingest_text(req)
    return IngestResponse(**res)


@router.delete("/ingest/{source_id}", response_model=DeleteResponse)
def delete_source(source_id: str, tenant_id: str = "default", _auth=Depends(require_token)):
    """Delete all chunks for a specific source_id."""
    count = delete_by_source(tenant_id, source_id)
    return DeleteResponse(status="ok", deleted_source=source_id, deleted_chunks=count)


@router.delete("/ingest", response_model=DeleteResponse)
def delete_all_docs(tenant_id: str = "default", _auth=Depends(require_token)):
    """Delete all documents for a tenant."""
    count = delete_all(tenant_id)
    return DeleteResponse(status="ok", deleted_source="*", deleted_chunks=count)
