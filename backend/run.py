"""
AI Legal Aid Multi-Agent System — Backend Entry Point

Always run this file directly:
    python run.py              (from anywhere)
    python backend/run.py      (from project root)

It sets the working directory to backend/ before starting uvicorn,
so relative paths and .env discovery always work correctly.
"""
import os
import sys
import pathlib
import uvicorn

# ── Resolve the backend/ directory (the folder that contains this file) ──────
BACKEND_DIR = pathlib.Path(__file__).resolve().parent

# Change cwd to backend/ so uvicorn watch, .env loading, etc. all work
os.chdir(BACKEND_DIR)

# Make sure backend/ is on sys.path so "from app.xxx import ..." works
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

if __name__ == "__main__":
    print(f"[LexAI] Starting server from: {BACKEND_DIR}")
    print(f"[LexAI] API docs: http://127.0.0.1:8000/docs")
    print(f"[LexAI] Open frontend/index.html in your browser to use the dashboard.\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(BACKEND_DIR / "app")],  # only watch app/ — not system dirs
        log_level="info",
    )
