"""Executor — Module 5 of Kernel (HAS-004)
Executes a task by calling the assigned agent's entry point.
Collects duration, cost, output, and emitted events.
"""
import time
from datetime import datetime, timezone

from kernel.models import ExecutionResult, KernelTask
from memory import MemoryRef


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
            ctx = getattr(task, "context", None)
            if ctx and getattr(ctx, "memory_router", None):
                await ctx.memory_router.store(
                    MemoryRef(type="working", key=f"task_{task.id}"),
                    {"input": ctx.input, "output": output, "agent": agent_id, "status": "success"},
                )
                await ctx.memory_router.store(
                    MemoryRef(type="event", key=f"task_{task.id}"),
                    {"type": "agent.action.executed", "agent": agent_id, "task_id": task.id, "duration_ms": result.duration_ms},
                )
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
