"""HTTP executor — calls REST APIs for HTTP contract type providers."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from planner.exceptions import ProviderExecutionError
from planner.models import ProviderRef

log = logging.getLogger("planner.executors.http")

TIMEOUT = 15


async def execute(provider: ProviderRef, input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute an HTTP provider.

    Uses provider.config to determine:
    - base_url: API base URL
    - method: HTTP method (default GET)
    - endpoint_template: URL template with {param} placeholders
    - headers: optional headers
    """
    config = provider.config
    base_url = config.get("base_url", "")
    method = config.get("method", "GET").upper()
    headers = config.get("headers", {})
    timeout = config.get("timeout", TIMEOUT)

    endpoint = config.get("endpoint", "")
    if not endpoint:
        endpoint = base_url

    # Build query params or body from input_data
    params = config.get("params", {})
    for k, v in input_data.items():
        if k not in params:
            params[k] = v

    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            if method == "GET":
                resp = await client.get(endpoint, params=params, headers=headers)
            elif method == "POST":
                resp = await client.post(endpoint, json=input_data, headers=headers)
            elif method == "PUT":
                resp = await client.put(endpoint, json=input_data, headers=headers)
            else:
                resp = await client.get(endpoint, params=params, headers=headers)

            if resp.status_code >= 500:
                raise ProviderExecutionError(
                    provider.id, provider.id,
                    f"HTTP {resp.status_code}: {resp.text[:200]}"
                )
            if resp.status_code == 429:
                raise ProviderExecutionError(
                    provider.id, provider.id,
                    "Rate limited (HTTP 429)"
                )

            return {"status_code": resp.status_code, "data": resp.json()}

    except httpx.TimeoutException:
        raise ProviderExecutionError(provider.id, provider.id, "HTTP timeout")
    except httpx.HTTPError as e:
        raise ProviderExecutionError(provider.id, provider.id, str(e))
