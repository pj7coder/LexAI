"""
Document Parser Service
Handles PDF, DOCX, and plain text extraction + chunking.
"""
from __future__ import annotations
import io
import re
from typing import List


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks."""
    words  = text.split()
    chunks = []
    start  = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def clean_text(raw: str) -> str:
    """Remove excessive whitespace and non-printable characters."""
    text = re.sub(r"\s+", " ", raw)
    text = re.sub(r"[^\x20-\x7E\n]", "", text)
    return text.strip()


async def parse_pdf(content: bytes) -> str:
    """Extract text from a PDF file."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return clean_text("\n".join(pages))
    except Exception:
        # Fallback to PyPDF2
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            pages  = [p.extract_text() or "" for p in reader.pages]
            return clean_text("\n".join(pages))
        except Exception as e:
            raise ValueError(f"Could not parse PDF: {e}")


async def parse_docx(content: bytes) -> str:
    """Extract text from a DOCX file."""
    try:
        import docx2txt
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        text = docx2txt.process(tmp_path)
        os.unlink(tmp_path)
        return clean_text(text)
    except Exception as e:
        raise ValueError(f"Could not parse DOCX: {e}")


async def parse_document(filename: str, content: bytes) -> str:
    """Dispatch to the right parser based on file extension."""
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return await parse_pdf(content)
    elif ext in ("docx", "doc"):
        return await parse_docx(content)
    elif ext in ("txt", "md"):
        return clean_text(content.decode("utf-8", errors="ignore"))
    else:
        raise ValueError(f"Unsupported file type: .{ext}")


def chunk_document(text: str, source: str, metadata: dict | None = None) -> List[dict]:
    """Return a list of chunk dicts ready for the vector store."""
    chunks = _chunk_text(text)
    return [
        {
            "text": chunk,
            "source": source,
            "metadata": metadata or {},
            "chunk_index": i,
        }
        for i, chunk in enumerate(chunks)
    ]
