"""Base class for event handlers."""
from abc import ABC, abstractmethod
from typing import Any


class EventHandler(ABC):
    name: str = ""

    @abstractmethod
    async def handle(self, event: dict) -> None:
        """Process a single event."""
