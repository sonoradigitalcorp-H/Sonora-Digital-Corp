"""
JARVIS Agent Orchestrator
Multi-agent orchestration system for delegating tasks to specialized agents.
Now modular — each agent lives in src/core/agents/<name>.py
"""

import asyncio
import logging
import re
import time
import uuid
from pathlib import Path
from typing import Any

from src.core.agents import (
    AgentBase,
    CodeAgent,
    ExploreAgent,
    GbrainAgent,
    HermesAgent,
    MemoryAgent,
    OpenClawAgent,
    PRAgent,
    ResearchAgent,
    ReviewAgent,
    SalesAgent,
    SkillAgent,
    VoiceAgent,
)
from src.core.redis_streams import clear_context as redis_clear_stream
from src.core.redis_streams import push_agent_context, read_agent_context

log = logging.getLogger("jarvis.orchestrator")

# LangFuse tracing
import importlib.util

_LF_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "sonora-enterprise-os" / "scripts" / "instrument-langfuse.py"
if _LF_PATH.exists():
    _spec = importlib.util.spec_from_file_location("instrument_langfuse", str(_LF_PATH))
    _instr = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_instr)
    _tracker = _instr._tracker
else:
    _tracker = None


class AgentOrchestrator:
    """
    Orchestrates task execution across specialized agents.
    Analyzes task intent and routes to the most appropriate agent.
    """

    def __init__(self):
        self.agents: dict[str, AgentBase] = {
            "research": ResearchAgent(),
            "code": CodeAgent(),
            "explore": ExploreAgent(),
            "memory": MemoryAgent(),
            "skill": SkillAgent(),
            "voice": VoiceAgent(),
            "review": ReviewAgent(),
            "hermes": HermesAgent(),
            "openclaw": OpenClawAgent(),
            "gbrain": GbrainAgent(),
            "pr": PRAgent(),
            "sales": SalesAgent(),
        }

        self.routing_rules: list[tuple[list[str], str]] = [
            (
                [
                    "browser",
                    "navegador",
                    "chrome",
                    "abrí chrome",
                    "abre chrome",
                    "navega a",
                    "descarga de internet",
                    "scrapea",
                    "googlea",
                    "busca en internet",
                    "página web",
                ],
                "explore",
            ),
            (
                [
                    "mouse",
                    "click",
                    "teclea",
                    "pantalla",
                    "escritorio",
                    "desktop",
                    "terminal",
                    "carpeta",
                    "mueve el mouse",
                    "screenshot",
                    "captura pantalla",
                    "xdotool",
                ],
                "explore",
            ),
            (
                [
                    "buscar",
                    "investigar",
                    "search",
                    "encuentra",
                    "investigá",
                    "dónde está",
                    "qué es",
                    "explícame",
                    "explicame",
                    "decime",
                ],
                "research",
            ),
            (
                [
                    "escribe",
                    "implementa",
                    "codifica",
                    "refactoriza",
                    "escribí",
                    "implementá",
                    "codificá",
                    "refactorizá",
                    "arregla",
                    "fix",
                    "bug",
                    "función",
                    "analiza",
                    "analyze",
                    "métrica",
                    "código de",
                    "genera",
                    "arreglá",
                    "analizá",
                    "generá",
                ],
                "code",
            ),
            (
                [
                    "pull request",
                    "pullrequest",
                    "pr",
                    "prs",
                    "creá pr",
                    "crea pr",
                    "abrí pr",
                    "abre pr",
                    "nuevo pr",
                    "crear pull request",
                    "merge pr",
                    "fusioná pr",
                    "fusiona pr",
                    "revisá pr",
                    "revisa pr",
                    "lista pr",
                    "listá pr",
                    "list prs",
                    "listá los prs",
                    "auto-pr",
                    "autopr",
                    "auto pr",
                    "spec-kit pr",
                    "soulclone pr",
                ],
                "pr",
            ),
            (
                [
                    "explora",
                    "navega",
                    "listar",
                    "find",
                    "ls",
                    "explorá",
                    "navegá",
                    "listá",
                    "buscá",
                    "directorio",
                    "archivos",
                    "carpeta",
                    "mostrame",
                    "mostrá",
                    "mostrar",
                    "estructura",
                    "tree",
                    "árbol",
                ],
                "explore",
            ),
            (
                [
                    "recuerda",
                    "memoria",
                    "contexto",
                    "olvida",
                    "recordá",
                    "acordate",
                    "recuérdate",
                    "no olvides",
                    "guardá",
                    "guardar",
                    "olvidate",
                ],
                "memory",
            ),
            (
                [
                    "skill",
                    "herramienta",
                    "plugin",
                    "ejecuta",
                    "ejecutá",
                    "corré",
                    "usá",
                    "usar",
                    "skill de",
                    "gsd",
                    "close-loop",
                    "wrap-up",
                    "wrap up",
                    "get shit done",
                    "suscripción",
                    "plan",
                    "subscription",
                    "pago",
                    "checkout",
                    "factura",
                    "mercadopago",
                    "bitso",
                    "spei",
                    "pagar",
                    "comprar",
                ],
                "skill",
            ),
            (
                [
                    "mystic",
                    "onboarding",
                    "sonora",
                    "sdc",
                    "quiero empezar",
                    "me interesa",
                    "quien eres",
                    "qué haces",
                    "explorador",
                    "conquistador",
                    "agente ia",
                    "imperio",
                ],
                "research",
            ),
            (
                [
                    "habla",
                    "di",
                    "dime",
                    "voz",
                    "audio",
                    "hablá",
                    "decí",
                    "decis",
                    "hablame",
                ],
                "voice",
            ),
            (
                [
                    "revisa",
                    "review",
                    "valida",
                    "testea",
                    "revisá",
                    "revisame",
                    "validá",
                    "prueba",
                    "verifica",
                    "probá",
                    "verificá",
                ],
                "review",
            ),
            (
                [
                    "telegram",
                    "whatsapp",
                    "hermes",
                    "n8n",
                    "automatización",
                    "automatizá",
                    "mensaje",
                    "envía",
                    "notifica",
                    "notificá",
                    "mandá",
                    "manda",
                    "canal",
                    "difunde",
                    "difundí",
                ],
                "hermes",
            ),
            (
                [
                    "openclaw",
                    "gateway",
                    "agente especializado",
                    "delegá",
                    "delega",
                    "deriva",
                    "derivá",
                    "agente externo",
                ],
                "openclaw",
            ),
            (
                [
                    "lead",
                    "venta",
                    "vender",
                    "cotizar",
                    "cotizá",
                    "propuesta",
                    "cliente",
                    "deal",
                    "pipeline",
                    "sales",
                    "crm",
                    "quiero comprar",
                    "me interesa un plan",
                    "presupuesto",
                ],
                "sales",
            ),
            (
                [
                    "gbrain",
                    "cerebro",
                    "sintetiza",
                    "síntesis",
                    "synthesize",
                    "think",
                    "gap analysis",
                    "traza",
                    "traza conocimiento",
                    "grafo",
                    "capturá",
                    "capture",
                    "recordá en el cerebro",
                    "learning-loop",
                    "learning loop",
                    "aprendé",
                    "aprende",
                    "patrón",
                    "patron",
                    "anomalía",
                ],
                "gbrain",
            ),
        ]

        self.context_history: list[dict[str, Any]] = []
        self.max_context = 50

    def push_context(self, agent: str, task: str, result: dict[str, Any]) -> None:
        entry = {
            "id": str(uuid.uuid4())[:8],
            "agent": agent,
            "task": task[:200],
            "result_summary": result.get("synthesis", result.get("status", "done"))[
                :200
            ],
            "timestamp": time.time(),
        }
        self.context_history.append(entry)
        if len(self.context_history) > self.max_context:
            self.context_history.pop(0)
        # Also push to Redis Stream (non-blocking fallback)
        push_agent_context(agent, task[:200], entry["result_summary"])

    def get_context(self, limit: int = 5) -> list[dict[str, Any]]:
        # Try Redis first, fall back to local list
        redis_ctx = read_agent_context(count=limit)
        if redis_ctx:
            return redis_ctx
        return self.context_history[-limit:]

    def search_context(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        return [
            c
            for c in self.context_history
            if q in c["task"].lower() or q in c["result_summary"].lower()
        ]

    def clear_context(self) -> None:
        self.context_history.clear()
        redis_clear_stream()

    def route(self, task: str) -> str:
        task_lower = task.lower()
        set(re.findall(r"\w+", task_lower))
        for keywords, agent_name in self.routing_rules:
            if any(
                re.search(r"\b" + re.escape(kw) + r"\b", task_lower) for kw in keywords
            ):
                return agent_name
        return "research"

    async def execute(self, task: str, context: dict = None) -> dict[str, Any]:
        _start = time.time()
        agent_name = self.route(task)
        agent = self.agents[agent_name]
        ctx = context or {}
        ctx["agent"] = agent_name
        ctx["history"] = self.get_context(5)
        # Auto-query Engram for relevant past learnings
        try:
            from src.core.pipeline_bridge import format_engram_context, query_engram_context
            engram_results = query_engram_context(task, limit=3)
            engram_ctx = format_engram_context(engram_results)
            if engram_ctx:
                ctx["engram_context"] = engram_ctx
                log.info(f"Engram: {len(engram_results)} past learnings injected for {agent_name}")
        except Exception:
            pass
        log.info(f"Routing to {agent.name}: {task[:100]}...")
        try:
            result = await asyncio.wait_for(agent.run(task, ctx), timeout=agent.timeout)
            result["status"] = "success"
        except TimeoutError:
            log.error(f"Agent {agent.name} timed out after {agent.timeout}s")
            result = {
                "agent": agent_name,
                "status": "error",
                "error": f"Timeout after {agent.timeout}s",
            }
        except Exception as e:
            log.error(f"Agent {agent.name} error: {e}")
            result = {"agent": agent_name, "status": "error", "error": str(e)}
        result["agent"] = agent_name
        result["task"] = task
        result["execution_time"] = time.time()
        self.push_context(agent_name, task, result)

        # Auto-store errors in Engram
        if result.get("status") == "error" and str(result.get("error", "")) != "unknown":
            try:
                from src.core.pipeline_bridge import store_spec_completion
                store_spec_completion(
                    f"error-{agent_name}-{int(time.time())}",
                    f"Agent {agent_name} failed: {result.get('error', 'unknown')[:200]}",
                    ["error", agent_name],
                )
            except Exception:
                pass
        # LangFuse trace
        if _tracker:
            _tracker.trace(
                name=f"orchestrator.execute.{agent_name}",
                input={"task": task[:200]},
                output={"status": result["status"]},
                tenant="sdc-core", agent=agent_name,
                duration_ms=(time.time() - _start) * 1000,
                metadata={"agent": agent_name, "timeout": agent.timeout},
                status="success" if result["status"] == "success" else "error",
            )
        return result

    async def execute_parallel(
        self, tasks: list[str], context: dict = None
    ) -> list[dict[str, Any]]:
        log.info(f"Running {len(tasks)} tasks in parallel")
        ctx = context or {}
        results = await asyncio.gather(
            *[self.execute(task, ctx) for task in tasks], return_exceptions=True
        )
        return [
            {"status": "error", "error": str(r)} if isinstance(r, Exception) else r
            for r in results
        ]

    def list_agents(self) -> list[dict[str, Any]]:
        return [
            {"name": a.name, "description": a.description, "timeout": a.timeout}
            for a in self.agents.values()
        ]


_orchestrator: AgentOrchestrator | None = None


def get_orchestrator() -> AgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator


async def execute_task(task: str, context: dict = None) -> dict[str, Any]:
    return await get_orchestrator().execute(task, context)
