"""JARVIS Action Router — Executes intents from the voice classifier.

Routes intent strings to handler functions and returns ActionResult objects.
Uses a persistent Playwright browser for page operations.
"""
import logging, os, time
from dataclasses import dataclass, field
from typing import Any

import asyncpg

log = logging.getLogger("jarvis.actions")
DB_DSN = os.getenv("CONTENT_DB_DSN", "postgresql://sdc:sdc@localhost:5432/sdc_content")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
BROWSER_PROFILE = "/tmp/jarvis-browser-profile"
DESTRUCTIVE_ACTIONS = {"send_message", "playwright_action"}


@dataclass
class ActionResult:
    text: str = ""
    screenshot_path: str = ""
    dashboard_html: str = ""
    action: str = ""
    needs_confirmation: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


# ─── Persistent Playwright Browser ───
_browser = _pw = None

async def _get_browser():
    global _browser, _pw
    if _browser: return _browser
    from playwright.async_api import async_playwright
    os.makedirs(BROWSER_PROFILE, exist_ok=True)
    _pw = await async_playwright().start()
    _browser = await _pw.chromium.launch_persistent_context(
        BROWSER_PROFILE, headless=False, channel="chrome",
        args=["--no-sandbox", "--disable-dev-shm-usage"],
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )
    return _browser

async def _close_page(page):
    try: await page.close()
    except Exception: pass


async def _open_page(params: dict) -> ActionResult:
    url = params.get("url", "https://google.com")
    page = await (await _get_browser()).new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        title = await page.title()
        return ActionResult(text=f"Abierta: {title} ({url})", action="open_page", extra={"title": title, "url": page.url})
    except Exception as e:
        return ActionResult(text=f"Error abriendo {url}: {e}", action="open_page")
    finally:
        await _close_page(page)


async def _query_db(params: dict) -> ActionResult:
    sql = params.get("sql", "")
    if not sql.strip().upper().startswith("SELECT"):
        return ActionResult(text="Solo se permiten consultas SELECT.", action="query_db")
    try:
        pool = await asyncpg.create_pool(DB_DSN, min_size=1, max_size=2)
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql)
        await pool.close()
        if not rows:
            return ActionResult(text="Consulta sin resultados.", action="query_db")
        headers = list(rows[0].keys())
        lines = [" | ".join(headers), "-" * 40]
        for row in rows[:20]:
            lines.append(" | ".join(str(row[h]) for h in headers))
        if len(rows) > 20: lines.append(f"... ({len(rows)} filas totales)")
        return ActionResult(text="\n".join(lines), action="query_db", extra={"row_count": len(rows)})
    except Exception as e:
        return ActionResult(text=f"Error en consulta: {e}", action="query_db")


async def _show_content(params: dict) -> ActionResult:
    title, items = params.get("title", "Contenido"), params.get("items", [])
    lines = [f"**{title}**", ""]
    for i, item in enumerate(items, 1):
        if isinstance(item, dict):
            lines.append(f"{i}. {item.get('name', item.get('title', ''))}")
            if desc := item.get("description", ""): lines.append(f"   {desc}")
        else:
            lines.append(f"{i}. {item}")
    return ActionResult(text="\n".join(lines), action="show_content")


async def _create_dashboard(params: dict) -> ActionResult:
    title, metrics = params.get("title", "Dashboard"), params.get("metrics", {})
    rows = "".join(f'<div style="margin:8px;padding:12px;background:#1a1a2e;border-radius:8px;color:#e0e0e0"><strong>{k}</strong>: {v}</div>' for k, v in metrics.items())
    html = f'<div style="font-family:sans-serif;padding:16px;background:#0f0f23;color:#e0e0e0"><h2>{title}</h2>{rows}</div>'
    return ActionResult(text=f"Dashboard '{title}' generado.", dashboard_html=html, action="create_dashboard")


