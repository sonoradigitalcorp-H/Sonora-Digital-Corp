"""Playwright MCP Server — Browser automation and web scraping [FR6].

Exposes Playwright browser actions as native MCP tools for agents.
Also serves as E2E test runner.
"""

import asyncio
import json
import logging
import os

log = logging.getLogger("mcp.playwright")

PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true") == "true"


async def browser_navigate(url: str) -> str:
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=PLAYWRIGHT_HEADLESS)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            title = await page.title()
            content = await page.content()
            await browser.close()
            return json.dumps({
                "title": title,
                "url": url,
                "content_length": len(content),
                "status": "ok",
            })
    except Exception as e:
        return json.dumps({"error": str(e), "status": "error"})


async def browser_screenshot(url: str, selector: str = None) -> str:
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=PLAYWRIGHT_HEADLESS)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            if selector:
                el = await page.wait_for_selector(selector)
                path = f"/tmp/screenshot_{hash(url)}.png"
                await el.screenshot(path=path)
            else:
                path = f"/tmp/screenshot_{hash(url)}.png"
                await page.screenshot(path=path, full_page=True)
            await browser.close()
            return json.dumps({"screenshot_path": path, "status": "ok"})
    except Exception as e:
        return json.dumps({"error": str(e), "status": "error"})


async def browser_extract(url: str, selector: str = "body") -> str:
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=PLAYWRIGHT_HEADLESS)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            elements = await page.query_selector_all(selector)
            texts = [await el.inner_text() for el in elements[:20]]
            await browser.close()
            return json.dumps({"results": texts, "count": len(texts), "status": "ok"})
    except Exception as e:
        return json.dumps({"error": str(e), "status": "error"})


MCP_TOOLS = {
    "browser_navigate": {
        "description": "Navigate to a URL and get page info",
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
        "description": "Take a screenshot of a URL or element",
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
        "description": "Extract text from a URL using CSS selector",
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
