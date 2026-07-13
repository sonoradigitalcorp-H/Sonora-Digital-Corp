"""Open Lovable MCP Server — Generate React code via OpenRouter LLM.

Uses OpenRouter (DeepSeek V4 Flash) directly with Firecrawl for cloning.
No dependency on the Open Lovable Next.js UI.
"""

import json
import os
import httpx

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", os.getenv("OPENAI_API_KEY", ""))
OPENROUTER_BASE = "https://openrouter.ai/api/v1"
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
LOVABLE_URL = "http://localhost:3030"


async def _call_llm(system_prompt: str, user_prompt: str, model: str = "opencode/deepseek-v4-flash-free", fallback: str = "openrouter/free") -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sdc.ai",
    }
    last_error = ""
    async with httpx.AsyncClient() as client:
        for attempt, m in enumerate([model, fallback]):
            try:
                resp = await client.post(
                    f"{OPENROUTER_BASE}/chat/completions",
                    json={
                        "model": m,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.7,
                        "max_tokens": 8000,
                    },
                    headers=headers,
                    timeout=120,
                )
                data = resp.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    return json.dumps({"content": content, "model": m})
                last_error = str(data.get("error", "unknown"))
            except Exception as e:
                last_error = str(e)
                if attempt == 0:
                    continue
    return json.dumps({"error": last_error})


async def lovable_generate_page(prompt: str, model: str = "opencode/deepseek-v4-flash-free") -> str:
    system = """You are an expert React developer. Generate complete, production-ready React code.
Output each file in this XML format:
<file path="src/App.jsx">
// code here
</file>
<file path="src/components/Example.jsx">
// code here
</file>

Rules:
- Use Tailwind CSS for ALL styling (NO inline styles, NO CSS files except index.css)
- ALWAYS include src/index.css with: @tailwind base; @tailwind components; @tailwind utilities;
- Include a Navigation/Header, Hero section, and Footer
- NEVER truncate files - always return complete code
- Use lucide-react for icons when needed
- Return ONLY the XML file blocks, no other text"""
    return await _call_llm(system, prompt, model)


async def lovable_clone_site(url: str, model: str = "opencode/deepseek-v4-flash-free") -> str:
    scraped = ""
    if FIRECRAWL_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    "https://api.firecrawl.dev/v1/scrape",
                    json={"url": url, "formats": ["markdown"]},
                    headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
                    timeout=30,
                )
                if r.status_code == 200:
                    scraped = r.json().get("data", {}).get("markdown", "")[:5000]
        except Exception:
            scraped = ""
    system = "You clone websites into React code. Recreate the EXACT look and feel using Tailwind CSS."
    user = f"Clone this website: {url}\n\nScraped content:\n{scraped}\n\nRecreate it as a complete React app with all sections."
    return await _call_llm(system, user, model)


async def lovable_extract_brand(url: str) -> str:
    if not FIRECRAWL_API_KEY:
        return json.dumps({"error": "FIRECRAWL_API_KEY not set"})
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.firecrawl.dev/v1/scrape",
                json={"url": url, "formats": ["markdown"]},
                headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
                timeout=30,
            )
            data = r.json().get("data", {})
            return json.dumps({
                "url": url,
                "content_preview": data.get("markdown", "")[:2000],
                "metadata": data.get("metadata", {}),
            }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def lovable_edit_page(prompt: str, current_code: str = "") -> str:
    system = f"""You are editing an existing React app. Apply ONLY the requested changes.
Current code:
{current_code[:3000]}

Output ONLY the modified files as <file path="..."> blocks. Include each file completely."""
    return await _call_llm(system, prompt)


MCP_TOOLS = {
    "lovable_generate_page": {
        "description": "Generate a complete React page/app from a description using AI",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Description of the page/app to generate"},
                "model": {"type": "string", "description": "Model override (optional)"},
            },
            "required": ["prompt"],
        },
        "handler": lambda args: lovable_generate_page(args["prompt"], args.get("model", "opencode/deepseek-v4-flash-free")),
    },
    "lovable_clone_site": {
        "description": "Clone any website URL into a React app",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Website URL to clone"},
                "model": {"type": "string", "description": "Model override (optional)"},
            },
            "required": ["url"],
        },
        "handler": lambda args: lovable_clone_site(args["url"], args.get("model", "opencode/deepseek-v4-flash-free")),
    },
    "lovable_extract_brand": {
        "description": "Extract brand content/styles from a website URL",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Website URL to analyze"},
            },
            "required": ["url"],
        },
        "handler": lambda args: lovable_extract_brand(args["url"]),
    },
    "lovable_edit_page": {
        "description": "Modify existing generated code with a description of changes",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Description of changes"},
                "current_code": {"type": "string", "description": "Current code to edit"},
            },
            "required": ["prompt"],
        },
        "handler": lambda args: lovable_edit_page(args["prompt"], args.get("current_code", "")),
    },
}