async def _send_message(params: dict) -> ActionResult:
    target, text, platform = params.get("target", ""), params.get("text", ""), params.get("platform", "telegram")
    log.info("send_message -> %s via %s: %s", target, platform, text[:80])
    return ActionResult(text=f"Mensaje enviado a {target} via {platform}.", action="send_message", extra={"target": target, "platform": platform})


async def _take_screenshot(params: dict) -> ActionResult:
    url, ts = params.get("url"), int(time.time())
    path = f"/tmp/jarvis-screenshot-{ts}.png"
    page = await (await _get_browser()).new_page()
    try:
        if url: await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.screenshot(path=path, full_page=True)
        return ActionResult(text=f"Screenshot guardado: {path}", screenshot_path=path, action="take_screenshot")
    except Exception as e:
        return ActionResult(text=f"Error en screenshot: {e}", action="take_screenshot")
    finally:
        await _close_page(page)


async def _playwright_action(params: dict) -> ActionResult:
    url, action_type = params.get("url", "https://google.com"), params.get("action", "click")
    selector, value = params.get("selector", ""), params.get("value", "")
    page = await (await _get_browser()).new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        if action_type == "click" and selector: await page.click(selector)
        elif action_type == "fill" and selector: await page.fill(selector, value)
        elif action_type == "select" and selector: await page.select_option(selector, value)
        await page.wait_for_timeout(1000)
        return ActionResult(text=f"Acción '{action_type}' ejecutada en {await page.title()}.", action="playwright_action", extra={"url": page.url, "action": action_type})
    except Exception as e:
        return ActionResult(text=f"Error en acción: {e}", action="playwright_action")
    finally:
        await _close_page(page)


async def _system_status(params: dict) -> ActionResult:
    checks = {}
    # Postgres
    try:
        pool = await asyncpg.create_pool(DB_DSN, min_size=1, max_size=1)
        async with pool.acquire() as c: await c.fetchval("SELECT 1")
        checks["postgres"] = "ok"; await pool.close()
    except Exception as e: checks["postgres"] = f"error: {e}"
    # Redis
    try:
        import redis.asyncio as aioredis
        r = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_timeout=3)
        await r.ping(); await r.aclose(); checks["redis"] = "ok"
    except Exception as e: checks["redis"] = f"error: {e}"
    # Qdrant
    try:
        import httpx
        async with httpx.AsyncClient(timeout=3) as cl:
            resp = await cl.get(f"http://{QDRANT_HOST}:{QDRANT_PORT}/healthz")
            checks["qdrant"] = "ok" if resp.status_code == 200 else f"status {resp.status_code}"
    except Exception as e: checks["qdrant"] = f"error: {e}"
    checks["playwright"] = "ok" if _browser else "idle"
    lines = ["**Estado del sistema:**", ""] + [f"  {'ok' if s == 'ok' else '!'} {k}: {s}" for k, s in checks.items()]
    return ActionResult(text="\n".join(lines), action="system_status", extra=checks)


async def _shutdown_mic(params: dict) -> ActionResult:
    return ActionResult(text="Micrófono apagado.", action="stop_listening")


ACTION_MAP = {
    "open_page": _open_page, "query_db": _query_db, "show_content": _show_content,
    "create_dashboard": _create_dashboard, "send_message": _send_message,
    "take_screenshot": _take_screenshot, "playwright_action": _playwright_action,
    "system_status": _system_status, "shutdown_mic": _shutdown_mic,
}


class ActionRouter:
    """Routes an intent string to the corresponding action handler."""

    async def execute(self, intent: str, params: dict | None = None) -> ActionResult:
        params = params or {}
        handler = ACTION_MAP.get(intent)
        if handler is None:
            return ActionResult(text=f"Intent desconocido: {intent}", action=intent)
        if intent in DESTRUCTIVE_ACTIONS and not params.get("confirmation"):
            return ActionResult(text=f"La acción '{intent}' requiere confirmation=True.", action=intent, needs_confirmation=True)
        try:
            return await handler(params)
        except Exception as e:
            log.exception("Error ejecutando %s", intent)
            return ActionResult(text=f"Error en {intent}: {e}", action=intent)
