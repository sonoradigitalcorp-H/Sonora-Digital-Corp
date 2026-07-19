#!/usr/bin/env python3
"""
Sonora SDK v2.0 — Python Client Library con Auth JWT

Mirror de mcp/sdk/sonora-client.js con la misma API.
Usa httpx asíncrono para mantener compatibilidad con el ecosistema asyncio.

Uso:
  from mcp.sdk.sonora_client import SonoraSDK
  sdk = SonoraSDK(client_id='sdc-core', client_secret='...')
  health = await sdk.health_all()
  result = await sdk.tool('enterprise_score', {})
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger("sonora.sdk")

# Log directory for SDK calls
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "state" / "logs" / "sdk"


class SonoraSDK:
    def __init__(
        self,
        host: str = "127.0.0.1",
        gateway_port: int = 18989,
        client_id: str | None = None,
        client_secret: str | None = None,
        timeout: int = 10,
    ):
        self.base_host = host
        self.gateway_port = gateway_port
        self.client_id = client_id or os.getenv("SONORA_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("SONORA_CLIENT_SECRET", "")
        self.timeout = timeout
        self._token: str | None = None
        self._token_expiry: float = 0.0
        self._http = httpx.AsyncClient(timeout=httpx.Timeout(timeout))

        self.services = {
            "paperclip": {"port": 3100},
            "n8n": {"port": 5678},
            "metabase": {"port": 3002},
            "uptime": {"port": 3003, "name": "uptime-kuma"},
            "dashy": {"port": 3004},
            "plausible": {"port": 3006},
        }

    async def _request(self, host: str, port: int, path: str, method: str = "GET", body: dict = None, headers: dict = None) -> dict:
        url = f"http://{host}:{port}{path}"
        req_headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if headers:
            req_headers.update(headers)
        try:
            if body:
                r = await self._http.request(method, url, json=body, headers=req_headers)
            else:
                r = await self._http.request(method, url, headers=req_headers)
            try:
                data = r.json()
            except Exception:
                data = None
            return {"status": r.status_code, "data": data, "raw": r.text}
        except httpx.TimeoutException:
            logger.error(f"Timeout requesting {method} {url}")
            return {"status": 0, "data": None, "raw": "timeout"}
        except Exception as e:
            logger.error(f"Request failed {method} {url}: {e}")
            return {"status": 0, "data": None, "raw": str(e)}

    async def _request_service(self, service: str, path: str, method: str = "GET", body: dict = None) -> dict:
        svc = self.services.get(service)
        if not svc:
            raise ValueError(f"Unknown service: {service}")
        return await self._request(self.base_host, svc["port"], path, method, body)

    async def _request_gateway(self, path: str, method: str = "GET", body: dict = None) -> dict:
        return await self._request(self.base_host, self.gateway_port, path, method, body)

    async def _ensure_token(self) -> str:
        if self._token and time.time() < self._token_expiry:
            return self._token
        if not self.client_id or not self.client_secret:
            raise ValueError("client_id and client_secret required. Set SONORA_CLIENT_ID / SONORA_CLIENT_SECRET env vars")
        r = await self._request_gateway("/api/auth/token", "POST", {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        })
        if r["status"] != 200:
            raise RuntimeError(f"Auth failed: {r['status']} {r['raw']}")
        data = r["data"]
        if not data:
            raise RuntimeError("Auth returned empty response")
        self._token = data.get("access_token") or data.get("token", "")
        expires_in = data.get("expires_in", 3600)
        self._token_expiry = time.time() + expires_in - 60
        return self._token

    async def _auth_request(self, path: str, method: str = "GET", body: dict = None) -> dict:
        token = await self._ensure_token()
        return await self._request_gateway(path, method, body, {
            "Authorization": f"Bearer {token}",
            "X-Tenant-ID": self.client_id,
        })

    async def health(self, service_id: str) -> dict:
        try:
            r = await self._request_service(service_id, "/api/health")
            if r["status"] == 0:
                return {"service": service_id, "status": "offline", "error": r["raw"]}
            status = "online" if r["status"] == 200 else "degraded"
            return {"service": service_id, "status": status, "code": r["status"]}
        except Exception as e:
            return {"service": service_id, "status": "offline", "error": str(e)}

    async def health_all(self) -> dict:
        results = {}
        for key in self.services:
            results[key] = await self.health(key)
        online = sum(1 for r in results.values() if r["status"] == "online")
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": results,
            "summary": {
                "total": len(results),
                "online": online,
                "offline": len(results) - online,
            },
        }

    async def tool(self, tool_name: str, params: dict = None) -> Any:
        r = await self._auth_request("/api/call", "POST", {"tool": tool_name, "params": params or {}})
        self._log_call("tool", tool_name, params, r)
        return r.get("data", r)

    async def tools(self) -> list:
        r = await self._auth_request("/api/tools", "GET")
        return r.get("data", r)

    async def status(self) -> dict:
        r = await self._auth_request("/api/status", "GET")
        return r.get("data", r)

    async def capability(self, task: str) -> dict:
        r = await self._auth_request("/api/capability/resolve", "POST", {"task": task})
        return r.get("data", r)

    async def capabilities(self) -> list:
        r = await self._auth_request("/api/capability/list", "GET")
        return r.get("data", r)

    async def skills(self) -> list:
        r = await self._auth_request("/api/call", "POST", {"tool": "skills_list", "params": {}})
        return r.get("data", r)

    async def skill_search(self, query: str) -> list:
        r = await self._auth_request("/api/call", "POST", {"tool": "skills_search", "params": {"query": query}})
        return r.get("data", r)

    async def skill_stats(self) -> dict:
        r = await self._auth_request("/api/call", "POST", {"tool": "skills_stats", "params": {}})
        return r.get("data", r)

    async def resource(self, service_id: str, resource_uri: str) -> dict:
        endpoint = f"/api/resource/{resource_uri}"
        return await self._request_service(service_id, endpoint)

    async def mcp(self, action: str, params: dict = None) -> Any:
        return await self._request_gateway("/api/call", "POST", {"tool": action, "params": params or {}})

    async def close(self):
        await self._http.aclose()

    def _log_call(self, call_type: str, name: str, params: Any, result: dict) -> None:
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            log_file = LOG_DIR / "calls.jsonl"
            entry = {
                "type": call_type,
                "name": name,
                "params": params,
                "status": result.get("status", 0),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            with open(log_file, "a") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


async def main():
    """CLI mode: python3 -m mcp.sdk.sonora_client <status|health|capabilities|skills|tools>"""
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    sdk = SonoraSDK()
    try:
        if cmd == "status":
            st = await sdk.status()
            print("\n🔮 SONORA SDK v2.0 — Estado del Ecosistema\n")
            print(f"   Tenant: {st.get('tenant', 'N/A')}")
            print(f"   Versión: {st.get('version', 'N/A')}")
            print(f"   Timestamp: {st.get('timestamp', 'N/A')}\n")
            services = st.get("services", {})
            for key, status in sorted(services.items()):
                icon = "🟢" if status else "🔴"
                state = "online" if status else "offline"
                print(f" {icon} {key:<14} {state}")
            summary = st.get("summary", {})
            if summary:
                print(f"\n 📊 {summary.get('online', 0)}/{summary.get('total', 0)} servicios online")
        elif cmd == "health":
            h = await sdk.health_all()
            print(json.dumps(h, indent=2, ensure_ascii=False))
        elif cmd == "capabilities":
            caps = await sdk.capabilities()
            print("\n📋 Capability Registry\n")
            for c in caps.get("capabilities", caps if isinstance(caps, list) else []):
                name = c.get("capability", c.get("name", "?"))
                maturity = c.get("maturity", "?")
                agent = c.get("agent", "?")
                print(f" • {name:<30} {maturity:<18} {agent}")
        elif cmd == "skills":
            sk = await sdk.skills()
            skills_list = sk.get("skills", sk if isinstance(sk, list) else [])
            print(f"\n📦 Skills Marketplace: {len(skills_list)} skills\n")
            by_source = {}
            for s in skills_list:
                src = s.get("source", "unknown")
                by_source[src] = by_source.get(src, 0) + 1
            for k, v in sorted(by_source.items()):
                print(f"   {k:<12} {v} skills")
        elif cmd == "tools":
            tl = await sdk.tools()
            tools_list = tl.get("tools", tl if isinstance(tl, list) else [])
            print(f"\n🔧 Tools disponibles: {len(tools_list)}\n")
            for t in tools_list:
                print(f"   • {t.get('name', t if isinstance(t, str) else '?')}")
        else:
            print(f"Unknown command: {cmd}. Use: status, health, capabilities, skills, tools")
    finally:
        await sdk.close()


if __name__ == "__main__":
    asyncio.run(main())
