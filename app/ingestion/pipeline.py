from ..vectordb.factory import get_vectorstore
from ..rag.llm import get_embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

def ingest_text(req):
    """
    Ingest a text document into the vector store for the given tenant.
    """
    # Preparazione del vector store
    vs = get_vectorstore(req.tenant_id)

    # Dividi il testo in chunk
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(req.text)

    # Metadata (filtriamo eventuali valori non supportati)
    metadatas = [{"source_id": req.source_id} for _ in chunks]

    # Aggiunge i chunk al vector store
    vs.add_texts(chunks, metadatas=metadatas)

    # ⚠️ RIMOSSO vs.persist() → non serve più in Chroma ≥ 0.4
    return {"status": "ok", "chunks_ingested": len(chunks)}
