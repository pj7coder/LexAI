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


async def ocr_image(content: bytes, mime_type: str = "image/png") -> str:
    """Extract text from an image using Groq Vision OCR (with pytesseract fallback)."""
    import base64
    from app.core.config import settings

    if settings.GROQ_API_KEY:
        import httpx
        b64 = base64.b64encode(content).decode("utf-8")
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extract all text from this legal document image verbatim. Preserve structure."},
                                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
                            ],
                        }
                    ],
                    "max_tokens": 2048,
                },
            )
            resp.raise_for_status()
            return clean_text(resp.json()["choices"][0]["message"]["content"])

    try:
        import pytesseract
        from PIL import Image
        img = Image.open(io.BytesIO(content))
        return clean_text(pytesseract.image_to_string(img))
    except Exception as e:
        raise ValueError(f"OCR failed (configure GROQ_API_KEY or install pytesseract): {e}")


async def parse_document(filename: str, content: bytes) -> str:
    """Dispatch to the right parser based on file extension."""
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return await parse_pdf(content)
    elif ext in ("docx", "doc"):
        return await parse_docx(content)
    elif ext in ("txt", "md"):
        return clean_text(content.decode("utf-8", errors="ignore"))
    elif ext in ("png", "jpg", "jpeg", "webp"):
        mime = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"
        return await ocr_image(content, mime_type=mime)
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
