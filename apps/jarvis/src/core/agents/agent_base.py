import logging
import re
from typing import Any


def match_keywords(task: str, keywords: list[str]) -> bool:
    task_lower = task.lower()
    return any(w in task_lower for w in keywords)


def extract_file_path(task: str, pattern: str = r"[\w/.-]+\.\w+") -> str | None:
    match = re.search(pattern, task)
    return match.group(0) if match else None


def success_response(agent_name: str, task: str, **extra) -> dict[str, Any]:
    return {"agent": agent_name, "task": task, "status": "success", **extra}


def error_response(agent_name: str, task: str, error: str, **extra) -> dict[str, Any]:
    return {
        "agent": agent_name,
        "task": task,
        "status": "error",
        "error": error,
        **extra,
    }


class AgentBase:
    name: str = "base"
    description: str = "Base agent class"
    timeout: int = 30

    def __init__(self):
        self.log = logging.getLogger(f"jarvis.agent.{self.name}")

    async def run(self, task: str, context: dict = None) -> dict[str, Any]:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<Agent {self.name}>"
