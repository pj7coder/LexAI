"""
Agents Route — Direct access to each specialized agent.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.agents.orchestrator import AgentType, dispatch

router = APIRouter()


# --- Request / Response Models ---

class ContractReviewRequest(BaseModel):
    document_text: str
    document_name: str = "contract"


class ComplianceCheckRequest(BaseModel):
    document_text: str
    document_name: str = "document"
    regulations: List[str] = ["General Contract Law"]


class QARagRequest(BaseModel):
    question: str
    session_history: Optional[List[dict]] = []


class CaseResearchRequest(BaseModel):
    query: str
    jurisdiction: str = "General / International"
    legal_area: str = ""


# --- Endpoints ---

@router.post("/contract-review")
async def contract_review(req: ContractReviewRequest):
    """Contract Reviewer Agent — flags risks and obligations."""
    try:
        return await dispatch(AgentType.CONTRACT_REVIEWER, req.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance-check")
async def compliance_check(req: ComplianceCheckRequest):
    """Compliance Checker Agent — verifies regulatory adherence."""
    try:
        return await dispatch(AgentType.COMPLIANCE_CHECKER, req.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/qa")
async def qa_rag(req: QARagRequest):
    """Q&A RAG Agent — answers legal questions using retrieved context."""
    try:
        return await dispatch(AgentType.QA_RAG, req.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/case-research")
async def case_research(req: CaseResearchRequest):
    """Case Research Agent — finds relevant judgments and precedents."""
    try:
        return await dispatch(AgentType.CASE_RESEARCH, req.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_agents():
    """List all available agents."""
    return {
        "agents": [
            {
                "id":          "contract_reviewer",
                "name":        "Contract Reviewer",
                "description": "Analyzes contracts for risks, obligations, and missing clauses.",
                "endpoint":    "/api/v1/agents/contract-review",
            },
            {
                "id":          "compliance_checker",
                "name":        "Compliance Checker",
                "description": "Checks documents against GDPR, HIPAA, SOX, and other regulations.",
                "endpoint":    "/api/v1/agents/compliance-check",
            },
            {
                "id":          "qa_rag",
                "name":        "Q&A RAG Agent",
                "description": "Answers legal questions using RAG over your uploaded documents.",
                "endpoint":    "/api/v1/agents/qa",
            },
            {
                "id":          "case_research",
                "name":        "Case Research Agent",
                "description": "Finds relevant case law, judgments, and legal precedents.",
                "endpoint":    "/api/v1/agents/case-research",
            },
        ]
    }
