"""
Chat Route — Conversational Legal Assistant (Q&A RAG + Auto-routing)
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json

from app.agents.orchestrator import auto_route, AgentType, dispatch
from app.core.llm_client import granite_client

router = APIRouter()


class Message(BaseModel):
    role: str    # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    session_history: Optional[List[Message]] = []
    document_context: Optional[str] = ""    # text of an uploaded doc if any
    auto_route: Optional[bool] = True


class ChatResponse(BaseModel):
    reply: str
    agent_used: str
    sources: List[str] = []
    confidence: Optional[str] = None


@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Conversational endpoint — auto-routes to best agent based on user message.
    """
    try:
        history = [m.dict() for m in (req.session_history or [])]
        result = await auto_route(req.message, req.document_context or "")

        # Merge session history into Q&A agent response if applicable
        agent = result.get("agent", "Q&A RAG")
        answer = (
            result.get("answer")
            or result.get("analysis")
            or result.get("report")
            or result.get("research")
            or "I could not generate a response. Please try again."
        )

        return ChatResponse(
            reply=answer,
            agent_used=result.get("routed_to", agent),
            sources=result.get("sources", []),
            confidence=result.get("confidence"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """
    Streaming endpoint — returns SSE chunks directly from Granite.
    """
    prompt = f"""You are a helpful legal AI assistant. Answer the following question clearly.

Question: {req.message}

Answer:"""

    async def event_generator():
        async for chunk in granite_client.stream(prompt):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
