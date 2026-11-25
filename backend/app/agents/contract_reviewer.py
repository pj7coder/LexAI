"""
Contract Reviewer Agent
Flags risks, obligations, one-sided clauses, and inconsistencies in contracts.
"""
from __future__ import annotations
from typing import Any

from app.core.llm_client import granite_client

SYSTEM_PROMPT = """You are an expert contract lawyer AI assistant. Your task is to analyze the
provided contract text and produce a structured legal review.

Your review MUST include:
1. **Executive Summary** – 2-3 sentence overview of the contract.
2. **Key Parties & Obligations** – List each party and their core obligations.
3. **Risk Flags** 🚩 – Highlight clauses that are one-sided, vague, or potentially harmful.
4. **Missing Clauses** – Note any standard protections that appear to be absent.
5. **Termination & Penalty Clauses** – Summarize exit conditions and financial penalties.
6. **Recommended Actions** – Concrete steps the user should take before signing.

Format your response in clean Markdown. Use ⚠️ for high risk, ⚡ for medium risk, ℹ️ for info.
Always end with: "⚖️ DISCLAIMER: This analysis is AI-generated and does not constitute legal advice.
Consult a qualified attorney before making legal decisions."
"""


async def run(payload: dict[str, Any]) -> dict:
    """
    Args:
        payload: { "document_text": str, "document_name": str }
    Returns:
        { "analysis": str, "risk_level": str, "risk_count": int }
    """
    doc_text = payload.get("document_text", "")
    doc_name = payload.get("document_name", "contract")

    if not doc_text.strip():
        return {"error": "No contract text provided."}

    # Truncate to ~6000 words to stay within context window
    words    = doc_text.split()
    truncated = " ".join(words[:6000])
    if len(words) > 6000:
        truncated += "\n\n[... document truncated for analysis ...]"

    prompt = f"""{SYSTEM_PROMPT}

--- CONTRACT: {doc_name} ---
{truncated}
--- END OF CONTRACT ---

Provide your structured review now:"""

    analysis = await granite_client.generate(prompt, max_tokens=1500)

    # Heuristic risk scoring
    high_risk_keywords = [
        "indemnif", "unlimited liability", "perpetual", "irrevocable",
        "waive", "arbitration only", "no warranty", "as-is",
    ]
    medium_risk_keywords = [
        "automatic renewal", "liquidated damages", "non-compete",
        "exclusive", "jurisdiction", "governing law",
    ]

    text_lower = doc_text.lower()
    high_count   = sum(1 for kw in high_risk_keywords if kw in text_lower)
    medium_count = sum(1 for kw in medium_risk_keywords if kw in text_lower)
    total_flags  = high_count + medium_count

    if high_count >= 3:
        risk_level = "HIGH"
    elif high_count >= 1 or medium_count >= 3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "analysis":   analysis,
        "risk_level": risk_level,
        "risk_count": total_flags,
        "agent":      "Contract Reviewer",
    }
