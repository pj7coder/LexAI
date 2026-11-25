"""
Case Research Agent
Fetches and summarizes relevant case law, judgments, and legal precedents.
"""
from __future__ import annotations
from typing import Any

from app.core.llm_client import granite_client
from app.services.vector_store import VectorStoreService

SYSTEM_PROMPT = """You are an expert legal researcher AI. Your task is to find and summarize
relevant case law, judicial precedents, and legal judgments related to the user's query.

Your research report MUST include:
1. **Relevant Cases Found** – List the most applicable cases with:
   - Case name and citation
   - Court and year
   - Key facts and holding
   - Relevance to the user's situation
2. **Legal Principles Established** – Key doctrines or rules arising from these cases.
3. **Precedent Analysis** – How these precedents might apply to the user's situation.
4. **Jurisdiction Notes** – Flag if precedents vary significantly by jurisdiction.
5. **Research Summary** – Practical takeaways for the user.

If you cannot find specific cases, explain the general legal principle and suggest
the user consult legal databases like Westlaw, LexisNexis, or IndianKanoon.

Always end with: "⚖️ DISCLAIMER: Case research is AI-generated and may not include
the most recent judgments. Always verify case citations independently."
"""

# Curated built-in landmark cases for common legal topics
LANDMARK_CASES = {
    "contract": [
        "Carlill v Carbolic Smoke Ball Co [1893] 1 QB 256 — Unilateral contract, offer and acceptance",
        "Hadley v Baxendale (1854) 9 Exch 341 — Remoteness of damage in contract breach",
        "Hong Kong Fir Shipping Co v Kawasaki Kisen Kaisha [1962] — Innominate terms",
    ],
    "gdpr": [
        "Schrems II (Data Protection Commissioner v Facebook Ireland, C-311/18) — Data transfers",
        "Google Spain SL v AEPD (C-131/12) — Right to be forgotten",
        "Planet49 GmbH (C-673/17) — Cookie consent requirements",
    ],
    "employment": [
        "Faragher v City of Boca Raton (1998) — Employer liability for harassment",
        "Bostock v Clayton County (2020) — LGBTQ+ employment discrimination",
        "NCT v Maheshwari (India, 2021) — Wrongful termination",
    ],
    "privacy": [
        "Puttaswamy v Union of India (2017) — Right to Privacy (India)",
        "Olmstead v United States (1928) — Electronic surveillance, 4th Amendment",
        "Riley v California (2014) — Digital privacy, cell phone searches",
    ],
    "intellectual property": [
        "Diamond v Chakrabarty (1980) — Patentability of living organisms",
        "Campbell v Acuff-Rose Music (1994) — Fair use, parody",
        "Alice Corp v CLS Bank (2014) — Software patent eligibility",
    ],
}


async def run(payload: dict[str, Any]) -> dict:
    """
    Args:
        payload: { "query": str, "jurisdiction": str, "legal_area": str }
    Returns:
        { "research": str, "cases_found": list, "legal_area": str }
    """
    query        = payload.get("query", "").strip()
    jurisdiction = payload.get("jurisdiction", "General / International")
    legal_area   = payload.get("legal_area", "").strip().lower()

    if not query:
        return {"error": "No research query provided."}

    # Find matching landmark cases
    built_in_cases = []
    for topic, cases in LANDMARK_CASES.items():
        if topic in query.lower() or topic in legal_area:
            built_in_cases.extend(cases)

    built_in_text = ""
    if built_in_cases:
        built_in_text = "\n=== KNOWN RELEVANT CASES ===\n"
        for case in built_in_cases[:6]:
            built_in_text += f"• {case}\n"
        built_in_text += "=== END ===\n"

    # RAG search over uploaded documents
    retrieved = await VectorStoreService.search(query, top_k=3)
    rag_text  = ""
    if retrieved:
        rag_text = "\n=== UPLOADED DOCUMENT CONTEXT ===\n"
        for chunk, _ in retrieved:
            rag_text += chunk["text"][:500] + "\n---\n"
        rag_text += "=== END ===\n"

    prompt = f"""{SYSTEM_PROMPT}
{built_in_text}{rag_text}
Research Query: {query}
Jurisdiction: {jurisdiction}
Legal Area: {legal_area or 'General'}

Provide your case research report now:"""

    research = await granite_client.generate(prompt, max_tokens=1400)

    return {
        "research":    research,
        "cases_found": built_in_cases,
        "jurisdiction": jurisdiction,
        "legal_area":   legal_area or "General",
        "agent":        "Case Research",
    }
