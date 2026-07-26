"""Unified Brain v2 — Modelos de datos."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class KnowledgeNode:
    """Nodo de conocimiento unificado.

    Puede venir de Engram, Neo4j, Qdrant, Hermes, eventos, o lecciones.
    """
    id: str
    type: str  # MEMORY | SERVICE | SPEC | PERSON | EVENT | SESSION | LECCION | ACHIEVEMENT
    label: str
    content: str
    source: str  # engram | neo4j | qdrant | hermes | events | lecciones | truth
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: list = field(default_factory=list)
    score: float = 0.0  # Relevancia para la consulta
    metadata: dict = field(default_factory=dict)


@dataclass
class BrainQuery:
    """Consulta al cerebro unificado."""
    text: str
    mode: str = "auto"  # auto | semantic | graph | fts
    limit: int = 10
    source: Optional[str] = None  # Filtrar por fuente
    type_filter: Optional[str] = None  # Filtrar por tipo


@dataclass
class BrainResult:
    """Resultado de una consulta al cerebro."""
    query: str
    mode: str
    results: list = field(default_factory=list)
    total: int = 0
    elapsed_ms: int = 0
    sources_queried: list = field(default_factory=list)


@dataclass
class SyncStatus:
    """Estado de la sincronización."""
    last_sync: Optional[str] = None
    ingestor_results: dict = field(default_factory=dict)
    total_nodes: int = 0
    errors: list = field(default_factory=list)
