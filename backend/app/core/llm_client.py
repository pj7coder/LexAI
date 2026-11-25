"""
IBM WatsonX Granite LLM Client
Wraps ibm-watsonx-ai / langchain-ibm for inference
"""
from __future__ import annotations
import httpx
import json
from typing import AsyncGenerator

from app.core.config import settings


class GraniteLLMClient:
    """
    Thin async client for IBM WatsonX Granite models.
    Uses the WatsonX REST API directly for streaming support.
    """

    _GENERATE_URL = "{url}/ml/v1/text/generation?version=2023-05-29"
    _STREAM_URL   = "{url}/ml/v1/text/generation_stream?version=2023-05-29"
    _TOKEN_URL    = "https://iam.cloud.ibm.com/identity/token"

    def __init__(self):
        self.api_key      = settings.IBM_WATSONX_API_KEY
        self.project_id   = settings.IBM_WATSONX_PROJECT_ID
        self.base_url     = settings.IBM_WATSONX_URL.rstrip("/")
        self.model_id     = settings.GRANITE_MODEL_ID
        self._iam_token: str | None = None

    # ------------------------------------------------------------------
    # IAM token refresh
    # ------------------------------------------------------------------
    async def _get_iam_token(self) -> str:
        if self._iam_token:
            return self._iam_token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self._TOKEN_URL,
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": self.api_key,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
            resp.raise_for_status()
            self._iam_token = resp.json()["access_token"]
            return self._iam_token

    def _headers(self, token: str) -> dict:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _body(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> dict:
        return {
            "model_id": self.model_id,
            "project_id": self.project_id,
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "stop_sequences": ["</s>"],
            },
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Single-shot text generation."""
        # Fallback to mock when API key is not configured
        if not self.api_key:
            return self._mock_response(prompt)

        token = await self._get_iam_token()
        url   = self._GENERATE_URL.format(url=self.base_url)
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                url,
                headers=self._headers(token),
                json=self._body(prompt, max_tokens),
            )
            resp.raise_for_status()
            data = resp.json()
            return data["results"][0]["generated_text"].strip()

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Server-sent-events streaming generation."""
        if not self.api_key:
            yield self._mock_response(prompt)
            return

        token = await self._get_iam_token()
        url   = self._STREAM_URL.format(url=self.base_url)
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                url,
                headers=self._headers(token),
                json=self._body(prompt),
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        payload = line[5:].strip()
                        if payload and payload != "[DONE]":
                            try:
                                chunk = json.loads(payload)
                                text = chunk.get("results", [{}])[0].get("generated_text", "")
                                if text:
                                    yield text
                            except json.JSONDecodeError:
                                pass

    # ------------------------------------------------------------------
    # Mock (dev / no API key)
    # ------------------------------------------------------------------
    @staticmethod
    def _mock_response(prompt: str) -> str:
        return (
            "[DEMO MODE — IBM Granite not configured]\n\n"
            "This is a simulated response. Configure IBM_WATSONX_API_KEY and "
            "IBM_WATSONX_PROJECT_ID in your .env file to enable real AI responses.\n\n"
            f"Your prompt was received ({len(prompt)} chars). In production this would be "
            "analyzed by IBM Granite-13B-Instruct running on IBM WatsonX."
        )


# Singleton
granite_client = GraniteLLMClient()
