"""AgentExecutor — ejecuta operaciones en agentes [FR4]"""
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent.parent


class AgentExecutor:
    def __init__(self, repo: Optional[Path] = None):
        self.repo = repo or REPO

    async def execute(self, agent: str, operation: str, params: dict) -> dict:
        handler = self._get_handler(agent, operation)
        if handler:
            return await handler(params)

        return await self._default_execute(agent, operation, params)

    def _get_handler(self, agent: str, operation: str):
        registry = {
            "mystic": {"plan": self._run_script, "doc": self._run_script},
            "builder": {"write.code": self._run_script, "build.docker": self._run_script, "run.tests": self._run_tests},
            "auditor": {"audit.compliance": self._run_compliance, "check.truth": self._run_truth_check},
            "devops": {"docker.*": self._run_script, "systemctl.*": self._run_script},
            "process-doc": {"write.docs": self._run_script, "generate.doc": self._run_auto_doc},
        }
        agent_ops = registry.get(agent, {})
        if operation in agent_ops:
            return agent_ops[operation]
        for pattern, handler in agent_ops.items():
            if pattern.endswith(".*") and operation.startswith(pattern[:-1]):
                return handler
        return None

    async def _run_script(self, params: dict) -> dict:
        script = params.get("script", "")
        args = params.get("args", [])
        if not script:
            return {"status": "error", "error": "no script specified"}
        script_path = self.repo / script
        if not script_path.exists():
            script_path = self.repo / "scripts" / script
        if not script_path.exists():
            return {"status": "error", "error": f"script not found: {script}"}
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)] + args,
                capture_output=True, text=True, timeout=60, cwd=str(self.repo)
            )
            return {
                "status": "completed",
                "stdout": result.stdout[-500:],
                "stderr": result.stderr[-500:],
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "error": "timeout (60s)"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _run_tests(self, params: dict) -> dict:
        test_path = params.get("test_path", "tests/")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-q", "--no-header"],
                capture_output=True, text=True, timeout=120, cwd=str(self.repo)
            )
            return {
                "status": "completed",
                "stdout": result.stdout[-500:],
                "stderr": result.stderr[-500:],
                "returncode": result.returncode,
                "passed": "passed" in result.stdout and "failed" not in result.stdout,
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "error": "test timeout (120s)"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _run_compliance(self, params: dict) -> dict:
        try:
            sys.path.insert(0, str(self.repo))
            from apps.measure.guardian.compliance_auditor import run_all
            violations = run_all()
            return {"status": "completed", "violations": len(violations), "details": violations[:5]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _run_truth_check(self, params: dict) -> dict:
        try:
            result = subprocess.run(
                [sys.executable, str(self.repo / "scripts" / "validate-truth.py")],
                capture_output=True, text=True, timeout=30, cwd=str(self.repo)
            )
            return {"status": "completed", "valid": result.returncode == 0, "output": result.stdout[-300:]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _run_auto_doc(self, params: dict) -> dict:
        try:
            result = subprocess.run(
                [sys.executable, str(self.repo / "scripts" / "auto-doc.py"), "--auto"],
                capture_output=True, text=True, timeout=30, cwd=str(self.repo)
            )
            return {"status": "completed", "output": result.stdout[-300:]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _default_execute(self, agent: str, operation: str, params: dict) -> dict:
        return {
            "status": "simulated",
            "agent": agent,
            "operation": operation,
            "note": f"Agent {agent} has no handler for {operation}. Task recorded.",
        }
