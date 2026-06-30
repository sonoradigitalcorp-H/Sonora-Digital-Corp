import logging
from typing import Any

# Import agents from the existing AgentOrchestrator
from .agents.agent_base import AgentBase


class Harness:
    """
    SDD Agent Harness - Orquestador de fases basado en Spec-Driven Development.
    Implementa un pipeline estricto de: Research -> Spec -> Design -> Apply -> Verify -> Archive.
    """

    def __init__(self):
        self.log = logging.getLogger("jarvis.harness")
        self._agents: dict[str, AgentBase] = {}
        self._history: list[dict[str, Any]] = []
        # We will populate agents on demand via get_agent method

    async def execute(
        self, task: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Executes a task through the SDD pipeline phases.
        Returns the result of the last phase (typically Archive).
        """
        self.log.info(f"Starting Harness execution: {task[:100]}")

        # Initialize context if not provided
        ctx = context or {}
        ctx["history"] = self._history[-3:] if self._history else []

        # Run each phase in order
        phases = ["research", "spec", "design", "apply", "verify", "archive"]
        result: dict[str, Any] = {"status": "pending"}

        for phase in phases:
            self.log.info(f"Executing phase: {phase}")
            agent = self._get_agent_for_phase(phase)
            if agent is None:
                self.log.error(f"No agent found for phase: {phase}")
                result = {
                    "status": "error",
                    "error": f"Missing agent for phase {phase}",
                }
                break

            # Execute the phase
            phase_result = await agent.run(task, ctx)
            phase_result["phase"] = phase
            self._history.append(phase_result)

            # Stop on error unless it's just a warning (we'll treat any error as stop)
            if phase_result.get("status") == "error":
                self.log.error(f"Phase {phase} failed: {phase_result.get('error')}")
                result = phase_result
                break

            # Update context with successful result
            ctx.update(
                {f"{phase}_result": phase_result, "last_successful_phase": phase}
            )
            result = phase_result

        self.log.info(f"Harness execution completed: {result.get('status')}")
        return result

    def _get_agent_for_phase(self, phase: str) -> AgentBase | None:
        """
        Returns the appropriate agent instance for a given phase.
        Maps phase names to actual agent classes.
        """
        # Map phase to agent name (lowercase for matching)
        agent_map = {
            "research": "research",
            "spec": "spec",
            "design": "design",
            "apply": "apply",
            "verify": "verify",
            "archive": "archive",
        }

        agent_name = agent_map.get(phase)
        if agent_name is None:
            return None

        # Lazy load agent instance
        if agent_name not in self._agents:
            try:
                # Import the specific agent class
                if agent_name == "research":
                    from .agents.research import ResearchAgent

                    self._agents[agent_name] = ResearchAgent()
                elif agent_name == "spec":
                    from .agents.spec import SpecAgent

                    self._agents[agent_name] = SpecAgent()
                elif agent_name == "design":
                    from .agents.design import DesignAgent

                    self._agents[agent_name] = DesignAgent()
                elif agent_name == "apply":
                    from .agents.apply import ApplyAgent

                    self._agents[agent_name] = ApplyAgent()
                elif agent_name == "verify":
                    from .agents.verify import VerifyAgent

                    self._agents[agent_name] = VerifyAgent()
                elif agent_name == "archive":
                    from .agents.archive import ArchiveAgent

                    self._agents[agent_name] = ArchiveAgent()
                elif agent_name == "code":
                    from .agents.code import CodeAgent

                    self._agents[agent_name] = CodeAgent()
                elif agent_name == "review":
                    from .agents.review import ReviewAgent

                    self._agents[agent_name] = ReviewAgent()
                elif agent_name == "memory":
                    from .agents.memory import MemoryAgent

                    self._agents[agent_name] = MemoryAgent()
                elif agent_name == "explore":
                    from .agents.explore import ExploreAgent

                    self._agents[agent_name] = ExploreAgent()
                else:
                    self.log.error(f"No agent implementation found for: {agent_name}")
                    return None
            except ImportError as e:
                self.log.error(f"Failed to import agent {agent_name}: {e}")
                return None

        return self._agents[agent_name]

    def get_history(self) -> list[dict[str, Any]]:
        """Returns the execution history of the harness."""
        return self._history.copy()

    def clear_history(self):
        """Clears the execution history."""
        self._history = []
