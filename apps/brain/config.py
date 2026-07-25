"""Unified Brain v2 — Configuración.

Lee de environment variables con prefijo BRAIN_.
Paths adaptados para VPS.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BrainConfig:
    """Configuración del Unified Brain."""

    # Neo4j
    neo4j_uri: str = os.getenv("BRAIN_NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("BRAIN_NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("BRAIN_NEO4J_PASSWORD", "RezBcUz5ufu7AUXg1hZ3")

    # Qdrant
    qdrant_host: str = os.getenv("BRAIN_QDRANT_HOST", "localhost")
    qdrant_port: int = int(os.getenv("BRAIN_QDRANT_PORT", "6333"))

    # Engram
    engram_path: str = os.getenv("BRAIN_ENGRAM_PATH", "state/engram.db")

    # Hermes state (292MB — leer solo recientes)
    hermes_state_path: str = os.getenv(
        "BRAIN_HERMES_PATH", os.path.expanduser("~/.hermes/state.db")
    )

    # Eventos
    events_path: str = os.getenv("BRAIN_EVENTS_PATH", "state/logs/events.jsonl")

    # Lecciones
    lecciones_paths: list = field(default_factory=lambda: [
        "process/completed/20260703-unified-brain-v2/LECCION.md",
    ])

    # LLM Provider para resúmenes
    llm_provider: str = os.getenv("LLM_PROVIDER", "opencode-go")
    llm_model: str = os.getenv("LLM_MODEL", "deepseek-v4-flash")

    # Sync
    sync_interval_minutes: int = int(os.getenv("BRAIN_SYNC_INTERVAL", "30"))

    # Colección Qdrant para brain
    qdrant_collection: str = "brain-knowledge"

    def __post_init__(self):
        """Resolver paths relativos."""
        base = os.getcwd()
        if self.engram_path and not os.path.isabs(self.engram_path):
            self.engram_path = os.path.join(base, self.engram_path)
        if self.events_path and not os.path.isabs(self.events_path):
            self.events_path = os.path.join(base, self.events_path)
