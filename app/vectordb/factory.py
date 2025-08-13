from ..core.settings import settings
from ..rag.llm import get_embeddings

def safe_collection(tenant_id: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in tenant_id.lower())
    return f"vo_{safe}"

def get_vectorstore(tenant_id: str):
    """
    Return a VectorStore for the given tenant.
    - chroma (dev) persists to disk automatically (Chroma >= 0.4)
    - qdrant (prod) uses Qdrant Cloud
    """
    emb = get_embeddings()
    coll = safe_collection(tenant_id)

    if settings.VECTOR_BACKEND == "qdrant":
        from qdrant_client import QdrantClient
        from langchain_qdrant import QdrantVectorStore
        if not settings.QDRANT_URL or not settings.QDRANT_API_KEY:
            raise RuntimeError("QDRANT_URL/QDRANT_API_KEY not configured")
        client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY, timeout=30)
        return QdrantVectorStore(client=client, collection_name=coll, embeddings=emb)

    # Default: Chroma (nuovo import dal pacchetto langchain-chroma)
    from langchain_chroma import Chroma
    return Chroma(collection_name=coll, embedding_function=emb, persist_directory=settings.CHROMA_DIR)
