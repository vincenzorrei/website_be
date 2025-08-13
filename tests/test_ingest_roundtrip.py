from fastapi.testclient import TestClient
from app.main import app

def test_ingest_roundtrip():
    c = TestClient(app)
    txt = "Agentic apps automate workflows integrating APIs and databases."
    c.post("/ingest", json={"tenant_id":"default","source_id":"doc_demo","text":txt})
    r = c.post("/chat", json={"tenant_id":"default","messages":[{"role":"user","content":"What do agentic apps do?"}]})
    assert r.status_code == 200
