"""Event Bus module - Comunicación asíncrona entre componentes."""

from .bus import EventBus, Event, EventSubscription

__all__ = ["EventBus", "Event", "EventSubscription"]
