"""
Health Check Route
"""
from fastapi import APIRouter
from app.services.vector_store import VectorStoreService

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status":        "ok",
        "service":       "AI Legal Aid Multi-Agent System",
        "vector_docs":   VectorStoreService.document_count(),
    }
