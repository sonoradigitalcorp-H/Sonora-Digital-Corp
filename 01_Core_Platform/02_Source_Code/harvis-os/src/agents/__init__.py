"""Agents module - Wrappers para agentes externos."""

from .base import BaseAgent
from .openhands import OpenHandsAgent
from .opencode import OpenCodeAgent
from .hermes import HermesAgent
from .aider import AiderAgent

__all__ = [
    "BaseAgent",
    "OpenHandsAgent",
    "OpenCodeAgent",
    "HermesAgent",
    "AiderAgent",
]
