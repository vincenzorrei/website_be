from fastapi.testclient import TestClient
from app.main import app

def test_chat_smoke():
    c = TestClient(app)
    r = c.post("/chat", json={"tenant_id":"default","messages":[{"role":"user","content":"Hello?"}]})
    assert r.status_code == 200
    assert "answer" in r.json()
