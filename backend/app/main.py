"""
FastAPI Application — AI Legal Aid Multi-Agent System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import pathlib

from app.core.config import settings
from app.api.routes import chat, documents, agents, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    # Use pathlib so paths work regardless of cwd
    pathlib.Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    pathlib.Path(settings.VECTOR_STORE_DIR).mkdir(parents=True, exist_ok=True)
    # Warm-up vector store
    from app.services.vector_store import VectorStoreService
    await VectorStoreService.initialize()
    yield


app = FastAPI(
    title="AI Legal Aid Multi-Agent System",
    description="IBM Granite-powered multi-agent system for legal assistance",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
