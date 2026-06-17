import os
from typing import Any, Dict, List

from src.core.agents.agent_base import (
    AgentBase,
    match_keywords,
    success_response,
    error_response,
)


class ExploreAgent(AgentBase):
    name = "explore"
    description = "Navegación de archivos y repositorios"
    timeout = 15

    async def run(self, task: str, context: dict = None) -> Dict[str, Any]:
        self.log.info(f"Exploring: {task[:100]}...")
        if match_keywords(task, ["busca", "search", "find", "encuentra", "grep"]):
            return self._search(task)
        elif match_keywords(task, ["estructura", "tree", "árbol", "organización"]):
            return self._structure(task)
        elif match_keywords(task, ["lee", "read", "contenido", "muestra"]):
            return self._read_batch(task)
        else:
            return self._explore(task)

    def _extract_path(self, task: str) -> str:
        import re

        for p in re.findall(r"[\w/.-]+", task):
            if os.path.isdir(p) or os.path.isfile(p):
                return p
        return "."

    def _explore(self, task: str) -> Dict[str, Any]:
        path = self._extract_path(task)
        from src.core.tools import list_files

        result = list_files(path)
        items = result.get("items", [])
        dirs = [f["name"] + "/" for f in items if f.get("type") == "directory"]
        file_list = [f["name"] for f in items if f.get("type") == "file"]
        return success_response(
            self.name,
            task,
            path=path,
            directories=dirs,
            files=file_list,
            total=len(items),
        )

    def _search(self, task: str) -> Dict[str, Any]:
        import re

        match = re.search(r'["\']([^"\']+)["\']', task)
        pattern = match.group(1) if match else task.split()[-1]
        from src.core.tools import search_code

        result = search_code(pattern)
        return success_response(
            self.name,
            task,
            pattern=pattern,
            matches=result.get("results", []),
            count=len(result.get("results", [])),
        )

    def _structure(self, task: str) -> Dict[str, Any]:
        path = self._extract_path(task)
        tree = self._build_tree(path, max_depth=3)
        return success_response(self.name, task, path=path, tree=tree)

    def _build_tree(self, path: str, max_depth: int = 3, _depth: int = 0) -> List:
        if _depth >= max_depth:
            return [{"name": "...", "type": "truncated"}]
        entries = []
        try:
            for entry in sorted(os.listdir(path)):
                full = os.path.join(path, entry)
                if os.path.isdir(full):
                    entries.append(
                        {
                            "name": entry + "/",
                            "type": "dir",
                            "children": self._build_tree(full, max_depth, _depth + 1),
                        }
                    )
                else:
                    entries.append({"name": entry, "type": "file"})
        except (PermissionError, FileNotFoundError):
            entries.append({"name": "⚠️ error", "type": "error"})
        return entries

    def _read_batch(self, task: str) -> Dict[str, Any]:
        import re

        paths = re.findall(r"[\w/.-]+\.[a-zA-Z]+", task)
        if not paths:
            return success_response(
                self.name, task, action="read", message="No file paths found in task"
            )
        from src.core.tools import read_file

        contents = []
        for p in paths[:5]:
            result = read_file(p, max_lines=200)
            contents.append(
                {
                    "path": p,
                    "status": result["status"],
                    "lines": len(result.get("content", "").splitlines()),
                    "preview": result.get("content", "")[:500],
                }
            )
        return success_response(
            self.name, task, action="read", files=contents, count=len(contents)
        )
