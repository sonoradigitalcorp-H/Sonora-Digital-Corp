"""Registry loader — reads config/registry.json and validates with Pydantic."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from planner.models import Capability, ProviderRef, RegistrySchema

log = logging.getLogger("planner.registry")

_registry: dict[str, Capability] | None = None
_registry_path: Path | None = None


def load_registry(path: str | Path = "config/registry.json") -> dict[str, Capability]:
    """Load registry from JSON file, validate with Pydantic, return dict[id -> Capability]."""
    global _registry, _registry_path
    p = Path(path)
    if not p.exists():
        log.warning("Registry file not found: %s", p)
        _registry = {}
        _registry_path = p
        return _registry

    try:
        raw = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        log.error("Invalid JSON in registry: %s", e)
        _registry = {}
        _registry_path = p
        return _registry

    schema = RegistrySchema(**raw)
    _registry = schema.capabilities
    _registry_path = p
    log.info("Registry loaded: %d capabilities from %s", len(_registry), p)
    return _registry


def get_capability(capability_id: str) -> Capability | None:
    """Return capability by ID. Lazy-loads registry if needed."""
    if _registry is None:
        load_registry()
    return _registry.get(capability_id) if _registry else None


def list_capabilities(tag: str | None = None) -> list[Capability]:
    """List all capabilities, optionally filtered by tag."""
    if _registry is None:
        load_registry()
    if not _registry:
        return []
    caps = list(_registry.values())
    if tag:
        caps = [c for c in caps if tag in c.tags]
    return caps


def list_providers(capability_id: str, healthy_only: bool = False) -> list[ProviderRef]:
    """List providers for a capability, ordered by weight. Optionally filter by health."""
    cap = get_capability(capability_id)
    if not cap:
        return []

    providers = [p for p in cap.providers if p.enabled]
    if healthy_only:
        from planner.health import get_provider_health
        healthy = []
        for p in providers:
            health = get_provider_health(p.id)
            if health and health.status == "healthy":
                healthy.append(p)
        providers = healthy

    return sorted(providers, key=lambda p: p.weight)


def reload_registry() -> dict[str, Capability]:
    """Force reload registry from disk."""
    global _registry
    _registry = None
    return load_registry(_registry_path or "config/registry.json")


def count_capabilities() -> int:
    """Return number of loaded capabilities."""
    if _registry is None:
        load_registry()
    return len(_registry) if _registry else 0


def count_providers() -> int:
    """Return total number of providers across all capabilities."""
    if _registry is None:
        load_registry()
    if not _registry:
        return 0
    return sum(len(c.providers) for c in _registry.values())
