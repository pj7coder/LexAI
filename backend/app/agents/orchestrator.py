"""
Multi-Agent Orchestrator
Routes tasks to the appropriate specialist agent.
"""
from __future__ import annotations
from enum import Enum
from typing import Any

from app.agents import contract_reviewer, compliance_checker, qa_rag_agent, case_research


class AgentType(str, Enum):
    CONTRACT_REVIEWER  = "contract_reviewer"
    COMPLIANCE_CHECKER = "compliance_checker"
    QA_RAG             = "qa_rag"
    CASE_RESEARCH      = "case_research"


async def dispatch(agent_type: AgentType, payload: dict[str, Any]) -> dict:
    """
    Route a request to the appropriate agent and return its result.
    """
    if agent_type == AgentType.CONTRACT_REVIEWER:
        return await contract_reviewer.run(payload)
    elif agent_type == AgentType.COMPLIANCE_CHECKER:
        return await compliance_checker.run(payload)
    elif agent_type == AgentType.QA_RAG:
        return await qa_rag_agent.run(payload)
    elif agent_type == AgentType.CASE_RESEARCH:
        return await case_research.run(payload)
    else:
        return {"error": f"Unknown agent type: {agent_type}"}


async def auto_route(question: str, document_text: str = "") -> dict:
    """
    Automatically choose the best agent based on query intent.
    Returns result from the most appropriate agent.
    """
    q_lower = question.lower()

    # Routing heuristics
    if any(kw in q_lower for kw in ["review contract", "analyze contract", "check contract", "sign this"]):
        payload = {"document_text": document_text or question, "document_name": "uploaded_document"}
        result  = await contract_reviewer.run(payload)
        result["routed_to"] = "Contract Reviewer"
        return result

    elif any(kw in q_lower for kw in ["comply", "compliance", "gdpr", "hipaa", "regulation", "violation"]):
        payload = {
            "document_text": document_text or question,
            "document_name": "uploaded_document",
            "regulations":   ["GDPR", "General Contract Law"],
        }
        result = await compliance_checker.run(payload)
        result["routed_to"] = "Compliance Checker"
        return result

    elif any(kw in q_lower for kw in ["case", "judgment", "precedent", "court", "ruling", "verdict"]):
        payload = {"query": question, "jurisdiction": "General", "legal_area": ""}
        result  = await case_research.run(payload)
        result["routed_to"] = "Case Research"
        return result

    else:
        # Default: Q&A RAG
        payload = {"question": question, "session_history": []}
        result  = await qa_rag_agent.run(payload)
        result["routed_to"] = "Q&A RAG"
        return result
