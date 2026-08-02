from dataclasses import dataclass
from typing import Literal


MemoryType = Literal["working", "semantic", "long", "graph", "business", "event", "file"]


@dataclass
class MemoryRef:
    type: MemoryType
    key: str
    ttl: int | None = None
