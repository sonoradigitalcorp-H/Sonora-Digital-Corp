"""Agent Router — Module 4 of Kernel (HAS-004)
Routes tasks to the appropriate agent based on capability registry.
"""
import yaml
from pathlib import Path

from kernel.models import KernelTask


REPO = Path(__file__).resolve().parent.parent


class AgentRouter:
    def __init__(self):
        self._registry: dict[str, dict] = {}
        self._load_registry()

    def _load_registry(self):
        registry_path = REPO / "agents" / "registry.yaml"
        if registry_path.exists():
            data = yaml.safe_load(registry_path.read_text())
            for agent in data.get("agents", []):
                self._registry[agent["name"]] = {
                    "name": agent["name"],
                    "role": agent.get("role", ""),
                    "capabilities": agent.get("capabilities", []),
                    "status": agent.get("status", "active"),
                    "level": agent.get("level", "L1"),
                    "model": agent.get("model", ""),
                }

    def route(self, task: KernelTask) -> str | None:
        if task.agent:
            return task.agent if task.agent in self._registry else None
        if task.capability:
            return self._find_best_agent(task.capability)
        return self._find_default_agent()

    def available(self, capability: str) -> list[str]:
        result = []
        for name, info in self._registry.items():
            caps = info.get("capabilities", [])
            if "*" in caps or capability in caps:
                result.append(name)
        return result

    def health(self, agent_id: str) -> dict:
        info = self._registry.get(agent_id, {})
        return {"agent": agent_id, "status": info.get("status", "unknown"), "level": info.get("level", "")}

    def list_agents(self) -> list[dict]:
        return list(self._registry.values())

    def _find_best_agent(self, capability: str) -> str | None:
        available = self.available(capability)
        if available:
            return available[0]
        return None

    def _find_default_agent(self) -> str | None:
        for name, info in self._registry.items():
            if "*" in info.get("capabilities", []):
                return name
        return None
