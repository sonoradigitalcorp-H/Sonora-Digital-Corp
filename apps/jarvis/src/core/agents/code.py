from typing import Any

from src.core.agents.agent_base import (
    AgentBase,
    error_response,
    extract_file_path,
    match_keywords,
    success_response,
)


class CodeAgent(AgentBase):
    name = "code"
    description = "Análisis y generación de código"
    timeout = 60

    async def run(self, task: str, context: dict = None) -> dict[str, Any]:
        self.log.info(f"Code task: {task[:100]}...")
        if match_keywords(task, ["analiza", "analyze", "métrica", "complejidad"]):
            return await self._analyze(task)
        elif match_keywords(task, ["genera", "create", "escribe", "write", "nuevo"]):
            return await self._generate(task)
        elif match_keywords(task, ["lee", "read", "muestra", "cat", "código de"]):
            return await self._read(task)
        elif match_keywords(task, ["fix", "bug", "arregla", "corrige", "error"]):
            return await self._fix_bug(task)
        else:
            return await self._analyze(task)

    async def _analyze(self, task: str) -> dict[str, Any]:
        path = extract_file_path(task)
        if not path:
            return error_response(
                self.name,
                task,
                "No encontré qué archivo analizar. Especifica una ruta.",
            )
        from src.core.tools import read_file

        content = read_file(path, max_lines=500)
        if content["status"] != "success":
            return error_response(
                self.name, task, f"No pude leer {path}: {content.get('message')}"
            )
        lines = content["content"].splitlines()
        total = len(lines)
        blank = sum(1 for l in lines if not l.strip())
        comment = sum(1 for l in lines if l.strip().startswith("#"))
        return success_response(
            self.name,
            task,
            file=path,
            metrics={
                "total_lines": total,
                "code_lines": total - blank - comment,
                "blank_lines": blank,
                "comment_lines": comment,
            },
            content=content["content"][:1000],
        )

    async def _generate(self, task: str) -> dict[str, Any]:
        path = extract_file_path(task)
        if not path:
            return error_response(
                self.name, task, "Especifica la ruta del archivo a generar."
            )
        from src.core.llm import ask

        code = ask(
            f"Genera código Python para: {task}\nSolo código, sin explicaciones."
        )
        from src.core.tools import write_file

        write_file(path, code)
        return success_response(
            self.name, task, file=path, lines=len(code.splitlines()), preview=code[:500]
        )

    async def _read(self, task: str) -> dict[str, Any]:
        import re

        paths = re.findall(r"[\w/.-]+\.\w+", task)
        if not paths:
            return error_response(self.name, task, "Especifica qué archivo(s) leer.")
        from src.core.tools import read_file

        results = []
        for p in paths[:3]:
            r = read_file(p, max_lines=100)
            results.append(
                {"path": p, "status": r["status"], "content": r.get("content", "")}
            )
        return success_response(self.name, task, files=results)

    async def _fix_bug(self, task: str) -> dict[str, Any]:
        path = extract_file_path(task)
        if not path:
            return error_response(self.name, task, "Especifica qué archivo arreglar.")
        from src.core.tools import read_file, write_file

        content = read_file(path, max_lines=500)
        if content["status"] != "success":
            return error_response(self.name, task, f"No pude leer {path}")
        from src.core.llm import ask

        fixed_code = ask(
            f"Este archivo tiene un bug:\n\n{content['content'][:2000]}\n\n"
            f"Bug descrito: {task}\n"
            f"Devuelve SOLO el código corregido, sin explicaciones."
        )
        write_file(path, fixed_code)
        return success_response(
            self.name,
            task,
            file=path,
            message="Archivo corregido",
            preview=fixed_code[:500],
        )
