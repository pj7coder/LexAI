# Role of Agentic AI in the Solution

## 1. Why Agentic AI?
A single monolithic LLM prompt struggles with legal aid because legal tasks require **distinct reasoning modes**:
- Reviewing a contract demands **adversarial risk detection**.
- Checking compliance demands **rule-by-rule regulatory verification**.
- Answering a user's question demands **grounded, citation-backed retrieval**.
- Researching case law demands **precedent synthesis**.

**Agentic AI** solves this by decomposing the problem into specialized, autonomous agents coordinated by an **Orchestrator Agent**, each with its own system persona, tools, and output structure.

---

## 2. Multi-Agent Architecture & Responsibilities

| Agent | Role in the System | Key Capabilities |
|---|---|---|
| **Orchestrator Agent** | Central router & synthesizer | Classifies user intent, selects the right specialist agent(s), merges outputs, and enforces legal disclaimers. |
| **Contract Reviewer Agent** | Risk & clause analyst | Parses contracts, identifies unfavorable/ambiguous clauses, flags missing protections, and rates risk severity. |
| **Compliance Checker Agent** | Regulatory auditor | Cross-checks business practices or documents against regulations (e.g., GDPR, HIPAA, labor laws) and outputs actionable checklists. |
| **Q&A RAG Agent** | Grounded legal explainer | Queries the FAISS vector store for relevant statutes/documents and generates empathetic, jargon-free answers with source citations. |
| **Case Research Agent** | Precedent finder | Retrieves and summarizes relevant judicial decisions, legal doctrines, and case holdings. |

---

## 3. Agentic Workflow
1. **Intent & Context Detection:** The Orchestrator inspects the user's message and any uploaded document context.
2. **Dynamic Delegation:** It routes the task to one or more specialized agents.
3. **Tool & Memory Use:** Agents query the RAG vector store (`VectorStoreService`) and parsed document chunks.
4. **Guardrails & Empathy:** Every agent response is formatted for readability and paired with a clear *"not a substitute for a licensed attorney"* disclaimer.
