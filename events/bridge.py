"""OpenClaw Bridge — connects SDC event bus to OpenClaw skill execution.
Allows the event bus to dispatch proactive skill calls to OpenClaw.
"""
import json
import urllib.request
import urllib.error
from typing import Optional

OPENCLAW_URL = "http://localhost:18789"
OPENCLAW_API_KEY = ""


class OpenClawBridge:
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = (base_url or OPENCLAW_URL).rstrip("/")
        self.api_key = api_key or OPENCLAW_API_KEY

    def execute(self, skill: str, params: dict = None) -> Optional[dict]:
        """Execute an OpenClaw skill command."""
        payload = {"command": skill, "args": params or {}}
        data = json.dumps(payload).encode()

        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/execute",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": True, "status": e.code, "body": e.read().decode()}
        except Exception as e:
            return {"error": True, "message": str(e)}

    def available_skills(self) -> list:
        """List skills registered in OpenClaw."""
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/skills",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                return data.get("skills", [])
        except Exception:
            return []
