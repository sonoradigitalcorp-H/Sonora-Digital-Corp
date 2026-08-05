"""Telegram Connector - Integración con Telegram Bot."""

import httpx
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from datetime import datetime


@dataclass
class TelegramConfig:
    """Configuración de Telegram."""
    bot_token: str
    api_url: str = "https://api.telegram.org"
    timeout: float = 30.0


@dataclass
class TelegramMessage:
    """Mensaje de Telegram."""
    message_id: int
    chat_id: str
    user_id: str
    username: str
    text: str
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class TelegramConnector:
    """
    Telegram Connector - Integración con Telegram Bot.

    Permite:
    - Enviar mensajes
    - Enviar notas de voz
    - Recibir mensajes
    - Gestión de callbacks
    """

    def __init__(self, config: TelegramConfig):
        self.config = config
        self.client = httpx.Client(
            base_url=f"{config.api_url}/bot{config.bot_token}",
            timeout=config.timeout,
        )
        self._handlers: list[Callable] = []
        self._messages: list[TelegramMessage] = []

    async def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = None,
        reply_to: int = None,
    ) -> bool:
        """
        Envía mensaje a Telegram.

        Args:
            chat_id: ID del chat
            text: Texto del mensaje
            parse_mode: Modo de parseo (HTML, Markdown)
            reply_to: ID del mensaje a responder

        Returns:
            True si se envió correctamente
        """
        payload = {
            "chat_id": chat_id,
            "text": text,
        }

        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_to:
            payload["reply_to_message_id"] = reply_to

        try:
            response = self.client.post("/sendMessage", json=payload)
            response.raise_for_status()

            # Registrar mensaje enviado
            msg = TelegramMessage(
                message_id=response.json().get("result", {}).get("message_id", 0),
                chat_id=chat_id,
                user_id="bot",
                username="harvis",
                text=text,
            )
            self._messages.append(msg)

            return True

        except httpx.HTTPError:
            return False

    async def send_voice(self, chat_id: str, audio_path: str) -> bool:
        """
        Envía nota de voz.

        Args:
            chat_id: ID del chat
            audio_path: Ruta del archivo de audio

        Returns:
            True si se envió correctamente
        """
        try:
            with open(audio_path, "rb") as f:
                files = {"voice": f}
                data = {"chat_id": chat_id}
                response = self.client.post("/sendVoice", files=files, data=data)
                response.raise_for_status()
                return True

        except (httpx.HTTPError, FileNotFoundError):
            return False

    async def send_document(
        self,
        chat_id: str,
        file_path: str,
        caption: str = None,
    ) -> bool:
        """
        Envía documento.

        Args:
            chat_id: ID del chat
            file_path: Ruta del archivo
            caption: Caption del documento

        Returns:
            True si se envió correctamente
        """
        try:
            with open(file_path, "rb") as f:
                files = {"document": f}
                data = {"chat_id": chat_id}
                if caption:
                    data["caption"] = caption
                response = self.client.post("/sendDocument", files=files, data=data)
                response.raise_for_status()
                return True

        except (httpx.HTTPError, FileNotFoundError):
            return False

    def on_message(self, handler: Callable):
        """Registra handler para mensajes entrantes."""
        self._handlers.append(handler)

    def process_update(self, update: dict):
        """
        Procesa un update de Telegram.

        Args:
            update: Update de Telegram
        """
        message = update.get("message")
        if not message:
            return

        chat = message.get("chat", {})
        user = message.get("from", {})

        msg = TelegramMessage(
            message_id=message.get("message_id", 0),
            chat_id=str(chat.get("id", "")),
            user_id=str(user.get("id", "")),
            username=user.get("username", ""),
            text=message.get("text", ""),
        )

        self._messages.append(msg)

        # Notificar handlers
        for handler in self._handlers:
            try:
                handler(msg)
            except Exception:
                pass

    def get_messages(
        self,
        chat_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[TelegramMessage]:
        """Obtiene mensajes filtrados."""
        messages = self._messages
        if chat_id:
            messages = [m for m in messages if m.chat_id == chat_id]
        return messages[-limit:]

    def get_stats(self) -> dict:
        """Obtiene estadísticas."""
        return {
            "total_messages": len(self._messages),
            "handlers_registered": len(self._handlers),
        }

    def close(self):
        """Cierra el cliente HTTP."""
        self.client.close()
