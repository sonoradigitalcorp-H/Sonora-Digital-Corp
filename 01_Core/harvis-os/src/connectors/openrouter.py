"""OpenRouter Connector - Integración con OpenRouter API."""

import httpx
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime
import os


@dataclass
class OpenRouterConfig:
    """Configuración de OpenRouter."""
    api_key: str = ""
    base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "deepseek/deepseek-v4-flash"
    timeout: float = 60.0
    max_tokens: int = 1000

    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.environ.get("OPENROUTER_API_KEY", "")


@dataclass
class ChatMessage:
    """Mensaje de chat."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class ChatResponse:
    """Respuesta de chat."""
    content: str
    model: str
    tokens_used: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    duration_ms: float = 0
    success: bool = True
    error: Optional[str] = None


# Modelos baratos recomendados
CHEAP_MODELS = {
    "deepseek-v4-flash": "deepseek/deepseek-v4-flash",
    "deepseek-flash-free": "deepseek/deepseek-chat-v3-0324:free",
    "deepseek-r1-free": "deepseek/deepseek-r1-0528:free",
    "gemma3-4b": "google/gemma-3-4b-it:free",
    "qwen3-8b": "qwen/qwen3-8b:free",
    "llama3-8b": "meta-llama/llama-3.3-8b-instruct:free",
    "mistral-small": "mistralai/mistral-small-3.2-24b:free",
}


class OpenRouterConnector:
    """
    OpenRouter Connector - Integración con OpenRouter.

    Permite usar modelos baratos como DeepSeek V4 Flash.
    """

    def __init__(self, config: Optional[OpenRouterConfig] = None):
        self.config = config or OpenRouterConfig()
        self.client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "HTTP-Referer": "https://harvis-os.local",
                "X-Title": "Harvis OS",
            },
        )

    async def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> ChatResponse:
        """
        Envía chat y obtiene respuesta.

        Args:
            messages: Lista de mensajes [{role, content}]
            model: Modelo a usar
            max_tokens: Máximo de tokens
            temperature: Temperatura

        Returns:
            ChatResponse con la respuesta
        """
        import time
        start = time.time()

        model = model or self.config.default_model
        max_tokens = max_tokens or self.config.max_tokens

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response = self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})

            return ChatResponse(
                content=content,
                model=model,
                tokens_used=usage.get("total_tokens", 0),
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                duration_ms=(time.time() - start) * 1000,
                success=True,
            )

        except httpx.HTTPError as e:
            return ChatResponse(
                content="",
                model=model,
                duration_ms=(time.time() - start) * 1000,
                success=False,
                error=str(e),
            )

    def list_models(self) -> list[dict]:
        """Lista modelos disponibles."""
        try:
            response = self.client.get("/models")
            response.raise_for_status()
            return response.json().get("data", [])
        except httpx.HTTPError:
            return []

    def health_check(self) -> dict:
        """Verifica salud de OpenRouter."""
        try:
            response = self.client.get("/models")
            response.raise_for_status()
            return {
                "status": "healthy",
                "api_key_configured": bool(self.config.api_key),
                "default_model": self.config.default_model,
            }
        except httpx.HTTPError as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def close(self):
        """Cierra el cliente HTTP."""
        self.client.close()
