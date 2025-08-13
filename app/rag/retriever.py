from ..vectordb.factory import get_vectorstore

def build_retriever(tenant_id: str, filters: dict | None = None):
    vs = get_vectorstore(tenant_id)
    retriever = vs.as_retriever(search_kwargs={"k": 6})
    # NOTE: filters can be applied via metadata if backend supports it (Qdrant has filters; Chroma limited)
    return retriever
