from fastapi import APIRouter
from ..core.settings import settings

router = APIRouter()

@router.get("/health")
def health():
    return {
        "status": "ok",
        "vector_backend": settings.VECTOR_BACKEND,
        "debug": settings.DEBUG,
        "time": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }

@router.get("/version")
def version():
    return {"app": "website_be", "version": "0.1.0"}
