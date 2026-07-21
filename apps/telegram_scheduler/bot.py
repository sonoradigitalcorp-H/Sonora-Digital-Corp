#!/usr/bin/env python3
"""Telegram Scheduler — Entry point for the message scheduler bot."""

import logging
import os
import sys
from pathlib import Path

from telegram.ext import Application

sys.path.insert(0, str(Path(__file__).parent))
import db
import handlers
import scheduler

LOG_DIR = Path(__file__).parent
LOG_FILE = LOG_DIR / "telegram_scheduler.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    logger.fatal("TELEGRAM_TOKEN environment variable not set")
    sys.exit(1)

OWNER_ID = os.environ.get("OWNER_TELEGRAM_ID")
if not OWNER_ID:
    logger.fatal("OWNER_TELEGRAM_ID environment variable not set")
    sys.exit(1)


def main() -> None:
    db.init_db()
    logger.info("Database initialized at %s", db.DB_PATH)

    app = Application.builder().token(TOKEN).build()

    handlers.register_handlers(app)
    logger.info("Handlers registered")

    scheduler.start_scheduler(app)
    logger.info("Scheduler task created")

    logger.info("Starting bot polling...")
    app.run_polling(allowed_updates=["messages"])


if __name__ == "__main__":
    main()
