"""Decision Engine — select best provider and execute capability."""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

from planner.events import emit_capability_executed, emit_provider_failed
from planner.exceptions import NoProviderAvailableError, ProviderExecutionError
from planner.health import is_healthy
from planner.models import CapabilityResult, ProviderRef
from planner.registry import get_capability

log = logging.getLogger("planner.engine")

# Map contract_type to module prefix for dynamic import
CONTRACT_EXECUTORS: dict[str, str] = {
    "http": "planner.executors.http",
    "cli": "planner.executors.cli",
    "browser": "planner.executors.browser",
    "mcp": "planner.executors.mcp",
    "sdk": "planner.executors.sdk",
}


def select_provider(
    capability_id: str,
    input_data: dict | None = None,
    preferred_provider: str | None = None,
    max_cost: float | None = None,
    healthy_only: bool = True,
) -> ProviderRef:
    """Select the best provider for a given capability.

    Algorithm:
    1. Lookup capability in registry
    2. Get providers sorted by weight
    3. If preferred_provider is specified and healthy, use it
    4. Otherwise select lowest-weight healthy provider
    5. Filter by max_cost if specified
    """
    cap = get_capability(capability_id)
    if not cap:
        raise NoProviderAvailableError(capability_id)

    if not cap.providers:
        raise NoProviderAvailableError(capability_id)

    providers = sorted([p for p in cap.providers if p.enabled], key=lambda p: p.weight)

    # Preferred provider
    if preferred_provider:
        preferred = next((p for p in providers if p.id == preferred_provider), None)
        if preferred and (not healthy_only or is_healthy(preferred.id)):
            return preferred

    # Select by weight + health + cost
    for provider in providers:
        if healthy_only and not is_healthy(provider.id):
            continue
        if max_cost is not None and provider.cost_per_call > max_cost:
            continue
        return provider

    raise NoProviderAvailableError(capability_id)


async def execute_capability(
    capability_id: str,
    input_data: dict[str, Any] | None = None,
    preferred_provider: str | None = None,
    max_cost: float | None = None,
    fallback: bool = True,
) -> CapabilityResult:
    """Execute a capability: select provider, run, emit event, return result.

    If fallback=True, automatically retry with next provider on failure.
    """
    cap = get_capability(capability_id)
    if not cap:
        return CapabilityResult(
            capability_id=capability_id,
            provider_id="",
            success=False,
            error=f"Capability '{capability_id}' not found",
        )

    providers = sorted([p for p in cap.providers if p.enabled], key=lambda p: p.weight)

    if preferred_provider:
        preferred = next((p for p in providers if p.id == preferred_provider), None)
        if preferred:
            providers = [preferred] + [p for p in providers if p.id != preferred_provider]

    for provider in providers:
        if max_cost is not None and provider.cost_per_call > max_cost:
            continue

        result = await _try_execute(capability_id, provider, input_data)
        if result.success:
            return result
        if not fallback:
            return result

    return CapabilityResult(
        capability_id=capability_id,
        provider_id=providers[0].id if providers else "",
        success=False,
        error=f"All providers failed for capability '{capability_id}'",
        timestamp=datetime.now(timezone.utc),
    )


async def _try_execute(
    capability_id: str,
    provider: ProviderRef,
    input_data: dict[str, Any] | None,
) -> CapabilityResult:
    """Try to execute a capability with a specific provider."""
    start = time.time()
    try:
        executor = _get_executor(provider.contract_type)
        data = await executor(provider, input_data or {})
        latency_ms = (time.time() - start) * 1000

        result = CapabilityResult(
            capability_id=capability_id,
            provider_id=provider.id,
            success=True,
            data=data,
            latency_ms=latency_ms,
            cost_estimate=provider.cost_per_call,
            timestamp=datetime.now(timezone.utc),
        )
        emit_capability_executed(result)
        return result

    except (NoProviderAvailableError, ProviderExecutionError) as e:
        latency_ms = (time.time() - start) * 1000
        emit_provider_failed(provider.id, capability_id, str(e))
        return CapabilityResult(
            capability_id=capability_id,
            provider_id=provider.id,
            success=False,
            error=str(e),
            latency_ms=latency_ms,
            timestamp=datetime.now(timezone.utc),
        )
    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        emit_provider_failed(provider.id, capability_id, str(e))
        return CapabilityResult(
            capability_id=capability_id,
            provider_id=provider.id,
            success=False,
            error=str(e),
            latency_ms=latency_ms,
            timestamp=datetime.now(timezone.utc),
        )


def _get_executor(contract_type: str) -> Any:
    """Get the executor function for a contract type."""
    module_path = CONTRACT_EXECUTORS.get(contract_type)
    if not module_path:
        raise ProviderExecutionError("unknown", "unknown",
                                     f"No executor for contract type '{contract_type}'")

    try:
        import importlib
        mod = importlib.import_module(module_path)
        return mod.execute
    except ImportError as e:
        raise ProviderExecutionError("unknown", "unknown",
                                     f"Executor module '{module_path}' not found: {e}") from e
