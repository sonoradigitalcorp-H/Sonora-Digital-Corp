"""Browser executor — uses Playwright MCP to control browser for browser contract type."""
from __future__ import annotations

import logging
from typing import Any

from planner.exceptions import ProviderExecutionError
from planner.models import ProviderRef

log = logging.getLogger("planner.executors.browser")


async def execute(provider: ProviderRef, input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a browser provider via Playwright MCP.

    Uses provider.config to determine:
    - url_template: URL template with {param} placeholders
    - actions: list of actions to perform (navigate, screenshot, extract)
    """
    config = provider.config
    url_template = config.get("url_template", "")
    timeout = config.get("timeout", 30)

    if not url_template:
        raise ProviderExecutionError(provider.id, provider.id, "No url_template configured")

    try:
        url = url_template.format(**input_data)
    except KeyError as e:
        raise ProviderExecutionError(
            provider.id, provider.id, f"Missing input parameter: {e}"
        )

    # Try direct Playwright first, then MCP
    try:
        return await _playwright_direct(url, timeout, input_data)
    except ImportError:
        log.warning("playwright not available, trying MCP for %s", url)
        return await _playwright_mcp(url, provider, timeout)


async def _playwright_direct(url: str, timeout: int,
                              input_data: dict[str, Any]) -> dict[str, Any]:
    """Use playwright directly for browser rendering."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/125.0.0.0 Safari/537.36",
        )
        page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        result = {
            "url": page.url,
            "title": page.title(),
            "html": page.content(),
        }

        if input_data.get("screenshot"):
            screenshot = page.screenshot(full_page=True)
            result["screenshot_base64"] = screenshot.base64() if hasattr(screenshot, 'base64') else None

        browser.close()
        return result


async def _playwright_mcp(url: str, provider: ProviderRef,
                           timeout: int) -> dict[str, Any]:
    """Use Playwright MCP server for browser automation."""
    mcp_url = provider.config.get("mcp_url", "http://127.0.0.1:8931")
    import httpx

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            f"{mcp_url}/tools/call",
            json={
                "name": "browser_navigate",
                "arguments": {"url": url},
            }
        )
        if resp.status_code != 200:
            raise ProviderExecutionError(
                provider.id, provider.id,
                f"MCP navigate failed: HTTP {resp.status_code}"
            )

        snapshot = await client.post(
            f"{mcp_url}/tools/call",
            json={"name": "browser_snapshot", "arguments": {}}
        )

        return {
            "url": url,
            "mcp_response": resp.json(),
            "snapshot": snapshot.json() if snapshot.status_code == 200 else None,
        }
