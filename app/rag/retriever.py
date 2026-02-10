import logging

from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.document_compressors import FlashrankRerank

from ..core.settings import settings
from ..vectordb.factory import get_vectorstore

logger = logging.getLogger(__name__)


def build_retriever(tenant_id: str, filters: dict | None = None):
    vs = get_vectorstore(tenant_id)
    semantic_retriever = vs.as_retriever(search_kwargs={"k": 6})

    # --- Hybrid: BM25 + Semantic via EnsembleRetriever ---
    # BM25 uses Chroma's .get() API which is not compatible with Qdrant,
    # so skip it entirely when using Qdrant to avoid unnecessary latency.
    doc_objects = []
    if settings.VECTOR_BACKEND != "qdrant":
        try:
            all_docs = vs.get()  # Chroma .get() returns dict with documents/metadatas
            from langchain_core.documents import Document

            texts = all_docs.get("documents", [])
            metadatas = all_docs.get("metadatas", []) or [{}] * len(texts)
            doc_objects = [
                Document(page_content=t, metadata=m or {})
                for t, m in zip(texts, metadatas)
                if t  # skip empty
            ]
        except Exception:
            doc_objects = []

    if doc_objects:
        bm25_retriever = BM25Retriever.from_documents(doc_objects, k=6)
        ensemble = EnsembleRetriever(
            retrievers=[bm25_retriever, semantic_retriever],
            weights=[0.3, 0.7],
        )
        base_retriever = ensemble
        logger.info("Hybrid search enabled: BM25 (0.3) + Semantic (0.7)")
    else:
        base_retriever = semantic_retriever
        logger.info("Using semantic search only")

    # --- Reranking with FlashRank ---
    try:
        reranker = FlashrankRerank(top_n=4)
        retriever = ContextualCompressionRetriever(
            base_compressor=reranker,
            base_retriever=base_retriever,
        )
        logger.info("FlashRank reranking enabled (top_n=4)")
    except Exception as e:
        logger.warning("FlashRank reranking unavailable: %s. Using base retriever.", e)
        retriever = base_retriever

    return retriever
