from pathlib import Path

from ..vectordb.factory import get_vectorstore
from .splitters import default_splitter


def ingest_text(req):
    """
    Ingest a text document into the vector store for the given tenant.
    """
    vs = get_vectorstore(req.tenant_id)

    splitter = default_splitter()
    chunks = splitter.split_text(req.text)

    metadatas = [{"source_id": req.source_id} for _ in chunks]

    vs.add_texts(chunks, metadatas=metadatas)

    return {"status": "ok", "chunks": len(chunks)}


def ingest_file(file_path: str, tenant_id: str = "default", source_id: str | None = None) -> dict:
    """
    Load a file from disk, split it, and ingest into the vector store.
    """
    from .loaders import load_file

    text = load_file(file_path)
    if not text:
        return {"status": "empty", "chunks": 0}

    if source_id is None:
        source_id = Path(file_path).name

    vs = get_vectorstore(tenant_id)
    splitter = default_splitter()
    chunks = splitter.split_text(text)
    metadatas = [{"source_id": source_id} for _ in chunks]
    vs.add_texts(chunks, metadatas=metadatas)

    return {"status": "ok", "chunks": len(chunks), "source_id": source_id}
