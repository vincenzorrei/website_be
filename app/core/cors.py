from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from .settings import settings

def add_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
