"""Entry point: starts EventListener with registered handlers.
Usage: python -m events.run_listener
"""
import asyncio
import signal
import sys

from events.listener import EventListener
from events.handlers.alert_handler import AlertHandler
from events.handlers.memory_handler import MemoryHandler


def _signal_handler(loop, listener):
    def _stop():
        print("\n[events] Shutting down...")
        loop.create_task(listener.stop())
    return _stop


async def main():
    listener = EventListener()
    listener.register(AlertHandler())
    listener.register(MemoryHandler())
    await listener.start()
    print("[events] Event bus running. PID: %d", sys.pid if hasattr(sys, 'pid') else '?')

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(listener.stop()))

    try:
        while listener.is_running:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass

    print("[events] Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())
