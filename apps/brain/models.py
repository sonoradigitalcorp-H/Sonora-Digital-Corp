from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

class KnowledgeType(str, Enum):
    SPEC = "spec"
    SERVICE = "service"
    PERSON = "person"
    ARTIST = "artist"
    SESSION = "session"
    MEMORY = "memory"
    RULE = "rule"
    EVENT = "event"
    LECCION = "leccion"
    ACHIEVEMENT = "achievement"
    CAPABILITY = "capability"
    MACHINE = "machine"

@dataclass
class KnowledgeNode:
    id: str
    type: KnowledgeType
    label: str
    summary: str
    details: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    importance: int = 1
    embedding: Optional[list[float]] = None
    source: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class KnowledgeRelation:
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
