"""Ollama Connector - Integración con Ollama LLM."""

import httpx
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime


@dataclass
class OllamaConfig:
    """Configuración de Ollama."""
    base_url: str = "http://localhost:11434"
    model: str = "qwen3:4b"
    system_prompt: str = "Eres HERMES, asistente de IA de Sonora Digital Corp."
    timeout: float = 120.0
    max_tokens: int = 800


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
    total_duration: int = 0
    eval_count: int = 0
    prompt_eval_count: int = 0


class OllamaConnector:
    """
    Ollama Connector - Integración con Ollama LLM.

    Permite:
    - Chat con modelos locales
    - Generación de embeddings
    - Health checks
    - Listado de modelos
    """

    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.client = httpx.Client(timeout=self.config.timeout)
        self._available_models: list[str] = []

    async def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        options: Optional[dict] = None,
    ) -> ChatResponse:
        """
        Envía mensajes y obtiene respuesta.

        Args:
            messages: Lista de mensajes [{role, content}]
            model: Modelo a usar (opcional)
            options: Opciones adicionales

        Returns:
            ChatResponse con la respuesta
        """
        model = model or self.config.model

        # Agregar system prompt si no existe
        if not messages or messages[0].get("role") != "system":
            messages = [{"role": "system", "content": self.config.system_prompt}] + messages

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": self.config.max_tokens,
                **(options or {}),
            },
        }

        try:
            response = self.client.post(
                f"{self.config.base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            return ChatResponse(
                content=data.get("message", {}).get("content", ""),
                model=model,
                total_duration=data.get("total_duration", 0),
                eval_count=data.get("eval_count", 0),
                prompt_eval_count=data.get("prompt_eval_count", 0),
            )

        except httpx.HTTPError as e:
            return ChatResponse(
                content=f"Error: {str(e)}",
                model=model,
            )

    async def embedding(self, text: str, model: Optional[str] = None) -> list[float]:
        """
        Obtiene embedding de texto.

        Args:
            text: Texto a procesar
            model: Modelo de embeddings

        Returns:
            Lista de floats con el embedding
        """
        model = model or "nomic-embed-text"

        payload = {
            "model": model,
            "prompt": text,
        }

        try:
            response = self.client.post(
                f"{self.config.base_url}/api/embeddings",
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            return data.get("embedding", [])

        except httpx.HTTPError:
            return []

    def health_check(self) -> dict:
        """
        Verifica salud de Ollama.

        Returns:
            Dict con estado de salud
        """
        try:
            response = self.client.get(f"{self.config.base_url}/api/tags")
            response.raise_for_status()

            data = response.json()
            models = [m["name"] for m in data.get("models", [])]

            return {
                "status": "healthy",
                "url": self.config.base_url,
                "models_available": len(models),
                "models": models,
            }

        except httpx.HTTPError as e:
            return {
                "status": "unhealthy",
                "url": self.config.base_url,
                "error": str(e),
            }

    def list_models(self) -> list[str]:
        """
        Lista modelos disponibles.

        Returns:
            Lista de nombres de modelos
        """
        try:
            response = self.client.get(f"{self.config.base_url}/api/tags")
            response.raise_for_status()

            data = response.json()
            self._available_models = [m["name"] for m in data.get("models", [])]
            return self._available_models

        except httpx.HTTPError:
            return []

    def is_model_available(self, model: str) -> bool:
        """Verifica si un modelo está disponible."""
        if not self._available_models:
            self.list_models()
        return model in self._available_models

    def close(self):
        """Cierra el cliente HTTP."""
        self.client.close()
