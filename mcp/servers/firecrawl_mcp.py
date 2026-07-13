"""Firecrawl MCP Server — Web crawling and scraping.

Extracts content from URLs as markdown for RAG ingestion.
"""

import json
import os

import httpx

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")


async def firecrawl_crawl(url: str) -> str:
    if not FIRECRAWL_API_KEY:
        return json.dumps({"error": "FIRECRAWL_API_KEY not configured"})
    if not url:
        return json.dumps({"error": "url is required"})
    try:
        headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.firecrawl.dev/v1/crawl",
                json={"url": url, "pageOptions": {"onlyMainContent": True}},
                headers=headers,
                timeout=60,
            )
            data = resp.json()
            if "data" in data:
                content = data["data"][0].get("markdown", "") if isinstance(data["data"], list) else data["data"].get("markdown", "")
                return json.dumps({"url": url, "content": content[:10000], "content_length": len(content)})
            return json.dumps({"url": url, "content": str(data)[:5000], "content_length": len(str(data))})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def firecrawl_scrape(url: str) -> str:
    if not FIRECRAWL_API_KEY:
        return json.dumps({"error": "FIRECRAWL_API_KEY not configured"})
    if not url:
        return json.dumps({"error": "url is required"})
    try:
        headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.firecrawl.dev/v1/scrape",
                json={"url": url, "formats": ["markdown"]},
                headers=headers,
                timeout=30,
            )
            data = resp.json()
            content = ""
            if "data" in data:
                content = data["data"].get("markdown", "") if isinstance(data.get("data"), dict) else str(data)
            return json.dumps({"url": url, "content": content[:10000], "content_length": len(content)})
    except Exception as e:
        return json.dumps({"error": str(e)})


MCP_TOOLS = {
    "firecrawl_crawl": {
        "description": "Crawl a URL and extract content as markdown",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to crawl"},
            },
            "required": ["url"],
        },
        "handler": lambda args: firecrawl_crawl(args["url"]),
    },
    "firecrawl_scrape": {
        "description": "Scrape a single URL and extract content as markdown",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to scrape"},
            },
            "required": ["url"],
        },
        "handler": lambda args: firecrawl_scrape(args["url"]),
    },
}
