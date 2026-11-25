"""
Q&A RAG Agent
Answers user legal questions using Retrieval-Augmented Generation
over indexed legal documents and built-in legal knowledge.
"""
from __future__ import annotations
from typing import Any

from app.core.llm_client import granite_client
from app.services.vector_store import VectorStoreService

SYSTEM_PROMPT = """You are a knowledgeable, empathetic legal AI assistant. Answer the user's
question clearly and accurately based on:
1. The retrieved legal context provided below (if any).
2. Your general knowledge of law, regulations, and legal principles.

Guidelines:
- Use plain English — avoid excessive jargon.
- Structure longer answers with headers and bullet points.
- If the answer depends on jurisdiction, mention this clearly.
- If you are uncertain, say so explicitly rather than guessing.
- Always cite the relevant law, section, or principle when possible.
- Provide practical, actionable guidance when appropriate.

Always end with:
"⚖️ DISCLAIMER: This is general legal information, not legal advice.
Laws vary by jurisdiction and change over time. Consult a qualified attorney for advice specific to your situation."
"""


async def run(payload: dict[str, Any]) -> dict:
    """
    Args:
        payload: { "question": str, "session_history": list[dict] }
    Returns:
        { "answer": str, "sources": list[str], "confidence": str }
    """
    question = payload.get("question", "").strip()
    history  = payload.get("session_history", [])

    if not question:
        return {"error": "No question provided."}

    # --- RAG: Retrieve relevant chunks ---
    retrieved = await VectorStoreService.search(question, top_k=4)
    context_parts = []
    sources = []
    for chunk, score in retrieved:
        context_parts.append(chunk["text"])
        src = chunk.get("source", "Unknown")
        if src not in sources:
            sources.append(src)

    context_text = "\n\n---\n\n".join(context_parts) if context_parts else ""

    # Build conversation history string
    history_text = ""
    for turn in history[-4:]:  # last 4 turns for context
        role    = turn.get("role", "user")
        content = turn.get("content", "")
        history_text += f"\n{role.upper()}: {content}"

    # Build prompt
    prompt_parts = [SYSTEM_PROMPT, "\n"]
    if context_text:
        prompt_parts.append(f"=== RETRIEVED LEGAL CONTEXT ===\n{context_text}\n=== END CONTEXT ===\n")
    if history_text:
        prompt_parts.append(f"=== CONVERSATION HISTORY ==={history_text}\n=== END HISTORY ===\n")
    prompt_parts.append(f"\nUSER QUESTION: {question}\n\nANSWER:")

    prompt = "\n".join(prompt_parts)
    answer = await granite_client.generate(prompt, max_tokens=1200)

    # Confidence heuristic
    if context_parts:
        confidence = "HIGH" if len(context_parts) >= 3 else "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "answer":     answer,
        "sources":    sources,
        "confidence": confidence,
        "rag_chunks": len(context_parts),
        "agent":      "Q&A RAG",
    }
