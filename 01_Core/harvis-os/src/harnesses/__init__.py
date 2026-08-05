"""Agent Harnesses - Marcos de test para agentes."""

from .base import AgentHarness, MockAgent
from .openhands import OpenHandsHarness
from .opencode import OpenCodeHarness
from .hermes import HermesHarness
from .aider import AiderHarness

__all__ = [
    "AgentHarness",
    "MockAgent",
    "OpenHandsHarness",
    "OpenCodeHarness",
    "HermesHarness",
    "AiderHarness",
]
