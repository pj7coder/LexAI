# Proposed Solution — LexAI: Multi-Agent Legal Aid System

## 1. Executive Summary
**LexAI** is an AI-powered Multi-Agent Legal Aid System designed to democratize access to legal information, contract analysis, and regulatory compliance for individuals and small businesses. Powered by **IBM Granite** (`ibm/granite-3-8b-instruct` via IBM watsonx.ai) and a **Retrieval-Augmented Generation (RAG)** pipeline, LexAI translates complex legal jargon into clear, empathetic, and actionable guidance—while strictly maintaining ethical boundaries with explicit *"not a substitute for a lawyer"* disclaimers.

---

## 2. Problem Statement & Objectives
Access to legal advice is traditionally expensive, slow, and fragmented across dense statutes, case law, and complex contracts. LexAI addresses this through four core capabilities:

1. **Legal Information Retrieval (RAG):** Extracts and summarizes relevant laws, precedents, and compliance rules from indexed legal corpora.
2. **Document Parsing & Analysis:** Automatically ingests PDF, DOCX, and TXT contracts, policies, and notices to highlight key clauses, obligations, and potential risks.
3. **Conversational Legal Assistant:** Delivers empathetic, plain-English explanations of legal concepts through natural dialogue, always accompanied by clear legal disclaimers.
4. **Specialized Multi-Agent Orchestration:** Routes user requests to dedicated domain agents—**Contract Reviewer**, **Compliance Checker**, **Q&A RAG**, and **Case Research**—coordinated by a central **Orchestrator Agent**.

---

## 3. System Architecture

```
User (Web UI / REST API)
         │
         ▼
┌─────────────────────────────────────────────┐
│           Orchestrator Agent                │
│  (Intent Classification & Multi-Agent       │
│   Routing + Synthesis + Disclaimer)         │
└──────┬──────────┬──────────┬──────────┬─────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
 ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
 │ Contract │ │Compliance│ │ Q&A RAG  │ │   Case   │
 │ Reviewer │ │ Checker  │ │  Agent   │ │ Research │
 │  Agent   │ │  Agent   │ │          │ │  Agent   │
 └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
      │            │            │            │
      └────────────┴─────┬──────┴────────────┘
                         ▼
         ┌───────────────────────────────┐
         │   RAG & Document Pipeline     │
         │  (PyPDF2 / pdfplumber /       │
         │   python-docx + FAISS Vector  │
         │   Store + SentenceTransformers│
         └───────────────┬───────────────┘
                         ▼
         ┌───────────────────────────────┐
         │   IBM watsonx.ai (Granite)    │
         │  + Graceful Demo Fallback     │
         └───────────────────────────────┘
```

---

## 4. Core Components

### 4.1 Orchestrator Agent (`backend/app/agents/orchestrator.py`)
- Classifies incoming user queries and document contexts.
- Routes tasks to the most appropriate specialized agent (or multiple agents in parallel).
- Synthesizes structured, user-friendly responses with consistent legal disclaimers.

### 4.2 Specialized Multi-Agents
- **Contract Reviewer Agent (`contract_reviewer.py`):** Scans uploaded contracts and clauses to flag high-risk terms (e.g., unlimited liability, unilateral termination, non-compete overreach), missing protections, and internal inconsistencies.
- **Compliance Checker Agent (`compliance_checker.py`):** Evaluates documents and business scenarios against regulatory frameworks (GDPR, CCPA, HIPAA, labor laws, etc.) and provides remediation checklists.
- **Q&A RAG Agent (`qa_rag_agent.py`):** Answers user-specific legal questions grounded in retrieved legal documents and statutes, citing sources to minimize hallucinations.
- **Case Research Agent (`case_research.py`):** Fetches and summarizes relevant judicial precedents, case holdings, and legal principles.

### 4.3 Document Parsing & Vector Store (`backend/app/services/`)
- **Document Parser (`document_parser.py`):** Supports `.pdf`, `.docx`, and `.txt` uploads, chunking text with overlap for context preservation.
- **Vector Store (`vector_store.py`):** Indexes document embeddings using FAISS and `sentence-transformers` for fast semantic similarity search.

### 4.4 Frontend & API (`frontend/index.html`, `backend/app/api/routes/`)
- Clean, dark-themed single-page web interface with tabs for **Conversational Chat**, **Document Analysis**, **Compliance Check**, **Case Research**, and **Agent Status**.
- RESTful FastAPI backend (`/api/v1/chat`, `/api/v1/documents`, `/api/v1/agents`, `/api/v1/health`).
