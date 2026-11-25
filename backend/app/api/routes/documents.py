"""
Documents Route — Upload, parse, and index legal documents.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import List, Optional
import uuid

from app.services.document_parser import parse_document, chunk_document
from app.services.vector_store import VectorStoreService

router = APIRouter()


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    text_length: int
    chunks_indexed: int
    message: str


class DocumentAnalysisRequest(BaseModel):
    document_id: Optional[str] = None
    document_text: str
    document_name: str = "document"


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    index: bool = Form(True),
):
    """
    Upload a legal document (PDF/DOCX/TXT), parse it, and optionally index it
    into the RAG vector store.
    """
    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "application/octet-stream",
    }
    allowed_exts = {"pdf", "docx", "doc", "txt", "md"}

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type .{ext}. Allowed: {', '.join(allowed_exts)}"
        )

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="File too large (max 10 MB).")

    try:
        text = await parse_document(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    doc_id = str(uuid.uuid4())
    chunks_indexed = 0

    if index and text.strip():
        chunks = chunk_document(text, source=file.filename, metadata={"doc_id": doc_id})
        await VectorStoreService.add_documents(chunks)
        chunks_indexed = len(chunks)

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        text_length=len(text),
        chunks_indexed=chunks_indexed,
        message=f"Document parsed successfully. {chunks_indexed} chunks indexed for RAG.",
    )


@router.get("/stats")
async def document_stats():
    """Return current vector store statistics."""
    return {
        "indexed_chunks": VectorStoreService.document_count(),
        "status": "ready",
    }
