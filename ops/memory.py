"""SDC Memory Layer — Conversaciones por tenant.
Cada cliente tiene su propio historial (contexto + memoria).
Premium: memoria persistente entre sesiones.
Free: sin memoria (cada mensaje es nuevo).
"""
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MEMORY_DIR = BASE / "state" / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def _tenant_path(tenant_id: str) -> Path:
    return MEMORY_DIR / f"{tenant_id}.json"


def get_memory(tenant_id: str) -> list:
    """Get conversation history for a tenant."""
    path = _tenant_path(tenant_id)
    if path.exists():
        try:
            data = json.loads(path.read_text())
            return data.get("messages", [])
        except (json.JSONDecodeError, ValueError):
            return []
    return []


def save_memory(tenant_id: str, messages: list):
    """Save conversation history."""
    path = _tenant_path(tenant_id)
    path.write_text(json.dumps({
        "tenant_id": tenant_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "messages": messages[-100:],  # keep last 100
    }, indent=2))


def add_message(tenant_id: str, role: str, content: str, metadata: dict = None):
    """Add a single message to the conversation."""
    messages = get_memory(tenant_id)
    messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    })
    save_memory(tenant_id, messages)
    return messages


def clear_memory(tenant_id: str):
    """Clear conversation history for a tenant."""
    path = _tenant_path(tenant_id)
    if path.exists():
        path.unlink()


def get_context_window(tenant_id: str, limit: int = 10) -> list:
    """Get last N messages for context (for LLM)."""
    messages = get_memory(tenant_id)
    return messages[-limit:]
