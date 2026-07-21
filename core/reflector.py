"""Reflector — Module 6 of Kernel (HAS-004)
Post-execution analysis: scores result, extracts lessons, emits events.
"""
from datetime import datetime, timezone

from kernel.models import ExecutionResult, KernelTask


class Reflector:
    async def reflect(self, task: KernelTask, result: ExecutionResult) -> dict:
        score = self._score(task, result)
        lessons = self._extract_lessons(task, result)
        summary = {
            "task_id": task.id,
            "score": score,
            "lessons": lessons,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return summary

    def _score(self, task: KernelTask, result: ExecutionResult) -> int:
        base = 50
        if result.status == "success":
            base += 30
        if result.duration_ms < 1000:
            base += 10
        elif result.duration_ms > 10000:
            base -= 10
        if result.error:
            base -= 40
        return max(0, min(100, base))

    def _extract_lessons(self, task: KernelTask, result: ExecutionResult) -> list[str]:
        lessons = []
        if result.status == "failure":
            lessons.append(f"Task '{task.id}' failed: {result.error}")
        if result.duration_ms > 5000:
            lessons.append(f"Task '{task.id}' took {result.duration_ms}ms — consider optimization")
        if task.agent and not result.model_used:
            lessons.append(f"Agent '{task.agent}' did not specify model used")
        return lessons
