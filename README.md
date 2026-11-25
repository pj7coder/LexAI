# AI Legal Aid Multi-Agent System
### Powered by IBM Granite · IBM WatsonX · IBM Cloud

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      LexAI Frontend                             │
│              (HTML5 Dashboard — Single Page App)                │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────────────┐
│               FastAPI Backend — Multi-Agent Orchestrator         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Agent Router / Dispatcher               │   │
│  └───┬────────────┬────────────┬──────────────┬────────────┘   │
│      │            │            │              │                 │
│  ┌───▼───┐  ┌────▼────┐ ┌────▼────┐  ┌──────▼──────┐         │
│  │Contract│  │Complian-│ │Q&A RAG  │  │  Case       │         │
│  │Review  │  │ce Check │ │ Agent   │  │ Research    │         │
│  │Agent   │  │ Agent   │ │         │  │  Agent      │         │
│  └───┬───┘  └────┬────┘ └────┬────┘  └──────┬──────┘         │
└──────┼───────────┼────────────┼──────────────┼─────────────────┘
       │           │            │              │
┌──────▼───────────▼────────────▼──────────────▼─────────────────┐
│                       IBM WatsonX                               │
│              Granite 13B Instruct LLM (ibm-granite-13b-v2)      │
└─────────────────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────────┐
│          RAG Pipeline: FAISS + Sentence Transformers            │
│          Document Parser: PDF / DOCX / TXT                      │
│          IBM Watson Discovery (optional enrichment)             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node / npm (optional — for local dev server)
- Docker + Docker Compose (for containerized run)
- IBM WatsonX API Key + Project ID

---

### Option A: Local Development (No Docker)

```bash
# 1. Clone / navigate to project
cd backend

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env — add your IBM_WATSONX_API_KEY and IBM_WATSONX_PROJECT_ID

# 5. Start the backend
python run.py
# Server starts at http://localhost:8000

# 6. Open the frontend
# Simply open frontend/index.html in your browser
# OR serve it: cd ../frontend && python -m http.server 3000
```

---

### Option B: Docker Compose

```bash
# 1. Copy and configure environment
copy backend\.env.example .env
# Edit .env with your IBM credentials

# 2. Build and start all services
docker-compose up --build

# Frontend → http://localhost:3000
# Backend API → http://localhost:8000
# API Docs → http://localhost:8000/docs
```

---

## 🔑 IBM WatsonX Configuration

| Variable | Description | Where to Get |
|---|---|---|
| `IBM_WATSONX_API_KEY` | WatsonX API key | IBM Cloud → IAM → API Keys |
| `IBM_WATSONX_PROJECT_ID` | WatsonX project ID | IBM WatsonX → Projects |
| `IBM_WATSONX_URL` | Regional endpoint | Default: `us-south.ml.cloud.ibm.com` |
| `IBM_DISCOVERY_API_KEY` | Watson Discovery key | IBM Cloud → Watson Discovery |
| `IBM_DISCOVERY_PROJECT_ID` | Discovery project | Watson Discovery Console |

---

## 🤖 Agents

| Agent | Endpoint | Description |
|---|---|---|
| **Contract Reviewer** | `POST /api/v1/agents/contract-review` | Flags risks, obligations, missing clauses |
| **Compliance Checker** | `POST /api/v1/agents/compliance-check` | GDPR, HIPAA, SOX, PCI-DSS, ISO 27001 checks |
| **Q&A RAG Agent** | `POST /api/v1/agents/qa` | Answers questions using RAG over indexed docs |
| **Case Research Agent** | `POST /api/v1/agents/case-research` | Finds relevant case law and precedents |
| **Chat (Auto-route)** | `POST /api/v1/chat/` | Routes to best agent automatically |

---

## 📄 Document Upload & RAG

```bash
# Upload a PDF to index it for RAG
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@contract.pdf" \
  -F "index=true"

# Check vector store stats
curl http://localhost:8000/api/v1/documents/stats
```

Supported formats: `.pdf`, `.docx`, `.doc`, `.txt`, `.md`

---

## 🧪 Example API Calls

### Contract Review
```bash
curl -X POST http://localhost:8000/api/v1/agents/contract-review \
  -H "Content-Type: application/json" \
  -d '{"document_text": "This agreement grants unlimited rights...", "document_name": "NDA"}'
```

### Compliance Check
```bash
curl -X POST http://localhost:8000/api/v1/agents/compliance-check \
  -H "Content-Type: application/json" \
  -d '{"document_text": "We collect user data...", "regulations": ["GDPR", "CCPA"]}'
```

### Q&A
```bash
curl -X POST http://localhost:8000/api/v1/agents/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "What constitutes a breach of contract?"}'
```

### Case Research
```bash
curl -X POST http://localhost:8000/api/v1/agents/case-research \
  -H "Content-Type: application/json" \
  -d '{"query": "data breach liability GDPR", "jurisdiction": "European Union", "legal_area": "gdpr"}'
```

---

## 🗂️ Project Structure

```
IBM BOB/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── contract_reviewer.py    # Agent 1
│   │   │   ├── compliance_checker.py   # Agent 2
│   │   │   ├── qa_rag_agent.py         # Agent 3
│   │   │   ├── case_research.py        # Agent 4
│   │   │   └── orchestrator.py         # Router
│   │   ├── api/routes/
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   ├── agents.py
│   │   │   └── health.py
│   │   ├── core/
│   │   │   ├── config.py               # Settings (Pydantic)
│   │   │   └── llm_client.py           # IBM Granite client
│   │   ├── services/
│   │   │   ├── vector_store.py         # FAISS RAG store
│   │   │   └── document_parser.py      # PDF/DOCX/TXT parser
│   │   └── main.py                     # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
├── frontend/
│   └── index.html                      # Full dashboard SPA
├── docker-compose.yml
├── nginx.conf
└── README.md
```

---

## ⚖️ Disclaimer

This system provides AI-generated legal information only. It does **not** constitute legal advice.
Always consult a qualified attorney before making legal decisions.

---

*Built for IBM Bob · IBM WatsonX · IBM Granite 13B*
