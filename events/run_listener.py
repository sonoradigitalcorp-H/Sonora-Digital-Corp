#!/usr/bin/env python3
import asyncio
import logging
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from events.listener import EventListener
from events.handlers import AlertHandler, MemoryHandler, NotificationHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

log = logging.getLogger("run_listener")


async def main():
    listener = EventListener()
    listener.register_handler(AlertHandler())
    listener.register_handler(MemoryHandler())
    listener.register_handler(NotificationHandler())
    log.info("3 handlers registered: Alert, Memory, Notification")

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, listener.stop)

    await listener.poll_loop(interval=1.0)


if __name__ == "__main__":
    asyncio.run(main())
