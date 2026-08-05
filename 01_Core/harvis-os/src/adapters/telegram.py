"""Telegram Adapter - Integración con Telegram Bot."""

from dataclasses import dataclass
from typing import Optional, Callable
from datetime import datetime


@dataclass
class TelegramMessage:
    """Mensaje de Telegram."""
    message_id: int
    user_id: int
    username: str
    text: str
    chat_id: int
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class TelegramAdapter:
    """
    Telegram Adapter - Adaptador para Telegram Bot.

    Convierte mensajes de Telegram en IncomingRequests para el Dispatcher.
    """

    def __init__(self):
        self.token: Optional[str] = None
        self.bot_username: Optional[str] = None
        self.message_handler: Optional[Callable] = None
        self.messages: list[TelegramMessage] = []

    def configure(self, token: str, bot_username: Optional[str] = None):
        """
        Configura el adaptador de Telegram.

        Args:
            token: Token del bot de Telegram
            bot_username: Username del bot
        """
        self.token = token
        self.bot_username = bot_username

    def set_message_handler(self, handler: Callable):
        """Establece el handler para procesar mensajes."""
        self.message_handler = handler

    async def process_message(self, message: TelegramMessage) -> dict:
        """
        Procesa un mensaje de Telegram.

        Args:
            message: Mensaje de Telegram

        Returns:
            Respuesta a enviar
        """
        # Almacenar mensaje
        self.messages.append(message)

        # Si hay handler configurado, usarlo
        if self.message_handler:
            return await self.message_handler(message)

        # Respuesta por defecto
        return {
            "chat_id": message.chat_id,
            "text": f"Mensaje recibido: {message.text}",
        }

    def create_message(
        self,
        message_id: int,
        user_id: int,
        username: str,
        text: str,
        chat_id: int,
    ) -> TelegramMessage:
        """Crea un mensaje de Telegram."""
        return TelegramMessage(
            message_id=message_id,
            user_id=user_id,
            username=username,
            text=text,
            chat_id=chat_id,
        )

    def get_user_id(self, message: TelegramMessage) -> str:
        """Obtiene el ID del usuario como string."""
        return str(message.user_id)

    def get_source(self) -> str:
        """Retorna la fuente del adaptador."""
        return "telegram"

    def get_messages(
        self,
        user_id: Optional[int] = None,
        limit: int = 10,
    ) -> list[TelegramMessage]:
        """Lista mensajes con filtro."""
        messages = self.messages.copy()

        if user_id:
            messages = [m for m in messages if m.user_id == user_id]

        return messages[-limit:]

    def get_stats(self) -> dict:
        """Obtiene estadísticas del adaptador."""
        return {
            "total_messages": len(self.messages),
            "unique_users": len(set(m.user_id for m in self.messages)),
            "configured": self.token is not None,
        }
