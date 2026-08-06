"""Aider Harness - Test harness para Aider."""

from typing import Any, Optional
from .base import AgentHarness, HarnessConfig, HarnessResult


class AiderHarness(AgentHarness):
    """
    Aider Harness - Tests específicos para Aider.

    Casos de prueba:
    - Git commit
    - Git branch
    - Changelog
    - Cambios múltiples
    """

    def __init__(self, agent=None, config: Optional[HarnessConfig] = None):
        if agent is None:
            from src.agents.aider import AiderAgent
            agent = AiderAgent()
        super().__init__(agent, config)

    def test_commit(self, message: str = "test commit") -> HarnessResult:
        """Test: Crear commit."""
        return self.execute(
            action="commit",
            inputs={
                "task": "Crear commit",
                "message": message,
                "files": ["test.py"],
            },
            expected={"status": "success"},
        )

    def test_branch(self, branch_name: str = "test-branch") -> HarnessResult:
        """Test: Crear branch."""
        return self.execute(
            action="branch",
            inputs={
                "task": "Crear branch",
                "name": branch_name,
            },
            expected={"status": "success"},
        )

    def test_changelog(self) -> HarnessResult:
        """Test: Generar changelog."""
        return self.execute(
            action="changelog",
            inputs={
                "task": "Generar changelog",
                "from_ref": "v1.0.0",
                "to_ref": "HEAD",
            },
            expected={"status": "success"},
        )

    def test_multi_file(self, files: list[str] = None) -> HarnessResult:
        """Test: Cambios en múltiples archivos."""
        if files is None:
            files = ["file1.py", "file2.py", "file3.py"]

        return self.execute(
            action="multi-file",
            inputs={
                "task": "Modificar múltiples archivos",
                "files": files,
                "changes": {},
            },
            expected={"status": "success"},
        )
