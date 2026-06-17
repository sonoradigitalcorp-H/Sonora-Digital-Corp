from typing import Any, Dict

from src.core.agents.agent_base import (
    AgentBase,
    match_keywords,
    extract_file_path,
    success_response,
    error_response,
)


class ReviewAgent(AgentBase):
    name = "review"
    description = "Code review y validación de código"
    timeout = 30

    async def run(self, task: str, context: dict = None) -> Dict[str, Any]:
        self.log.info(f"Review task: {task[:100]}...")
        if match_keywords(task, ["archivo", "file", "revisa", "analiza"]):
            return self._review_file(task)
        elif match_keywords(task, ["snippet", "código", "code", "pedazo"]):
            return self._review_snippet(task)
        elif match_keywords(task, ["sugiere", "suggest", "mejora", "fix"]):
            return self._suggest_fixes(task)
        else:
            return self._review_file(task)

    def _review_file(self, task: str) -> Dict[str, Any]:
        path = extract_file_path(task, r"[\w/.-]+\.[a-zA-Z]+")
        if not path:
            return error_response(
                self.name, task, "Especificá qué archivo revisar, no te hagas"
            )
        from src.core.tools import read_file

        result = read_file(path, max_lines=1000)
        if result["status"] != "success":
            return error_response(
                self.name, task, f"No pude leer {path}: {result.get('message')}"
            )
        content = result["content"]
        lines = content.splitlines()
        total = len(lines)
        issues = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and len(line) > 150:
                issues.append(
                    {
                        "line": i,
                        "type": "style",
                        "severity": "warning",
                        "message": f"Línea demasiado larga ({len(line)} chars, max 150)",
                    }
                )
            if stripped.startswith("TODO"):
                issues.append(
                    {
                        "line": i,
                        "type": "todo",
                        "severity": "info",
                        "message": stripped[:80],
                    }
                )
            if stripped.startswith("FIXME"):
                issues.append(
                    {
                        "line": i,
                        "type": "bug",
                        "severity": "error",
                        "message": stripped[:80],
                    }
                )
            if stripped.startswith("print(") or stripped.startswith("console.log("):
                issues.append(
                    {
                        "line": i,
                        "type": "debug",
                        "severity": "info",
                        "message": "Debug statement left in code",
                    }
                )
        blank = sum(1 for l in lines if not l.strip())
        comment = sum(1 for l in lines if l.strip().startswith(("#", "//", "/*", "*")))
        score = max(
            1,
            round(
                10.0
                - min(3, len([i for i in issues if i["severity"] == "error"]) * 1.0)
                - min(3, len([i for i in issues if i["severity"] == "warning"]) * 0.5)
                - min(2, len([i for i in issues if i["severity"] == "info"]) * 0.2),
                1,
            ),
        )
        if total == 0:
            score = 0
        return success_response(
            self.name,
            task,
            action="review_file",
            file=path,
            metrics={
                "total_lines": total,
                "code_lines": total - blank - comment,
                "blank_lines": blank,
                "comment_lines": comment,
            },
            issues=issues[:30],
            issue_count=len(issues),
            score=score,
        )

    def _review_snippet(self, task: str) -> Dict[str, Any]:
        import re

        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", task, re.DOTALL)
        if not code_blocks:
            return success_response(
                self.name,
                task,
                action="review_snippet",
                message="No se encontró bloque de código. Pasame el snippet entre ```",
            )
        code = code_blocks[0]
        lines = code.splitlines()
        issues = []
        prev_line = ""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and len(stripped) > 150:
                issues.append(
                    {
                        "line": i,
                        "type": "style",
                        "severity": "warning",
                        "message": "Línea muy larga",
                    }
                )
            if stripped.startswith("TODO") or stripped.startswith("FIXME"):
                issues.append(
                    {
                        "line": i,
                        "type": "todo",
                        "severity": "info",
                        "message": stripped[:80],
                    }
                )
            if stripped.startswith("import ") and prev_line.strip().startswith(
                "import "
            ):
                issues.append(
                    {
                        "line": i,
                        "type": "style",
                        "severity": "info",
                        "message": "Múltiples imports, agrupar con import on line",
                    }
                )
            prev_line = stripped
        score = 8.0 if not issues else 6.0
        return success_response(
            self.name,
            task,
            action="review_snippet",
            code=code[:500],
            metrics={"total_lines": len(lines)},
            issues=issues[:20],
            issue_count=len(issues),
            score=round(score, 1),
        )

    def _suggest_fixes(self, task: str) -> Dict[str, Any]:
        path = extract_file_path(task, r"[\w/.-]+\.[a-zA-Z]+")
        if not path:
            return success_response(
                self.name,
                task,
                action="suggest_fixes",
                message="Decime qué archivo mejorar y tiro sugerencias",
            )
        from src.core.tools import read_file

        result = read_file(path, max_lines=500)
        if result["status"] != "success":
            return error_response(self.name, task, f"No pude leer {path}")
        lines = result["content"].splitlines()
        suggestions = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if "TODO" in stripped:
                suggestions.append(
                    {
                        "line": i,
                        "type": "unresolved_todo",
                        "suggestion": "Resolve or remove TODO before production",
                    }
                )
            if len(line) > 150:
                suggestions.append(
                    {
                        "line": i,
                        "type": "long_line",
                        "suggestion": f"Break line into multiple lines (>{150} chars)",
                    }
                )
        return success_response(
            self.name,
            task,
            action="suggest_fixes",
            file=path,
            suggestions=suggestions[:20],
            suggestion_count=len(suggestions),
        )
