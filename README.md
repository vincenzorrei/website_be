# website_be — Backend for Chat + RAG

FastAPI backend structured for local development (Chroma) and production (Qdrant).

## Quickstart
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Test it
```bash
curl http://127.0.0.1:8000/health

# Ingest some text
curl -X POST http://127.0.0.1:8000/ingest -H "Content-Type: application/json" -d '{"tenant_id":"default","source_id":"doc_demo","text":"Agentic apps automate workflows integrating APIs and databases."}'

# Ask
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d '{"tenant_id":"default","messages":[{"role":"user","content":"What do agentic apps do?"}]}'
```

> If `OPENAI_API_KEY` is missing, `/chat` returns a **placeholder answer** so you can validate the frontend↔backend wiring. Set your key to enable real LLM answers.

## Project Layout
- `app/api` — HTTP routers (`/chat`, `/ingest`, `/health`)
- `app/core` — settings, CORS, security helpers
- `app/rag` — LLM, prompts, retriever, chains (RAG logic)
- `app/vectordb` — vector DB adapters (Chroma/Qdrant)
- `app/ingestion` — loaders, splitters, pipeline
- `app/models` — Pydantic schemas

## Env (edit `.env`)
```
DEBUG=false
ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5173
# API_TOKEN=your_token

OPENAI_API_KEY=
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-large
TEMPERATURE=0.2

VECTOR_BACKEND=chroma
CHROMA_DIR=.chroma
# QDRANT_URL=
# QDRANT_API_KEY=
```

## Deploy
- Railway: start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Use Qdrant Cloud in production by setting `VECTOR_BACKEND=qdrant` and the related credentials.
