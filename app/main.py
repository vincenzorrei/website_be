from fastapi import FastAPI
from .core.settings import settings
from .core.cors import add_cors
from .api.router_health import router as health_router
from .api.router_chat import router as chat_router
from .api.router_ingest import router as ingest_router

app = FastAPI(title="website_be", debug=settings.DEBUG)

add_cors(app)

app.include_router(health_router, prefix="")
app.include_router(chat_router, prefix="")
app.include_router(ingest_router, prefix="")
