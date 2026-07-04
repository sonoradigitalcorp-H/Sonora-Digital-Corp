"""PriorityScheduler — prioridad + retry con backoff exponencial [FR2-FR3]"""
import asyncio
import logging
import time
from typing import Optional

from .queue import TaskQueue

log = logging.getLogger("execution")

BACKOFF_SECONDS = [1, 5, 30, 300]
MAX_CONCURRENT_PER_AGENT = 2


class PriorityScheduler:
    def __init__(self, queue: Optional[TaskQueue] = None):
        self.queue = queue or TaskQueue()
        self.running = {}
        self._loop_task = None

    def start(self):
        self._loop_task = asyncio.create_task(self._run_loop())

    async def stop(self):
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass

    async def _run_loop(self):
        while True:
            try:
                await self._tick()
            except Exception as e:
                log.error(f"Scheduler tick error: {e}")
            await asyncio.sleep(2)

    async def _tick(self):
        for agent in list(self.running.keys()):
            self.running[agent] = [t for t in self.running[agent] if not t.done()]
            if not self.running[agent]:
                del self.running[agent]

        for agent_name in self._get_available_agents():
            current = len(self.running.get(agent_name, []))
            if current >= MAX_CONCURRENT_PER_AGENT:
                continue

            task = self.queue.dequeue(agent=agent_name)
            if task:
                coro = self._execute_task(task)
                self.running.setdefault(agent_name, []).append(asyncio.create_task(coro))

    def _get_available_agents(self) -> list[str]:
        agents = set()
        for t in self.queue.list_tasks(status="queued", limit=100):
            agents.add(t["agent"])
        return list(agents)

    async def _execute_task(self, task: dict):
        task_id = task["id"]
        agent = task["agent"]
        operation = task["operation"]
        log.info(f"Executing {task_id}: {agent}.{operation}")

        try:
            result = await self._run_with_retry(task)
            self.queue.complete(task_id, result)
            log.info(f"Completed {task_id}: {agent}.{operation}")
        except Exception as e:
            error = str(e)
            self.queue.fail(task_id, error, retry=True)
            log.warning(f"Failed {task_id}: {error}")

    async def _run_with_retry(self, task: dict):
        last_error = None
        for attempt in range(task.get("max_retries", 3) + 1):
            try:
                if attempt > 0:
                    backoff = BACKOFF_SECONDS[min(attempt - 1, len(BACKOFF_SECONDS) - 1)]
                    log.info(f"Retry {attempt}/{task['max_retries']} for {task['id']} in {backoff}s")
                    await asyncio.sleep(backoff)

                from .executor import AgentExecutor
                executor = AgentExecutor()
                result = await executor.execute(task["agent"], task["operation"], task.get("params", {}))
                return result
            except Exception as e:
                last_error = e
                if attempt < task.get("max_retries", 3):
                    continue
                raise last_error
