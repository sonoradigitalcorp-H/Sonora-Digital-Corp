#!/usr/bin/env python3
"""E2E verification of the full Sonora OS stack using Playwright.

Tests that all services are running, communicating, and responding correctly.
Run: python3 tests/e2e/test_sonora_stack.py
"""

import json
import subprocess
import sys
import time
from pathlib import Path

import httpx

REPO = Path(__file__).resolve().parent.parent.parent

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}: {detail}")


def test_engine_health():
    print("\n🔍 Engine Health")
    try:
        r = httpx.get("http://localhost:5100/health", timeout=5)
        check("Engine /health responds", r.status_code == 200)
        check("Engine status ok", r.json().get("status") == "ok")
    except Exception as e:
        check("Engine reachable", False, str(e))


def test_dashboard_served():
    print("\n🔍 Dashboard Static")
    try:
        r = httpx.get("http://localhost:5100/dashboard/", timeout=5)
        check("Dashboard HTML served", r.status_code == 200)
        check("Dashboard has Three.js", "three.min.js" in r.text)
        check("Dashboard has WebSocket", "WebSocket" in r.text)
    except Exception as e:
        check("Dashboard reachable", False, str(e))


def test_client_app_served():
    print("\n🔍 Client App")
    try:
        r = httpx.get("http://localhost:5100/app/", timeout=5)
        check("Client app HTML served", r.status_code == 200)
        check("Client app has login", "login" in r.text.lower())
        check("Client app has JS", "app.js" in r.text)

        r2 = httpx.get("http://localhost:5100/app/js/app.js", timeout=5)
        check("Client app JS served", r2.status_code == 200)
    except Exception as e:
        check("Client app reachable", False, str(e))


def test_api_endpoints():
    print("\n🔍 API Endpoints")
    endpoints = [
        ("/api/v1/dashboard/revenue?tenant_id=abe-music", "revenue"),
        ("/api/v1/dashboard/tokens?tenant_id=abe-music", "tokens"),
        ("/api/v1/dashboard/greetings?tenant_id=abe-music", "greetings"),
        ("/api/v1/dashboard/quests?tenant_id=abe-music", "quests"),
        ("/api/v1/dashboard/leaderboard?tenant_id=abe-music", "leaderboard"),
        ("/api/v1/auth/me", "auth"),
    ]
    for path, name in endpoints:
        try:
            r = httpx.get(f"http://localhost:5100{path}", timeout=5)
            check(f"GET {name}", r.status_code == 200)
        except Exception as e:
            check(f"GET {name}", False, str(e))


def test_mcp_gateway():
    print("\n🔍 MCP Gateway")
    try:
        r = httpx.get("http://localhost:8180/mcp/health", timeout=5)
        check("MCP health", r.status_code == 200)

        r2 = httpx.get("http://localhost:8180/mcp/tools", timeout=5)
        check("MCP tools listed", r2.status_code == 200)
        data = r2.json()
        check(f"Tools count >= 10", data.get("count", 0) >= 10)
    except Exception as e:
        check("MCP gateway reachable", False, str(e))


def test_mcp_execute():
    print("\n🔍 MCP Tool Execution")
    try:
        r = httpx.post(
            "http://localhost:8180/mcp/execute",
            json={"tool": "hasura_query", "args": {"query": "{ __typename }"}},
            timeout=10,
        )
        check("Hasura query via MCP", r.status_code == 200)
    except Exception as e:
        check("MCP execute", False, str(e))


def test_hasura_console():
    print("\n🔍 Hasura")
    try:
        r = httpx.get("http://localhost:8080/console", timeout=5, follow_redirects=False)
        check("Hasura console responds", r.status_code in (200, 302))
    except Exception as e:
        check("Hasura reachable", False, str(e))


def test_redis():
    print("\n🔍 Redis")
    try:
        import redis as redis_lib
        r = redis_lib.Redis(host="localhost", port=6379, password="redis2026")
        ping = r.ping()
        check("Redis responds to PING", ping)
        r.close()
    except Exception as e:
        check("Redis reachable", False, str(e))


def test_omnivoice():
    print("\n🔍 OmniVoice")
    try:
        r = httpx.get("http://localhost:3900/voices", timeout=10)
        check("OmniVoice /voices responds", r.status_code == 200)
    except Exception as e:
        check("OmniVoice reachable", False, str(e))


def test_playwright_browser():
    print("\n🔍 Playwright Browser")
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("http://localhost:5100/health", wait_until="networkidle")
            content = page.content()
            check("Playwright navigates to engine", "\"ok\"" in content)
            browser.close()
    except Exception as e:
        check("Playwright browser works", False, str(e))


def test_playwright_e2e():
    print("\n🔍 Playwright E2E — Full Stack Flow")
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # 1. Dashboard loads
            page = browser.new_page()
            page.goto("http://localhost:5100/dashboard/", wait_until="networkidle")
            check("1. Dashboard page loads", "Sonora" in page.title() or "Dashboard" in page.content())

            # 2. Client app login page
            page.goto("http://localhost:5100/app/", wait_until="networkidle")
            has_login = "Google" in page.content() or "correo" in page.content()
            check("2. Client app shows login", has_login)

            # 3. Navigation sidebar exists
            has_sidebar = "Dashboard" in page.content() and "Configuración" in page.content()
            check("3. Client has navigation", has_sidebar)

            # 4. API health endpoint
            page.goto("http://localhost:5100/health", wait_until="networkidle")
            check("4. Health endpoint", "\"ok\"" in page.content())

            # 5. Dashboard API
            page.goto("http://localhost:5100/api/v1/auth/me", wait_until="networkidle")
            check("5. Auth endpoint", "authenticated" in page.content())

            browser.close()
            check("6. Playwright E2E complete", True)
    except Exception as e:
        check("E2E test suite", False, str(e))


def main():
    print("=" * 50)
    print("Sonora OS — Stack Verification Suite")
    print("=" * 50)

    test_engine_health()
    test_dashboard_served()
    test_client_app_served()
    test_api_endpoints()
    test_mcp_gateway()
    test_mcp_execute()
    test_hasura_console()
    test_redis()
    test_omnivoice()
    test_playwright_browser()
    test_playwright_e2e()

    print("\n" + "=" * 50)
    print(f"Results: {PASS} passed, {FAIL} failed out of {PASS + FAIL} tests")
    print("=" * 50)

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
