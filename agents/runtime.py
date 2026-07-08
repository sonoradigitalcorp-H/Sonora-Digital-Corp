import yaml
from pathlib import Path

from agents.base import HermesAgent
from agents.types import AgentContext, AgentResult

REPO = Path(__file__).resolve().parent.parent


class AgentRuntime:
    def __init__(self):
        self._agents: dict[str, HermesAgent] = {}
        self._states: dict[str, str] = {}
        self._registry = self._load_registry()

    def _load_registry(self) -> list[dict]:
        path = REPO / "agents" / "registry.yaml"
        if not path.exists():
            path2 = REPO / "agents" / "index.yaml"
            if path2.exists():
                data = yaml.safe_load(path2.read_text())
                return data.get("agents", [])
            return []
        data = yaml.safe_load(path.read_text())
        return data.get("agents", [])

    def register(self, agent: HermesAgent):
        self._agents[agent.agent_id] = agent
        self._states[agent.agent_id] = "idle"

    def get(self, agent_id: str) -> HermesAgent | None:
        return self._agents.get(agent_id)

    def list_agents(self) -> list[dict]:
        results = []
        for agent in self._registry:
            status = self._states.get(agent.get("name", ""), "registered")
            results.append({"id": agent.get("name"), "role": agent.get("role"), "status": status, "capabilities": agent.get("capabilities", [])})
        for agent_id, agent in self._agents.items():
            exists = any(r["id"] == agent_id for r in results)
            if not exists:
                results.append({"id": agent_id, "role": "", "status": self._states.get(agent_id, "registered"), "capabilities": agent.capabilities})
        return results

    def find_by_capability(self, capability: str) -> list[str]:
        matches = []
        for entry in self._registry:
            caps = entry.get("capabilities", [])
            if any(capability in c for c in caps):
                matches.append(entry.get("name", ""))
        for agent_id, agent in self._agents.items():
            if any(capability in c for c in agent.capabilities):
                if agent_id not in matches:
                    matches.append(agent_id)
        return matches

    async def execute(self, agent_id: str, context: AgentContext) -> AgentResult:
        agent = self._agents.get(agent_id)
        if not agent:
            return AgentResult(status="failure", output=None, reasoning=f"Agent '{agent_id}' not found", score=0)
        self._states[agent_id] = "thinking"
        try:
            result = await agent.think(context)
            self._states[agent_id] = "idle"
            return result
        except Exception as e:
            self._states[agent_id] = "failure"
            return AgentResult(status="failure", output=None, reasoning=str(e), score=0)

    def get_state(self, agent_id: str) -> str:
        return self._states.get(agent_id, "registered")

    def get_stats(self) -> dict:
        return {
            "registered": len(self._registry),
            "loaded": len(self._agents),
            "states": {aid: s for aid, s in self._states.items() if s != "registered"},
        }
