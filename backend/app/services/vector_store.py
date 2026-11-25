"""
Vector Store Service — FAISS + Sentence Transformers
Used by the RAG pipeline for semantic legal document retrieval.
"""
from __future__ import annotations
import os
import pickle
import asyncio
from typing import List, Tuple

import numpy as np

from app.core.config import settings


class VectorStoreService:
    """
    In-process FAISS vector store.
    Falls back gracefully when faiss/sentence-transformers are unavailable.
    """

    _index = None
    _documents: List[dict] = []
    _embedder = None
    _initialized: bool = False

    @classmethod
    async def initialize(cls):
        """Load or create the FAISS index on startup."""
        if cls._initialized:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, cls._load_or_create)
        cls._initialized = True

    # ------------------------------------------------------------------
    # Sync helpers (run in executor)
    # ------------------------------------------------------------------
    @classmethod
    def _load_or_create(cls):
        try:
            import faiss  # noqa: F401
            from sentence_transformers import SentenceTransformer
            cls._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            cls._embedder = None
            return

        index_path = os.path.join(settings.VECTOR_STORE_DIR, "legal.index")
        docs_path  = os.path.join(settings.VECTOR_STORE_DIR, "legal_docs.pkl")

        if os.path.exists(index_path) and os.path.exists(docs_path):
            import faiss
            cls._index = faiss.read_index(index_path)
            with open(docs_path, "rb") as f:
                cls._documents = pickle.load(f)
        else:
            import faiss
            cls._index = faiss.IndexFlatL2(384)   # all-MiniLM-L6-v2 dim
            cls._documents = []

    @classmethod
    def _save(cls):
        import faiss
        os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
        faiss.write_index(
            cls._index,
            os.path.join(settings.VECTOR_STORE_DIR, "legal.index"),
        )
        with open(os.path.join(settings.VECTOR_STORE_DIR, "legal_docs.pkl"), "wb") as f:
            pickle.dump(cls._documents, f)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @classmethod
    async def add_documents(cls, chunks: List[dict]):
        """
        Add text chunks to the index.
        Each chunk: {"text": str, "source": str, "metadata": dict}
        """
        if cls._embedder is None:
            cls._documents.extend(chunks)
            return

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, cls._add_documents_sync, chunks)

    @classmethod
    def _add_documents_sync(cls, chunks: List[dict]):
        texts = [c["text"] for c in chunks]
        embeddings = cls._embedder.encode(texts, normalize_embeddings=True)
        cls._index.add(np.array(embeddings, dtype="float32"))
        cls._documents.extend(chunks)
        cls._save()

    @classmethod
    async def search(cls, query: str, top_k: int = 5) -> List[Tuple[dict, float]]:
        """Return top-k most relevant chunks for a query."""
        if cls._embedder is None or not cls._documents:
            return []

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, cls._search_sync, query, top_k)

    @classmethod
    def _search_sync(cls, query: str, top_k: int) -> List[Tuple[dict, float]]:
        query_vec = cls._embedder.encode([query], normalize_embeddings=True)
        distances, indices = cls._index.search(
            np.array(query_vec, dtype="float32"), top_k
        )
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(cls._documents):
                results.append((cls._documents[idx], float(dist)))
        return results

    @classmethod
    def document_count(cls) -> int:
        return len(cls._documents)
