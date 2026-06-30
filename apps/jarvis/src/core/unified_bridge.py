"""
Unified Bridge — JARVIS ↔ Hermes ↔ OpenClaw
Single integration layer that connects all systems into one.
"""

import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")
load_dotenv(Path.home() / "sdcorp" / ".secrets" / "keys.env")

log = logging.getLogger("jarvis.unified")

HERMES_API = os.getenv("HERMES_API_URL", "http://localhost:8000")
OPENCLAW_API = os.getenv("OPENCLAW_API_URL", "http://localhost:18789")
HERMES_API_KEY = os.getenv("HERMES_API_KEY", "")


class HermesBridge:
    """Bridge to Hermes: messaging (Telegram/WhatsApp), n8n, ERP."""

    def __init__(self):
        self.api_url = HERMES_API
        self.headers = {"Content-Type": "application/json"}
        if HERMES_API_KEY:
            self.headers["Authorization"] = f"Bearer {HERMES_API_KEY}"

    def health(self) -> dict:
        try:
            r = requests.get(f"{self.api_url}/health", timeout=5)
            return r.json() if r.ok else {"status": "error"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def send_telegram(self, chat_id: str, text: str) -> dict:
        try:
            r = requests.post(
                f"{self.api_url}/api/telegram/send",
                headers=self.headers,
                json={"chat_id": chat_id, "text": text},
                timeout=10,
            )
            return r.json() if r.ok else {"status": "error", "detail": r.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def send_whatsapp_hermes(self, to: str, text: str) -> dict:
        """Send WhatsApp via Hermes API (port 8000)."""
        try:
            from dotenv import load_dotenv

            load_dotenv()
            api_key = os.environ.get("HERMES_API_KEY", "")
            r = requests.post(
                f"{self.api_url}/api/wa/send",
                headers={"Content-Type": "application/json", "x-api-key": api_key},
                json={"to": to, "text": text},
                timeout=10,
            )
            return r.json() if r.ok else {"status": "error", "detail": r.text[:200]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def send_whatsapp(self, to: str, text: str) -> dict:
        try:
            r = requests.post(
                f"{self.api_url}/api/whatsapp/send",
                headers=self.headers,
                json={"to": to, "text": text},
                timeout=10,
            )
            return r.json() if r.ok else {"status": "error", "detail": r.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def trigger_n8n(self, workflow_id: str, data: dict = None) -> dict:
        try:
            r = requests.post(
                f"{self.api_url}/api/n8n/trigger/{workflow_id}",
                headers=self.headers,
                json=data or {},
                timeout=30,
            )
            return r.json() if r.ok else {"status": "error", "detail": r.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_messages(self, limit: int = 50) -> list:
        try:
            r = requests.get(
                f"{self.api_url}/api/messages",
                headers=self.headers,
                params={"limit": limit},
                timeout=10,
            )
            return r.json() if r.ok else []
        except Exception as e:
            log.error(f"Hermes get_messages error: {e}")
            return []


class GbrainBridge:
    """Bridge to GBrain: synthesis + graph + gap analysis via CLI.
    Uses CLI directly (no MCP auth needed) as the user requested.
    """

    def __init__(self):
        self.brain_dir = os.path.expanduser("~/.gbrain")
        self.brain_db = os.path.join(self.brain_dir, "brain.pglite")

    def health(self) -> dict:
        if os.path.exists(self.brain_db):
            size = os.path.getsize(self.brain_db)
            return {
                "status": "ok",
                "engine": "pglite",
                "db_size_mb": round(size / 1024 / 1024, 1),
            }
        return {"status": "offline", "engine": "none"}

    def _run_cli(self, *args: str) -> dict:
        try:
            import subprocess

            result = subprocess.run(
                ["gbrain"] + list(args),
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.expanduser("~/.gbrain"),
            )
            if result.returncode == 0:
                return {"status": "success", "output": result.stdout.strip()}
            return {"status": "error", "error": result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {"status": "error", "error": "timeout"}
        except FileNotFoundError:
            return {"status": "error", "error": "gbrain CLI no instalado"}

    def search(self, query: str, limit: int = 5) -> dict:
        return self._run_cli("search", query, "--limit", str(limit))

    def think(self, query: str) -> dict:
        """Synthesized answer with citations and gap analysis."""
        return self._run_cli("think", query)

    def capture(self, text: str) -> dict:
        """Store a thought/piece of information."""
        return self._run_cli("capture", text)

    def status(self) -> dict:
        stats = self.health()
        if stats["status"] == "ok":
            skills = self._run_cli("skillpack", "list")
            stats["skills"] = skills.get("output", "unknown")
        return stats


class OpenClawBridge:
    """Bridge to OpenClaw: gateway for specialized AI agents."""

    def __init__(self):
        self.api_url = OPENCLAW_API

    def health(self) -> dict:
        try:
            r = requests.get(f"{self.api_url}/health", timeout=5)
            return r.json() if r.ok else {"status": "error"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def list_agents(self) -> list:
        try:
            r = requests.get(f"{self.api_url}/v1/agents", timeout=5)
            return r.json() if r.ok else []
        except Exception as e:
            log.error(f"OpenClaw list_agents error: {e}")
            return []

    def list_models(self) -> list:
        try:
            r = requests.get(f"{self.api_url}/v1/models", timeout=5)
            return r.json() if r.ok else []
        except Exception:
            return []

    def chat(self, agent_id: str, message: str) -> dict:
        try:
            r = requests.post(
                f"{self.api_url}/v1/chat",
                json={"agent_id": agent_id, "message": message},
                timeout=60,
            )
            return r.json() if r.ok else {"status": "error", "detail": r.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}


class UnifiedMemory:
    """Single memory layer across Neo4j + Qdrant + Hermes Postgres + Redis."""

    def __init__(self, neo4j_store=None, qdrant_client=None):
        self.neo4j = neo4j_store
        self.qdrant = qdrant_client
        self.memory_cache = {}

    def store(self, key: str, value: str, source: str = "jarvis") -> bool:
        success = False
        if self.neo4j:
            try:
                self.neo4j.save_memory(key, value)
                success = True
            except Exception as e:
                log.error(f"Neo4j store error: {e}")
        self.memory_cache[key] = {"value": value, "source": source}
        return success

    def recall(self, key: str) -> str | None:
        if key in self.memory_cache:
            return self.memory_cache[key]["value"]
        if self.neo4j:
            try:
                result = self.neo4j.get_memory(key)
                if result:
                    return result
            except Exception as e:
                log.error(f"Neo4j recall error: {e}")
        return None

    def search(self, query: str, limit: int = 5) -> list:
        results = []
        if self.qdrant:
            try:
                results = self.qdrant.search(query, limit=limit)
            except Exception as e:
                log.error(f"Qdrant search error: {e}")
        return results

    def status(self) -> dict:
        return {
            "cache_entries": len(self.memory_cache),
            "neo4j": bool(self.neo4j),
            "qdrant": bool(self.qdrant),
        }


class HumanInTheLoop:
    """Gate for human approval on important decisions.
    - Auto: routine tasks (code gen, search, recall)
    - Human: deploy, execute commands, financial ops, data deletion
    """

    APPROVAL_REQUIRED = [
        "execute_command",
        "docker_deploy",
        "delete_session",
        "purge_memory",
        "send_webhook",
        "modify_system",
    ]

    def __init__(self, approval_callback=None):
        self.pending = {}
        self.callback = approval_callback

    def requires_approval(self, action: str) -> bool:
        return action in self.APPROVAL_REQUIRED

    def request(self, action: str, details: dict) -> str:
        import uuid

        ticket = str(uuid.uuid4())[:8]
        self.pending[ticket] = {
            "action": action,
            "details": details,
            "status": "pending",
        }
        if self.callback:
            self.callback(ticket, action, details)
        return ticket

    def approve(self, ticket: str) -> bool:
        if ticket in self.pending and self.pending[ticket]["status"] == "pending":
            self.pending[ticket]["status"] = "approved"
            return True
        return False

    def reject(self, ticket: str) -> bool:
        if ticket in self.pending and self.pending[ticket]["status"] == "pending":
            self.pending[ticket]["status"] = "rejected"
            return True
        return False

    def pending_count(self) -> int:
        return sum(1 for v in self.pending.values() if v["status"] == "pending")

    def list_pending(self) -> list:
        return [
            {"ticket": k, **v}
            for k, v in self.pending.items()
            if v["status"] == "pending"
        ]


class UnifiedSystem:
    """The one system to rule them all - JARVIS + Hermes + OpenClaw."""

    def __init__(self, neo4j_store=None, qdrant_client=None):
        self.hermes = HermesBridge()
        self.openclaw = OpenClawBridge()
        if qdrant_client is None:
            try:
                from src.core.rag import rag

                qdrant_client = rag
            except Exception:
                qdrant_client = None
        self.memory = UnifiedMemory(neo4j_store, qdrant_client)
        self.control = HumanInTheLoop()
        self.initialized = False

    def init(self) -> dict:
        hermes_health = self.hermes.health()
        openclaw_health = self.openclaw.health()
        memory_status = self.memory.status()
        self.initialized = True
        return {
            "status": "unified",
            "hermes": hermes_health.get("status", "unknown"),
            "openclaw": openclaw_health.get("status", "unknown"),
            "memory": memory_status,
            "human_control": {"pending": self.control.pending_count()},
        }

    def status(self) -> dict:
        return {
            "hermes": self.hermes.health(),
            "openclaw": self.openclaw.health(),
            "memory": self.memory.status(),
            "human_control_pending": self.control.pending_count(),
        }

    def process(self, task: str, context: dict = None) -> dict:
        import asyncio

        from src.core.orchestrator import get_orchestrator

        orch = get_orchestrator()
        ctx = context or {}
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(orch.execute(task, ctx), loop)
                return future.result(timeout=30)
            else:
                return asyncio.run(orch.execute(task, ctx))
        except Exception as e:
            return {"status": "error", "error": str(e), "agent": "unified"}
