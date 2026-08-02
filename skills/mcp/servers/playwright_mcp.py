"""Playwright MCP Server — Browser automation with persistent browser instance.

FIX: Reuses a single browser instance instead of creating a new one per request.
Each function reuses the same browser context. Browser auto-restarts after 30 min
or on memory limit.
"""

import asyncio
import json
import logging
import os
import time

log = logging.getLogger("mcp.playwright")

PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true") == "true"
MAX_SESSION_SECONDS = 1800  # 30 min
MAX_MEMORY_MB = 400

# Persistent browser state
_browser = None
_context = None
_pw = None
_session_start = 0


async def _get_browser():
    """Get or create a persistent browser instance."""
    global _browser, _context, _pw, _session_start

    now = time.time()

    # Auto-restart if session expired or memory exceeded
    if _browser:
        elapsed = now - _session_start
        try:
            import psutil
            proc = psutil.Process(os.getpid())
            mem_mb = proc.memory_info().rss / 1024 / 1024
            if mem_mb > MAX_MEMORY_MB:
                log.warning(f"Playwright MCP: memory {mem_mb:.0f}MB > {MAX_MEMORY_MB}MB, restarting")
                await _close_browser()
            elif elapsed > MAX_SESSION_SECONDS:
                log.info(f"Playwright MCP: session {elapsed:.0f}s > {MAX_SESSION_SECONDS}s, restarting")
                await _close_browser()
        except Exception:
            if elapsed > MAX_SESSION_SECONDS:
                await _close_browser()

    if not _browser:
        from playwright.async_api import async_playwright
        _pw = await async_playwright().start()
        _browser = await _pw.chromium.launch(
            headless=PLAYWRIGHT_HEADLESS,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-background-networking",
            ],
        )
        _context = await _browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        _session_start = now
        log.info("Playwright MCP: browser started")

    return _context


async def _close_browser():
    """Close and cleanup browser."""
    global _browser, _context, _pw, _session_start
    try:
        if _browser:
            await _browser.close()
        if _pw:
            await _pw.stop()
    except Exception:
        pass
    _browser = None
    _context = None
    _pw = None
    _session_start = 0
    log.info("Playwright MCP: browser closed")


async def browser_navigate(url: str) -> str:
    try:
        ctx = await _get_browser()
        page = await ctx.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            title = await page.title()
            content = await page.content()
            return json.dumps({
                "title": title,
                "url": url,
                "content_length": len(content),
                "status": "ok",
            })
        finally:
            await page.close()
    except Exception as e:
        return json.dumps({"error": str(e), "status": "error"})


async def browser_screenshot(url: str, selector: str = None) -> str:
    try:
        ctx = await _get_browser()
        page = await ctx.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            if selector:
                el = await page.wait_for_selector(selector)
                path = f"/tmp/screenshot_{hash(url)}.png"
                await el.screenshot(path=path)
            else:
                path = f"/tmp/screenshot_{hash(url)}.png"
                await page.screenshot(path=path, full_page=True)
            return json.dumps({"screenshot_path": path, "status": "ok"})
        finally:
            await page.close()
    except Exception as e:
        return json.dumps({"error": str(e), "status": "error"})


async def browser_extract(url: str, selector: str = "body") -> str:
    try:
        ctx = await _get_browser()
        page = await ctx.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            elements = await page.query_selector_all(selector)
            texts = [await el.inner_text() for el in elements[:20]]
            return json.dumps({"results": texts, "count": len(texts), "status": "ok"})
        finally:
            await page.close()
    except Exception as e:
        return json.dumps({"error": str(e), "status": "error"})


MCP_TOOLS = {
    "browser_navigate": {
        "description": "Navigate to a URL and get page info (reuses browser)",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to navigate to"},
            },
            "required": ["url"],
        },
        "handler": lambda args: browser_navigate(args["url"]),
    },
    "browser_screenshot": {
        "description": "Take a screenshot of a URL or element (reuses browser)",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to screenshot"},
                "selector": {"type": "string", "description": "CSS selector (optional)"},
            },
            "required": ["url"],
        },
        "handler": lambda args: browser_screenshot(args["url"], args.get("selector")),
    },
    "browser_extract": {
        "description": "Extract text from a URL using CSS selector (reuses browser)",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to extract from"},
                "selector": {"type": "string", "description": "CSS selector", "default": "body"},
            },
            "required": ["url"],
        },
        "handler": lambda args: browser_extract(args["url"], args.get("selector", "body")),
    },
}