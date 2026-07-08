"""TenantManager — loads, validates, and resolves tenants (HAS-011)"""
import json
from pathlib import Path
from typing import Any

from tenants.models import Tenant, TenantConfig

REPO = Path(__file__).resolve().parent.parent
TENANTS_DIR = REPO / "state" / "tenants"


class TenantManager:
    def __init__(self):
        self._tenants: dict[str, Tenant] = {}
        self._load_defaults()

    def _load_defaults(self):
        TENANTS_DIR.mkdir(parents=True, exist_ok=True)
        default = TenantConfig.default()
        path = TENANTS_DIR / f"{default.id}.json"
        if not path.exists():
            path.write_text(json.dumps({
                "id": default.id,
                "name": default.name,
                "isolation": default.isolation,
                "capabilities": default.capabilities,
                "constitution_overrides": default.constitution_overrides,
                "budget": default.budget,
                "settings": default.settings,
            }, indent=2))
        config_paths = list(TENANTS_DIR.glob("*.json"))
        for p in config_paths:
            try:
                data = json.loads(p.read_text())
                config = TenantConfig(**data)
                self._tenants[config.id] = Tenant(config=config)
            except Exception as e:
                print(f"[tenants] Warning: failed to load {p.name}: {e}")

    def get(self, tenant_id: str) -> Tenant | None:
        return self._tenants.get(tenant_id)

    def list_tenants(self) -> list[TenantConfig]:
        return [t.config for t in self._tenants.values()]

    def is_capability_allowed(self, tenant_id: str, capability_id: str) -> bool:
        tenant = self.get(tenant_id)
        if not tenant:
            return False
        caps = tenant.config.capabilities
        if "*" in caps:
            return True
        return capability_id in caps

    def is_enabled(self, tenant_id: str) -> bool:
        tenant = self.get(tenant_id)
        return tenant is not None and tenant.active

    def get_budget(self, tenant_id: str) -> float:
        tenant = self.get(tenant_id)
        if not tenant:
            return 0.0
        return tenant.config.budget

    def get_stats(self) -> dict:
        return {
            "total_tenants": len(self._tenants),
            "tenants": [{"id": t.config.id, "name": t.config.name, "active": t.active, "isolation": t.config.isolation} for t in self._tenants.values()],
        }
