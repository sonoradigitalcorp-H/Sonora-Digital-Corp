"""Planner — Capability Registry and Decision Engine.

Usage:
    from planner import select_provider, execute_capability, get_capability

    # Select best provider
    provider = select_provider("acquire-metadata")

    # Execute capability with automatic fallback
    result = await execute_capability("acquire-metadata", {"artist_name": "Hector Rubio"})
"""
from .decision_engine import execute_capability, select_provider
from .events import (
    emit_capability_executed,
    emit_no_provider,
    emit_provider_degraded,
    emit_provider_failed,
    emit_provider_recovered,
    emit_registry_updated,
    emit_sync_completed,
    emit_sync_started,
)
from .exceptions import NoProviderAvailableError, ProviderExecutionError
from .health import check_provider_health, get_provider_health, is_healthy
from .models import Capability, CapabilityResult, ProviderHealth, ProviderRef
from .registry import get_capability, list_capabilities, list_providers, load_registry

__all__ = [
    "execute_capability", "select_provider",
    "get_capability", "list_capabilities", "list_providers", "load_registry",
    "check_provider_health", "get_provider_health", "is_healthy",
    "Capability", "CapabilityResult", "ProviderHealth", "ProviderRef",
    "NoProviderAvailableError", "ProviderExecutionError",
    "emit_capability_executed", "emit_provider_failed", "emit_no_provider",
    "emit_provider_degraded", "emit_provider_recovered", "emit_registry_updated",
    "emit_sync_started", "emit_sync_completed",
]
