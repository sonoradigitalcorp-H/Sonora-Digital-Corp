"""Context Engine — Module 1 of Kernel (HAS-004)
Builds working context from input + memory + constitution + session.
Tenant-aware via TenantManager (HAS-011).
"""
import yaml
from datetime import datetime, timezone
from pathlib import Path

from kernel.models import HermesContext
from memory import MemoryRouter, MemoryRef
from memory.stores import WorkingMemory, BusinessMemory, LongMemory, SemanticMemory, EventMemory, FileMemory
from memory.tenant import TenantAwareStore


REPO = Path(__file__).resolve().parent.parent


class ContextEngine:
    def __init__(self, tenant_manager=None):
        self._constitution_cache: list[dict] | None = None
        self._session_store: dict[str, list[dict]] = {}
        self._memory = MemoryRouter()
        self._tenant_manager = tenant_manager
        self._init_memory()

    def _init_memory(self):
        store_dir = REPO / "state" / "memory"
        self._memory.register("working", WorkingMemory(store_dir))
        self._memory.register("long", LongMemory())
        self._memory.register("business", BusinessMemory(REPO / "state" / "business"))
        self._memory.register("semantic", SemanticMemory(REPO / "state" / "semantic"))
        self._memory.register("event", EventMemory())
        self._memory.register("file", FileMemory(REPO / "state" / "files"))

    def _get_tenant_store(self, store_type: str, tenant_id: str):
        store = self._memory.get_store(store_type)
        if not store:
            return None
        return TenantAwareStore(store, tenant_id)

    async def build(self, raw: dict) -> HermesContext:
        tenant = raw.get("tenant", "default")
        if tenant == "default":
            tenant = "abe-music"
        if self._tenant_manager:
            if not self._tenant_manager.is_enabled(tenant):
                raise ValueError(f"Tenant '{tenant}' is not enabled")
        ctx = HermesContext(
            input=raw.get("input", ""),
            channel=raw.get("channel", "api"),
            tenant=tenant,
            user_id=raw.get("user_id", ""),
            conversation_id=raw.get("conversation_id", ""),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        ctx.constitution_rules = self._load_constitution()
        ctx.working_memory = self._get_session(ctx.conversation_id)
        ctx.memory_router = self._memory
        ctx.tenant_manager = self._tenant_manager
        return ctx

    def _load_constitution(self) -> list[dict]:
        if self._constitution_cache is not None:
            return self._constitution_cache
        rules = []
        const_dir = REPO / "constitution"
        if const_dir.exists():
            for f in sorted(const_dir.glob("*.yaml")):
                try:
                    data = yaml.safe_load(f.read_text())
                    rules.extend(data.get("rules", []))
                except Exception:
                    pass
        self._constitution_cache = rules
        return rules

    def _get_session(self, conversation_id: str) -> list[dict]:
        return self._session_store.get(conversation_id, [])

    def append_session(self, conversation_id: str, entry: dict):
        if conversation_id not in self._session_store:
            self._session_store[conversation_id] = []
        self._session_store[conversation_id].append(entry)

    def get_stats(self) -> dict:
        return {
            "sessions": len(self._session_store),
            "constitution_rules_loaded": len(self._constitution_cache or []),
        }
