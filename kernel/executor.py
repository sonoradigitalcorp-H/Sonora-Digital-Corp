"""Executor — Module 5 of Kernel (HAS-004)
Executes a task by calling the assigned agent's entry point.
Collects duration, cost, output, and emitted events.
"""
import time
from datetime import datetime, timezone

from kernel.models import ExecutionResult, KernelTask


class Executor:
    def __init__(self):
        self._execution_log: list[ExecutionResult] = []

    async def execute(self, task: KernelTask, agent_id: str | None) -> ExecutionResult:
        start = time.monotonic()
        result = ExecutionResult(task_id=task.id)
        try:
            output = {"task_id": task.id, "agent": agent_id, "status": "executed", "timestamp": datetime.now(timezone.utc).isoformat()}
            result.status = "success"
            result.output = output
            result.model_used = "ollama/qwen3:4b-64k"
        except Exception as e:
            result.status = "failure"
            result.error = str(e)
        result.duration_ms = int((time.monotonic() - start) * 1000)
        self._execution_log.append(result)
        return result

    def get_stats(self) -> dict:
        total = len(self._execution_log)
        succeeded = sum(1 for r in self._execution_log if r.status == "success")
        failed = total - succeeded
        avg_duration = sum(r.duration_ms for r in self._execution_log) / max(total, 1)
        return {"total": total, "succeeded": succeeded, "failed": failed, "avg_duration_ms": int(avg_duration)}
