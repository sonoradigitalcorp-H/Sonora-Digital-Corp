"""OpenClaw Integration - Verificación de integración con OpenClaw y LLM."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import json


@dataclass
class OpenClawMessage:
    """Mensaje de OpenClaw."""
    id: str
    direction: str = "inbound"  # "inbound" o "outbound"
    source: str = ""
    content: str = ""
    metadata: dict = field(default_factory=dict)
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class LLMResponse:
    """Respuesta del LLM."""
    model: str
    content: str
    tokens_used: int
    latency_ms: float
    success: bool
    error: Optional[str] = None


class OpenClawIntegration:
    """
    OpenClaw Integration - Verifica la integración con OpenClaw y LLM.

    Verifica:
    - Recepción de mensajes
    - Envío de respuestas
    - Integración con LLM
    - Procesamiento de comandos
    """

    def __init__(self):
        self.messages: list[OpenClawMessage] = []
        self.llm_responses: list[LLMResponse] = []
        self.config = {
            "llm_enabled": True,
            "llm_model": "qwen2.5:1.5b",
            "llm_url": "http://localhost:11434",
            "openclaw_enabled": True,
            "openclaw_url": "http://localhost:18789",
        }

    def receive_message(self, message: OpenClawMessage) -> bool:
        """
        Recibe un mensaje de OpenClaw.

        Args:
            message: Mensaje recibido

        Returns:
            True si se procesó correctamente
        """
        message.direction = "inbound"
        self.messages.append(message)
        return True

    def send_message(self, message: OpenClawMessage) -> bool:
        """
        Envía un mensaje a OpenClaw.

        Args:
            message: Mensaje a enviar

        Returns:
            True si se envió correctamente
        """
        message.direction = "outbound"
        self.messages.append(message)
        return True

    def process_with_llm(self, content: str, model: str = None) -> LLMResponse:
        """
        Procesa contenido con el LLM.

        Args:
            content: Contenido a procesar
            model: Modelo a usar (opcional)

        Returns:
            LLMResponse con la respuesta
        """
        import time
        start = time.time()

        model = model or self.config["llm_model"]

        try:
            # Simular procesamiento LLM
            # En producción, esto se conectaría a Ollama
            response = LLMResponse(
                model=model,
                content=f"Processed: {content}",
                tokens_used=len(content.split()),
                latency_ms=(time.time() - start) * 1000,
                success=True,
            )
        except Exception as e:
            response = LLMResponse(
                model=model,
                content="",
                tokens_used=0,
                latency_ms=(time.time() - start) * 1000,
                success=False,
                error=str(e),
            )

        self.llm_responses.append(response)
        return response

    def get_messages(
        self,
        direction: Optional[str] = None,
        limit: int = 10,
    ) -> list[OpenClawMessage]:
        """Obtiene mensajes filtrados."""
        messages = self.messages
        if direction:
            messages = [m for m in messages if m.direction == direction]
        return messages[-limit:]

    def get_llm_stats(self) -> dict:
        """Obtiene estadísticas del LLM."""
        total = len(self.llm_responses)
        successful = sum(1 for r in self.llm_responses if r.success)
        avg_latency = (
            sum(r.latency_ms for r in self.llm_responses) / total
            if total > 0
            else 0
        )

        return {
            "total_requests": total,
            "successful": successful,
            "failed": total - successful,
            "avg_latency_ms": avg_latency,
            "models_used": list(set(r.model for r in self.llm_responses)),
        }

    def verify_integration(self) -> dict:
        """
        Verifica el estado de la integración.

        Returns:
            Dict con estado de cada componente
        """
        return {
            "openclaw": {
                "enabled": self.config["openclaw_enabled"],
                "url": self.config["openclaw_url"],
                "messages_received": len([m for m in self.messages if m.direction == "inbound"]),
                "messages_sent": len([m for m in self.messages if m.direction == "outbound"]),
            },
            "llm": {
                "enabled": self.config["llm_enabled"],
                "model": self.config["llm_model"],
                "url": self.config["llm_url"],
                "stats": self.get_llm_stats(),
            },
            "integration_status": "healthy" if self.config["openclaw_enabled"] and self.config["llm_enabled"] else "degraded",
        }


class OpenClawBridge:
    """
    OpenClaw Bridge - Puente entre OpenClaw y Harvis OS.

    Convierte mensajes de OpenClaw a formato Harvis y viceversa.
    """

    def __init__(self):
        self.integration = OpenClawIntegration()

    def handle_inbound(self, raw_message: dict) -> dict:
        """
        Maneja mensaje entrante de OpenClaw.

        Args:
            raw_message: Mensaje raw de OpenClaw

        Returns:
            Respuesta formateada
        """
        # Convertir a formato OpenClawMessage
        message = OpenClawMessage(
            id=raw_message.get("id", "unknown"),
            source=raw_message.get("source", "openclaw"),
            content=raw_message.get("content", ""),
            metadata=raw_message.get("metadata", {}),
        )

        # Recibir mensaje
        self.integration.receive_message(message)

        # Procesar con LLM si es necesario
        if self.integration.config["llm_enabled"]:
            llm_response = self.integration.process_with_llm(message.content)

            # Enviar respuesta
            response = OpenClawMessage(
                id=f"response_{message.id}",
                source="harvis",
                content=llm_response.content,
                metadata={"llm_model": llm_response.model},
            )
            self.integration.send_message(response)

            return {
                "status": "processed",
                "response": llm_response.content,
                "model": llm_response.model,
            }

        return {"status": "processed", "response": "LLM disabled"}

    def get_status(self) -> dict:
        """Obtiene estado de la integración."""
        return self.integration.verify_integration()
