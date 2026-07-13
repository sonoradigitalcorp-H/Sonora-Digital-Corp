"""Telegram Bot Central — entry point [FR4].

Arranca el bot como servicio independiente. Solo entrega mensajes.
"""

import asyncio
import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .handlers import message_handler, start_handler
from .message_queue import ack_outbox, poll_outbox

log = logging.getLogger("sonora.bot.main")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
OUTBOX_POLL_INTERVAL = int(os.getenv("OUTBOX_POLL_INTERVAL", "1"))  # seconds


async def outbox_worker(app: Application):
    """Background worker: poll outbox queue and send messages."""
    while True:
        try:
            messages = poll_outbox(blocking=False)
            for msg in messages:
                chat_id = msg.get("chat_id")
                text = msg.get("text", "")
                parse_mode = msg.get("parse_mode", "HTML")

                if chat_id and text:
                    try:
                        await app.bot.send_message(
                            chat_id=chat_id,
                            text=text,
                            parse_mode=parse_mode,
                        )
                    except Exception as e:
                        log.error(f"Send to {chat_id} failed: {e}")

                # Acknowledge regardless (prevents backlog)
                ack_outbox(msg.get("_id", ""))
        except Exception as e:
            log.error(f"Outbox worker error: {e}")

        await asyncio.sleep(OUTBOX_POLL_INTERVAL)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if not BOT_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN not set")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", start_handler))
    app.add_handler(MessageHandler(filters.ALL, message_handler))

    # Start outbox polling in background
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(outbox_worker(app))

    log.info("Sonora Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
