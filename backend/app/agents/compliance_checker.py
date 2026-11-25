"""
Compliance Checker Agent
Verifies a document's adherence to specified regulatory frameworks.
"""
from __future__ import annotations
from typing import Any

from app.core.llm_client import granite_client

SYSTEM_PROMPT = """You are a regulatory compliance expert AI. Analyze the provided document and
assess its compliance against the specified regulations or frameworks.

Your compliance report MUST include:
1. **Compliance Overview** – Overall compliance posture (Compliant / Partially Compliant / Non-Compliant).
2. **Regulation-by-Regulation Breakdown** – For each relevant regulation, assess compliance:
   - ✅ Compliant
   - ⚠️ Partially Compliant (describe gap)
   - ❌ Non-Compliant (describe violation)
3. **Key Violations Found** – List specific violations with clause references.
4. **Remediation Steps** – Prioritized actions to achieve compliance.
5. **Compliance Score** – Provide an estimated score out of 100.

Supported frameworks you can check against: GDPR, HIPAA, CCPA, SOX, ISO 27001,
DPDP Act (India), PCI-DSS, AML/KYC regulations, Employment Law, Contract Law.

Always end with: "⚖️ DISCLAIMER: This compliance check is AI-generated and may not reflect
current regulatory interpretations. Consult a legal or compliance professional."
"""

SUPPORTED_REGULATIONS = [
    "GDPR", "HIPAA", "CCPA", "SOX", "ISO 27001",
    "DPDP Act", "PCI-DSS", "AML/KYC", "Employment Law", "General Contract Law",
]


async def run(payload: dict[str, Any]) -> dict:
    """
    Args:
        payload: {
            "document_text": str,
            "document_name": str,
            "regulations": list[str]  # e.g. ["GDPR", "HIPAA"]
        }
    Returns:
        { "report": str, "compliance_score": int, "violations": list }
    """
    doc_text    = payload.get("document_text", "")
    doc_name    = payload.get("document_name", "document")
    regulations = payload.get("regulations", ["General Contract Law"])

    if not doc_text.strip():
        return {"error": "No document text provided."}

    reg_list = ", ".join(regulations) if regulations else "General Contract Law"
    words    = doc_text.split()
    truncated = " ".join(words[:5000])

    prompt = f"""{SYSTEM_PROMPT}

--- DOCUMENT: {doc_name} ---
{truncated}
--- END OF DOCUMENT ---

Regulations to check against: {reg_list}

Provide your compliance report now:"""

    report = await granite_client.generate(prompt, max_tokens=1500)

    # Extract a rough compliance score from the report
    import re
    score_match = re.search(r"(\d{1,3})\s*/\s*100", report)
    score = int(score_match.group(1)) if score_match else 70

    # Extract violations mentioned
    violation_pattern = re.compile(r"❌[^\n]*", re.MULTILINE)
    violations = violation_pattern.findall(report)

    return {
        "report":           report,
        "compliance_score": min(score, 100),
        "violations":       violations,
        "regulations":      regulations,
        "agent":            "Compliance Checker",
    }
