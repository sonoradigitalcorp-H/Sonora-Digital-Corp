import uuid
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


def gen_id(prefix: str = "CT") -> str:
    ts = int(time.time() * 1000)
    suffix = uuid.uuid4().hex[:8]
    return f"{prefix}-{ts}-{suffix}"


@dataclass
class Contact:
    crm_id: str = ""
    name: str = ""
    phone: str = ""
    company: str = ""
    email: str = ""
    instagram: str = ""
    source: str = ""  # telegram, whatsapp, web, manual
    tags: str = ""  # comma-separated
    notes: str = ""
    first_contact: float = 0.0  # unix timestamp
    last_contact: float = 0.0
    created_at: float = 0.0
    updated_at: float = 0.0
    metadata: str = ""  # JSON blob for extra data

    def __post_init__(self):
        now = time.time()
        if not self.crm_id:
            self.crm_id = gen_id()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Contact":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


ContactID = str
