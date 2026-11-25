"""
Application Configuration — reads from .env
Paths are resolved relative to the backend/ directory (parent of this file),
so the app works regardless of where uvicorn is launched from.
"""
from pydantic_settings import BaseSettings
from typing import List
import os
import pathlib

# Absolute path to the backend/ folder (two levels up from this file)
_BACKEND_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

# .env file sits inside backend/
_ENV_FILE = str(_BACKEND_DIR / ".env")


class Settings(BaseSettings):
    # Groq LLM (Primary fast inference)
    GROQ_API_KEY: str = ""
    GROQ_MODEL_ID: str = "llama-3.3-70b-versatile"

    # IBM WatsonX / Granite
    IBM_WATSONX_API_KEY: str = ""
    IBM_WATSONX_PROJECT_ID: str = ""
    IBM_WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"

    # IBM Watson Discovery
    IBM_DISCOVERY_API_KEY: str = ""
    IBM_DISCOVERY_URL: str = ""
    IBM_DISCOVERY_VERSION: str = "2023-03-31"
    IBM_DISCOVERY_PROJECT_ID: str = ""

    # App
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "change-me"
    # Accept requests from any localhost port so the plain HTML frontend works
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "null",          # file:// origin that browsers send for local HTML files
    ]

    # Storage — absolute paths so they always resolve correctly
    UPLOAD_DIR: str = str(_BACKEND_DIR / "uploads")
    VECTOR_STORE_DIR: str = str(_BACKEND_DIR / "vector_store")

    # Granite model IDs (IBM WatsonX)
    GRANITE_MODEL_ID: str = "ibm/granite-13b-instruct-v2"
    GRANITE_EMBEDDING_MODEL: str = "ibm/slate-125m-english-rtrvr"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = _ENV_FILE
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
