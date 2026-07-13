"""Redis queue operations for Telegram bot [FR4].

El bot SOLO escribe a telegram:inbox y lee de telegram:outbox.
Cero lógica de negocio aquí — solo entrega de mensajes.
"""

import json
import logging
import os
from typing import Any

import redis

log = logging.getLogger("sonora.bot.queue")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
INBOX_KEY = "telegram:inbox"
OUTBOX_KEY = "telegram:outbox"


def _get_redis():
    return redis.Redis.from_url(REDIS_URL, decode_responses=False)


def push_to_inbox(
    chat_id: int,
    text: str | None,
    user_id: int,
    message_id: int,
    message_type: str = "text",
    **extra,
) -> bool:
    """Push incoming message to Redis queue for LangChain engine."""
    try:
        r = _get_redis()
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "message_id": message_id,
            "type": message_type,
            "text": text or "",
        }
        data.update(extra)
        r.xadd(INBOX_KEY, data, maxlen=10000)
        return True
    except Exception as e:
        log.error(f"Redis push failed: {e}")
        return False


def poll_outbox(blocking: bool = True, timeout: int = 5) -> list[dict[str, Any]]:
    """Poll outbox queue for messages to send."""
    try:
        r = _get_redis()
        result = r.xread({OUTBOX_KEY: "0-0"}, count=10, block=timeout * 1000 if blocking else 0)
        messages = []
        for stream_key, entries in result:
            for entry_id, data in entries:
                decoded = {k.decode(): v.decode() if isinstance(v, bytes) else v for k, v in data.items()}
                decoded["_id"] = entry_id.decode()
                decoded["chat_id"] = int(decoded.get("chat_id", 0))
                messages.append(decoded)
        return messages
    except Exception as e:
        log.error(f"Redis poll failed: {e}")
        return []


def ack_outbox(message_id: str) -> bool:
    """Acknowledge (delete) a processed outbox message."""
    try:
        r = _get_redis()
        r.xdel(OUTBOX_KEY, message_id)
        return True
    except Exception as e:
        log.error(f"Redis ack failed: {e}")
        return False


ack_message = ack_outbox
