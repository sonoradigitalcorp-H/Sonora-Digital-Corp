"""Telegram bot handlers [FR4] — solo validación y reenvío a Redis.

NO contiene lógica de negocio. Todo se reenvía al engine via Redis.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from .message_queue import push_to_inbox

log = logging.getLogger("sonora.bot.handlers")

WELCOME_TEXT = (
    "¡Bienvenido a Sonora OS! 🎵\n\n"
    "Soy el bot central de la plataforma. "
    "Para comenzar, regístrate en: https://sonoraos.com/register\n\n"
    "Comandos disponibles:\n"
    "/start — Ver este mensaje\n"
    "/help — Ayuda\n\n"
    "O simplemente escríbeme lo que necesites."
)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle /start command — welcome + registration link."""
    chat_id = update.effective_chat.id if update.effective_chat else None
    if not chat_id:
        return False

    await context.bot.send_message(
        chat_id=chat_id,
        text=WELCOME_TEXT,
        parse_mode="HTML",
    )
    return True


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle incoming messages — validate type, push to Redis.

    Solo mensajes de texto se reenvían al engine.
    Fotos, stickers, etc. reciben respuesta automática.
    """
    chat_id = update.effective_chat.id if update.effective_chat else 0
    user_id = update.effective_user.id if update.effective_user else 0
    message_id = update.effective_message.message_id if update.effective_message else 0

    # Detect message type
    if update.message and update.message.text:
        message_type = "text"
        text = update.message.text
    elif update.message and update.message.photo:
        message_type = "photo"
        text = None
    elif update.message and (update.message.sticker or update.message.dice):
        message_type = "sticker"
        text = None
    elif update.message and update.message.voice:
        message_type = "voice"
        text = None
    elif update.message and update.message.video:
        message_type = "video"
        text = None
    else:
        message_type = "unknown"
        text = None

    # Non-text messages get immediate response
    non_text_types = {"photo", "sticker", "voice", "video", "unknown"}
    if message_type in non_text_types:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Solo proceso mensajes de texto por ahora. "
                 "Escribe lo que necesites y te ayudaré.",
        )
        return True

    # Push text message to Redis inbox (engine processes it)
    pushed = push_to_inbox(
        chat_id=chat_id,
        text=text,
        user_id=user_id,
        message_id=message_id,
        message_type=message_type,
    )

    if not pushed:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Estoy teniendo problemas de conexión. Intenta de nuevo en un momento.",
        )

    # Bot does NOT respond directly — engine will respond via outbox
    return True
