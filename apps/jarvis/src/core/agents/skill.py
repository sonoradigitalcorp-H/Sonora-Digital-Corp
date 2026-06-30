import re
from typing import Any

from src.core.agents.agent_base import (
    AgentBase,
    error_response,
    match_keywords,
    success_response,
)


class SkillAgent(AgentBase):
    name = "skill"
    description = "Ejecución de skills especializadas"
    timeout = 20

    SKILL_CATALOG = [
        {
            "name": "web_fetch",
            "description": "Obtener contenido de una URL",
            "params": ["url"],
        },
        {
            "name": "analyze_code",
            "description": "Analizar código fuente (AST + métricas)",
            "params": ["path"],
        },
        {
            "name": "search_semantic",
            "description": "Búsqueda semántica en Qdrant",
            "params": ["query"],
        },
        {
            "name": "get_context",
            "description": "Contexto combinado grafo + vector",
            "params": ["query"],
        },
        {
            "name": "list_skills",
            "description": "Listar skills disponibles",
            "params": [],
        },
        {
            "name": "execute_command",
            "description": "Ejecutar comando bash (whitelist)",
            "params": ["command"],
        },
        {
            "name": "read_file",
            "description": "Leer archivo del proyecto",
            "params": ["path"],
        },
        {
            "name": "write_file",
            "description": "Escribir archivo en el proyecto",
            "params": ["path", "content"],
        },
        {
            "name": "mcporter",
            "description": "Gestionar servidores MCP",
            "params": ["action"],
        },
        {
            "name": "skill_creator",
            "description": "Crear nuevas skills para el agente",
            "params": ["name", "description"],
        },
        {
            "name": "github",
            "description": "Gestionar issues, PRs y repositorios GitHub",
            "params": ["action"],
        },
        {
            "name": "gog",
            "description": "Google Workspace: Gmail, Calendar, Drive",
            "params": ["service", "action"],
        },
        {
            "name": "taskflow",
            "description": "Tareas multi-paso con estado persistente",
            "params": ["goal"],
        },
        {
            "name": "sag",
            "description": "Texto a voz con ElevenLabs (voz natural)",
            "params": ["text"],
        },
        {
            "name": "healthcheck",
            "description": "Auditar seguridad y estado del sistema",
            "params": [],
        },
        {
            "name": "gsd",
            "description": "Get Shit Done: planificación y ejecución full-stack",
            "params": ["project"],
        },
        {
            "name": "close_loop",
            "description": "End-of-session: shippear cambios, consolidar memoria, auto-mejora",
            "params": [],
        },
        {
            "name": "reflect",
            "description": "Analizar conversaciones y proponer mejoras a agentes",
            "params": [],
        },
        {
            "name": "browser_use",
            "description": "Controlar navegador web",
            "params": ["action"],
        },
        {
            "name": "linux_desktop",
            "description": "Controlar escritorio Linux",
            "params": ["action"],
        },
    ]

    async def run(self, task: str, context: dict = None) -> dict[str, Any]:
        self.log.info(f"Skill task: {task[:100]}...")
        if match_keywords(task, ["lista", "list", "catálogo", "disponibles"]):
            return self._list_skills(task)
        elif match_keywords(task, ["ejecuta", "run", "corre", "usa", "aplica"]):
            return await self._run_skill(task)
        elif match_keywords(task, ["docs", "ayuda", "help", "cómo"]):
            return self._skill_docs(task)
        else:
            return self._list_skills(task)

    def _list_skills(self, task: str) -> dict[str, Any]:
        return success_response(
            self.name,
            task,
            action="list",
            skills=self.SKILL_CATALOG,
            count=len(self.SKILL_CATALOG),
        )

    async def _run_skill(self, task: str) -> dict[str, Any]:
        match = re.search(r"(?:skill|ejecuta|run|usa)\s+(\w+)", task.lower())
        skill_name = match.group(1) if match else None
        if not skill_name:
            names = ", ".join(s["name"] for s in self.SKILL_CATALOG)
            return error_response(
                self.name, task, f"Specify a skill name. Available: {names}"
            )
        skill = next((s for s in self.SKILL_CATALOG if s["name"] == skill_name), None)
        if not skill:
            return error_response(self.name, task, f"Skill '{skill_name}' not found")
        from src.core.tools import execute_tool

        params = {}
        for param in skill.get("params", []):
            p_match = re.search(
                rf'{param}["\']?\s*[:=]?\s*["\']?([^"\'\s,)]+)["\']?', task
            )
            if p_match:
                params[param] = p_match.group(1)
        result = execute_tool(skill_name, params)
        return success_response(
            self.name,
            task,
            action="run",
            skill=skill_name,
            params=params,
            result=result,
        )

    def _skill_docs(self, task: str) -> dict[str, Any]:
        match = re.search(r"(?:skill|docs|ayuda)\s+(\w+)", task.lower())
        skill_name = match.group(1) if match else None
        if skill_name:
            skill = next(
                (s for s in self.SKILL_CATALOG if s["name"] == skill_name), None
            )
            if skill:
                return success_response(self.name, task, action="docs", skill=skill)
        return success_response(
            self.name,
            task,
            action="docs",
            message="Specify a skill name for docs",
            skills=self.SKILL_CATALOG,
        )
