"""Capability Bus — HAS-005
The runtime that connects agents to capabilities.
"""
import importlib.util
import inspect
import sys
import yaml
from pathlib import Path
from typing import Any

from kernel.models import ExecutionResult

REPO = Path(__file__).resolve().parent.parent

CAPABILITY_HANDLER_PATH = "skills/handler.py"


class CapabilityManifest:
    def __init__(self, data: dict):
        self.id: str = data.get("id", "")
        self.name: str = data.get("name", "")
        self.version: str = data.get("version", "0.0.1")
        self.status: str = data.get("status", "experimental")
        self.domain: str = data.get("domain", "")
        self.description: str = data.get("description", "")
        self.entry_agent: str | None = None
        entry = data.get("entry", {})
        if isinstance(entry, dict):
            self.entry_agent = entry.get("agent")
        self.policies: dict = data.get("policies", {})
        events = data.get("events", {})
        self.emits: list[str] = events.get("emits", []) if isinstance(events, dict) else []
        self.consumes: list[str] = events.get("consumes", []) if isinstance(events, dict) else []


class Capability:
    def __init__(self, manifest: CapabilityManifest, base_path: Path):
        self.manifest = manifest
        self.base_path = base_path
        self._handler = None
        self.last_execution: str | None = None
        self.error_count: int = 0
        self.execution_count: int = 0
        self.total_duration_ms: int = 0

    def load_handler(self):
        if self._handler:
            return self._handler
        handler_path = self.base_path / CAPABILITY_HANDLER_PATH
        if not handler_path.exists():
            return None
        spec = importlib.util.spec_from_file_location(f"cap_{self.manifest.id}", handler_path)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self._handler = mod
        return self._handler

    @property
    def avg_latency_ms(self) -> int:
        if self.execution_count == 0:
            return 0
        return self.total_duration_ms // self.execution_count

    @property
    def error_rate(self) -> float:
        if self.execution_count == 0:
                return 0.0
        return self.error_count / self.execution_count


class CapabilityBus:
    def __init__(self, registry_path: str | None = None):
        if registry_path is None:
            registry_path = str(REPO / "capabilities" / "index.yaml")
        self.registry_path = registry_path
        self._registry: dict[str, CapabilityManifest] = {}
        self._cache: dict[str, Capability] = {}
        self._load_registry()

    def _load_registry(self):
        path = Path(self.registry_path)
        if not path.exists():
            return
        data = yaml.safe_load(path.read_text())
        for entry in data.get("capabilities", []):
            manifest = CapabilityManifest(entry)
            self._registry[manifest.id] = manifest

    async def resolve(self, capability_id: str) -> Capability | None:
        if capability_id in self._cache:
            return self._cache[capability_id]
        manifest = self._registry.get(capability_id)
        if not manifest:
            return None
        capability = Capability(manifest, REPO / "capabilities" / capability_id)
        capability.load_handler()
        self._cache[capability_id] = capability
        return capability

    async def execute(self, capability_id: str, context: Any) -> ExecutionResult:
        cap = await self.resolve(capability_id)
        if not cap:
            return ExecutionResult(task_id=capability_id, status="rejected", error=f"Capability '{capability_id}' not found")

        tenant_id = getattr(context, "tenant", "default") if not isinstance(context, dict) else context.get("tenant", "default")
        tenant_manager = getattr(context, "tenant_manager", None) if not isinstance(context, dict) else None
        if tenant_manager and not tenant_manager.is_capability_allowed(tenant_id, capability_id):
            return ExecutionResult(task_id=capability_id, status="rejected", error=f"Capability '{capability_id}' not allowed for tenant '{tenant_id}'")

        handler = cap.load_handler()
        if not handler:
            return ExecutionResult(task_id=capability_id, status="rejected", error=f"Capability '{capability_id}' has no handler")

        import time
        start = time.monotonic()
        try:
            execute_fn = getattr(handler, "execute", None) or getattr(handler, "handle", None) or getattr(handler, "run", None)
            if not execute_fn:
                return ExecutionResult(task_id=capability_id, status="rejected", error="Handler has no execute() function")
            sig = inspect.signature(execute_fn)
            if "query" in sig.parameters:
                query = context.get("query", str(context)) if isinstance(context, dict) else str(context)
                result = await execute_fn(query) if inspect.iscoroutinefunction(execute_fn) else execute_fn(query)
            elif len(sig.parameters) == 1 or "context" in sig.parameters:
                result = await execute_fn(context) if inspect.iscoroutinefunction(execute_fn) else execute_fn(context)
            else:
                result = await execute_fn() if inspect.iscoroutinefunction(execute_fn) else execute_fn()
            duration = int((time.monotonic() - start) * 1000)
            cap.execution_count += 1
            cap.total_duration_ms += duration
            cap.last_execution = "success"
            return ExecutionResult(
                task_id=capability_id,
                status="success",
                output=result if isinstance(result, dict) else {"result": str(result)},
                duration_ms=duration,
            )
        except Exception as e:
            duration = int((time.monotonic() - start) * 1000)
            cap.execution_count += 1
            cap.error_count += 1
            cap.last_execution = "failure"
            return ExecutionResult(
                task_id=capability_id,
                status="failure",
                error=str(e),
                duration_ms=duration,
            )

    def discover(self, query: str | None = None) -> list[CapabilityManifest]:
        if not query:
            return list(self._registry.values())
        q = query.lower()
        return [
            m for m in self._registry.values()
            if q in m.name.lower() or q in m.id.lower() or q in m.description.lower()
        ]

    def health(self, capability_id: str) -> dict:
        cap = self._cache.get(capability_id)
        if not cap:
            return {"id": capability_id, "status": "unknown"}
        return {
            "id": capability_id,
            "status": cap.manifest.status,
            "last_execution": cap.last_execution,
            "error_rate": cap.error_rate,
            "avg_latency_ms": cap.avg_latency_ms,
            "execution_count": cap.execution_count,
        }

    def list_status(self) -> list[dict]:
        return [
            {
                "id": m.id,
                "name": m.name,
                "version": m.version,
                "status": m.status,
                "domain": m.domain,
                "agent": m.entry_agent,
            }
            for m in self._registry.values()
        ]
