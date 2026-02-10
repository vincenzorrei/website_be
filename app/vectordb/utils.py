from ..core.settings import settings
from .factory import get_vectorstore, safe_collection


def delete_by_source(tenant_id: str, source_id: str) -> int:
    """Delete all chunks for a given source_id. Returns number of deleted chunks."""
    coll = safe_collection(tenant_id)

    if settings.VECTOR_BACKEND == "qdrant":
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY, timeout=30)
        # Count before delete
        count = client.count(
            collection_name=coll,
            count_filter=Filter(must=[FieldCondition(key="metadata.source_id", match=MatchValue(value=source_id))]),
        ).count
        client.delete(
            collection_name=coll,
            points_selector=Filter(must=[FieldCondition(key="metadata.source_id", match=MatchValue(value=source_id))]),
        )
        return count

    # Chroma
    from langchain_chroma import Chroma
    from ..rag.llm import get_embeddings

    store = Chroma(collection_name=coll, embedding_function=get_embeddings(), persist_directory=settings.CHROMA_DIR)
    col = store._collection
    results = col.get(where={"source_id": source_id})
    ids = results["ids"]
    if ids:
        col.delete(ids=ids)
    return len(ids)


def delete_all(tenant_id: str) -> int:
    """Delete all chunks in the tenant collection. Returns number of deleted chunks."""
    coll = safe_collection(tenant_id)

    if settings.VECTOR_BACKEND == "qdrant":
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter

        client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY, timeout=30)
        try:
            count = client.count(collection_name=coll).count
        except Exception:
            return 0
        client.delete_collection(collection_name=coll)
        return count

    # Chroma
    from langchain_chroma import Chroma
    from ..rag.llm import get_embeddings

    store = Chroma(collection_name=coll, embedding_function=get_embeddings(), persist_directory=settings.CHROMA_DIR)
    col = store._collection
    count = col.count()
    if count > 0:
        all_ids = col.get()["ids"]
        col.delete(ids=all_ids)
    return count


def list_sources(tenant_id: str) -> list[dict]:
    """List all unique source_ids with chunk counts. Returns list of {source_id, chunks}."""
    coll = safe_collection(tenant_id)

    if settings.VECTOR_BACKEND == "qdrant":
        from qdrant_client import QdrantClient
        from qdrant_client.models import ScrollRequest

        client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY, timeout=30)
        sources: dict[str, int] = {}
        try:
            offset = None
            while True:
                results, offset = client.scroll(
                    collection_name=coll,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )
                for point in results:
                    sid = (point.payload or {}).get("metadata", {}).get("source_id", "unknown")
                    sources[sid] = sources.get(sid, 0) + 1
                if offset is None:
                    break
        except Exception:
            pass
        return [{"source_id": k, "chunks": v} for k, v in sorted(sources.items())]

    # Chroma
    from langchain_chroma import Chroma
    from ..rag.llm import get_embeddings

    store = Chroma(collection_name=coll, embedding_function=get_embeddings(), persist_directory=settings.CHROMA_DIR)
    col = store._collection
    sources: dict[str, int] = {}
    if col.count() > 0:
        results = col.get(include=["metadatas"])
        for meta in results.get("metadatas", []):
            sid = (meta or {}).get("source_id", "unknown")
            sources[sid] = sources.get(sid, 0) + 1
    return [{"source_id": k, "chunks": v} for k, v in sorted(sources.items())]
