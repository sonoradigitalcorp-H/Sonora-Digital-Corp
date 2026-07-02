"""SDK executor — calls external SDKs for SDK contract type providers."""
from __future__ import annotations

import logging
from typing import Any

from planner.exceptions import ProviderExecutionError
from planner.models import ProviderRef

log = logging.getLogger("planner.executors.sdk")


async def execute(provider: ProviderRef, input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute an SDK provider by calling an external SDK.

    This executor is a placeholder for SDK-based providers (e.g., OpenAI SDK,
    Anthropic SDK, Spotify Web API SDK, etc.). Each SDK provider should register
    its own execute function in provider.config.executor_module.
    """
    config = provider.config
    executor_module = config.get("executor_module", "")

    if not executor_module:
        raise ProviderExecutionError(
            provider.id, provider.id,
            "No executor_module configured for SDK provider"
        )

    try:
        import importlib
        mod = importlib.import_module(executor_module)
        if hasattr(mod, "execute"):
            return await mod.execute(provider, input_data)
    except ImportError as e:
        raise ProviderExecutionError(
            provider.id, provider.id,
            f"SDK executor module '{executor_module}' not found: {e}"
        ) from e

    raise ProviderExecutionError(
        provider.id, provider.id,
        f"SDK executor '{executor_module}' has no execute() function"
    )
