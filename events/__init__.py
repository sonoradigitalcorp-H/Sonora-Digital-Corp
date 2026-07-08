"""Event Listener System (HAS-003)
Subscribes to events.jsonl and dispatches to registered handlers.
"""
from events.listener import EventListener
from events.handlers.base import EventHandler

__all__ = ["EventListener", "EventHandler"]
