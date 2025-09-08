import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()  # <— aggiungi questa riga


@dataclass
class _Settings:
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    # CORS
    ALLOWED_ORIGINS: list[str] = field(default_factory=lambda: [
        "http://127.0.0.1:5500",
        "http://localhost:5173"
    ])
    # Security
    API_TOKEN: str | None = os.getenv("API_TOKEN")
    # Models
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gpt-4o")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.9"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    # Vector DB
    VECTOR_BACKEND: str = os.getenv("VECTOR_BACKEND", "chroma")  # chroma | qdrant
    CHROMA_DIR: str = os.getenv("CHROMA_DIR", ".chroma")
    QDRANT_URL: str | None = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: str | None = os.getenv("QDRANT_API_KEY")
    # N8N
    N8N_CHAT_WEBHOOK: str | None = os.getenv("N8N_CHAT_WEBHOOK")

settings = _Settings()
