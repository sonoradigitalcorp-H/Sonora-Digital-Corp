"""OpenCode Harness - Test harness para OpenCode."""

from typing import Any, Optional
from .base import AgentHarness, HarnessConfig, HarnessResult


class OpenCodeHarness(AgentHarness):
    """
    OpenCode Harness - Tests específicos para OpenCode.

    Casos de prueba:
    - Editar código
    - Refactorizar
    - Analizar código
    """

    def __init__(self, agent=None, config: Optional[HarnessConfig] = None):
        if agent is None:
            from src.agents.opencode import OpenCodeAgent
            agent = OpenCodeAgent()
        super().__init__(agent, config)

    def test_edit_code(self, file_path: str = "test.py") -> HarnessResult:
        """Test: Editar archivo de código."""
        return self.execute(
            action="edit",
            inputs={
                "task": "Editar archivo",
                "file": file_path,
                "changes": [{"line": 1, "content": "# edited"}],
            },
            expected={"status": "success"},
        )

    def test_refactor(self, file_path: str = "test.py") -> HarnessResult:
        """Test: Refactorizar código."""
        return self.execute(
            action="refactor",
            inputs={
                "task": "Refactorizar función",
                "file": file_path,
                "function": "old_function",
                "new_name": "new_function",
            },
            expected={"status": "success"},
        )

    def test_analyze(self, file_path: str = "test.py") -> HarnessResult:
        """Test: Analizar código."""
        return self.execute(
            action="analyze",
            inputs={
                "task": "Analizar complejidad",
                "file": file_path,
            },
            expected={"status": "success"},
        )
