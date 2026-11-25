# Technology Used — LexAI

## 1. AI & Large Language Models
| Technology | Purpose |
|---|---|
| **IBM watsonx.ai (`ibm-watson`, `langchain-ibm`)** | Enterprise LLM inference platform powering the multi-agent system |
| **IBM Granite (`ibm/granite-3-8b-instruct`)** | Foundation model for legal reasoning, summarization, and plain-English explanation |
| **LangChain (`langchain`, `langchain-community`)** | Prompt orchestration, RAG chains, and agent abstractions |

## 2. Retrieval-Augmented Generation (RAG) & NLP
| Technology | Purpose |
|---|---|
| **FAISS (`faiss-cpu`)** | High-speed local vector similarity search for legal corpora and uploaded documents |
| **SentenceTransformers (`sentence-transformers`)** | Dense vector embeddings for semantic retrieval |
| **Tiktoken (`tiktoken`)** | Token counting and context-window management |
| **NumPy (`numpy`)** | Numerical operations for vector indexing |

## 3. Backend & API
| Technology | Purpose |
|---|---|
| **FastAPI (`fastapi`)** | High-performance async Python web framework for REST APIs |
| **Uvicorn (`uvicorn[standard]`)** | ASGI server for local and containerized execution |
| **Pydantic & Pydantic Settings (`pydantic`, `pydantic-settings`)** | Request/response validation and environment configuration |
| **HTTPX (`httpx`)** | Async HTTP client for external service calls |
| **AIOFiles (`aiofiles`)** | Non-blocking file I/O for document uploads |

## 4. Document Parsing
| Technology | Purpose |
|---|---|
| **PyPDF2 & pdfplumber** | Text and table extraction from PDF contracts and legal notices |
| **python-docx & docx2txt** | Parsing `.docx` Word documents |
| **BeautifulSoup4 & lxml** | HTML/XML parsing for structured legal texts |

## 5. Frontend
| Technology | Purpose |
|---|---|
| **HTML5, CSS3, Vanilla JavaScript** | Lightweight, zero-build-step responsive SPA (`frontend/index.html`) |

## 6. Deployment & Infrastructure
| Technology | Purpose |
|---|---|
| **Vercel** | Cloud hosting for the frontend and serverless Python API |
| **Docker & Docker Compose (`Dockerfile`, `docker-compose.yml`)** | Containerized local/cloud deployment |
| **Nginx (`nginx.conf`)** | Reverse proxy for production container setups |
| **Redis & Celery (`redis`, `celery`)** | Optional async task queue for heavy background document processing |
