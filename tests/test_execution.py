"""Tests para Execution Kernel — queue, scheduler, checkpoint, CLI, API [FR1-FR7]"""
import json
import sys
import pytest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from apps.decide.execution.queue import TaskQueue


@pytest.fixture
def tmp_queue(tmp_path):
    db = tmp_path / "test_queue.db"
    return TaskQueue(db_path=db)


class TestTaskQueue:
    def test_submit(self, tmp_queue):
        t = tmp_queue.submit("builder", "write.code", params={"file": "test.py"}, priority=1)
        assert t["status"] == "queued"
        assert t["agent"] == "builder"
        assert t["id"].startswith("exec_")

    def test_dequeue(self, tmp_queue):
        tmp_queue.submit("builder", "write.code", priority=0)
        t = tmp_queue.dequeue()
        assert t is not None
        assert t["status"] == "running"
        assert t["agent"] == "builder"

    def test_dequeue_priority(self, tmp_queue):
        tmp_queue.submit("builder", "low", priority=0)
        tmp_queue.submit("builder", "high", priority=2)
        t = tmp_queue.dequeue()
        assert t["operation"] == "high"

    def test_dequeue_by_agent(self, tmp_queue):
        tmp_queue.submit("builder", "code", priority=0)
        tmp_queue.submit("auditor", "audit", priority=1)
        t = tmp_queue.dequeue(agent="auditor")
        assert t["agent"] == "auditor"
        assert t["operation"] == "audit"

    def test_complete(self, tmp_queue):
        s = tmp_queue.submit("builder", "test")
        tmp_queue.complete(s["id"], {"status": "ok"})
        t = tmp_queue.status(s["id"])
        assert t["status"] == "completed"
        assert t["result"]["status"] == "ok"

    def test_fail_and_retry(self, tmp_queue):
        s = tmp_queue.submit("builder", "test", max_retries=1)
        tmp_queue.fail(s["id"], "error occurred", retry=True)
        t = tmp_queue.status(s["id"])
        assert t["status"] == "queued"
        assert t["retries"] == 1

    def test_fail_exhaust_retries(self, tmp_queue):
        s = tmp_queue.submit("builder", "test", max_retries=0)
        tmp_queue.fail(s["id"], "fatal", retry=True)
        t = tmp_queue.status(s["id"])
        assert t["status"] == "failed"

    def test_cancel(self, tmp_queue):
        s = tmp_queue.submit("builder", "test")
        tmp_queue.cancel(s["id"])
        t = tmp_queue.status(s["id"])
        assert t["status"] == "cancelled"

    def test_status_not_found(self, tmp_queue):
        t = tmp_queue.status("nonexistent")
        assert t is None

    def test_list_tasks(self, tmp_queue):
        tmp_queue.submit("builder", "a")
        tmp_queue.submit("auditor", "b")
        tasks = tmp_queue.list_tasks()
        assert len(tasks) == 2

    def test_list_tasks_filter_status(self, tmp_queue):
        s = tmp_queue.submit("builder", "a")
        tmp_queue.complete(s["id"])
        tasks = tmp_queue.list_tasks(status="completed")
        assert len(tasks) == 1
        tasks2 = tmp_queue.list_tasks(status="queued")
        assert len(tasks2) == 0

    def test_list_tasks_filter_agent(self, tmp_queue):
        tmp_queue.submit("builder", "a")
        tmp_queue.submit("auditor", "b")
        tasks = tmp_queue.list_tasks(agent="builder")
        assert len(tasks) == 1
        assert tasks[0]["agent"] == "builder"

    def test_stats(self, tmp_queue):
        tmp_queue.submit("builder", "a")
        s = tmp_queue.submit("auditor", "b")
        tmp_queue.complete(s["id"])
        stats = tmp_queue.stats()
        assert stats["total"] == 2
        assert stats["queued"] == 1
        assert stats["completed"] == 1

    def test_checkpoint(self, tmp_queue):
        s = tmp_queue.submit("builder", "long_task")
        tmp_queue.save_checkpoint(s["id"], {"progress": 50, "data": "partial"})
        cp = tmp_queue.get_checkpoint(s["id"])
        assert cp["progress"] == 50
        assert cp["data"] == "partial"

    def test_clean_old(self, tmp_queue):
        s = tmp_queue.submit("builder", "old_task")
        tmp_queue.complete(s["id"])
        from datetime import datetime, timedelta
        import time
        time.sleep(0.1)
        tmp_queue.clean_old(hours=0)
        tasks = tmp_queue.list_tasks()
        assert len(tasks) == 0

    def test_priority_ordering(self, tmp_queue):
        tmp_queue.submit("builder", "low", priority=0)
        tmp_queue.submit("builder", "medium", priority=1)
        tmp_queue.submit("builder", "high", priority=2)
        t1 = tmp_queue.dequeue()
        assert t1["operation"] == "high"
        t2 = tmp_queue.dequeue()
        assert t2["operation"] == "medium"
        t3 = tmp_queue.dequeue()
        assert t3["operation"] == "low"

    def test_submit_with_params(self, tmp_queue):
        params = {"file": "test.py", "mode": "create"}
        s = tmp_queue.submit("builder", "write.code", params=params)
        t = tmp_queue.status(s["id"])
        assert t["params"]["file"] == "test.py"
        assert t["params"]["mode"] == "create"

    def test_multiple_agents_queue(self, tmp_queue):
        tmp_queue.submit("mystic", "plan")
        tmp_queue.submit("builder", "code")
        tmp_queue.submit("auditor", "review")
        tasks = tmp_queue.list_tasks()
        assert len(tasks) == 3
        agents = {t["agent"] for t in tasks}
        assert agents == {"mystic", "builder", "auditor"}


class TestCheckpoint:
    def test_checkpoint_manager(self, tmp_path):
        from apps.decide.execution.checkpoint import CheckpointManager
        cm = CheckpointManager(TaskQueue(db_path=tmp_path / "queue.db"))
        task = cm.queue.submit("builder", "task")
        cm.save(task["id"], {"step": 1, "data": "hello"})
        loaded = cm.load(task["id"])
        assert loaded["step"] == 1
        resumed = cm.resume(task["id"])
        assert resumed["_resumed"] is True
        cm.delete(task["id"])
        assert cm.load(task["id"]) is None


class TestCLI:
    def test_submit_via_cli(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, "scripts/execution.py", "submit",
             "--agent", "builder", "--operation", "write.code",
             "--params", '{"file":"test.py"}'],
            capture_output=True, text=True, timeout=10,
            cwd=str(REPO)
        )
        data = json.loads(result.stdout)
        assert data["status"] == "queued"
        assert data["agent"] == "builder"

    def test_stats_via_cli(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, "scripts/execution.py", "stats"],
            capture_output=True, text=True, timeout=10,
            cwd=str(REPO)
        )
        data = json.loads(result.stdout)
        assert "total" in data
        assert "by_status" in data

    def test_list_via_cli(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, "scripts/execution.py", "list", "--limit", "5"],
            capture_output=True, text=True, timeout=10,
            cwd=str(REPO)
        )
        data = json.loads(result.stdout)
        assert isinstance(data, list)


class TestAgentExecutor:
    def test_default_execute(self):
        from apps.decide.execution.executor import AgentExecutor
        import asyncio
        ex = AgentExecutor()
        result = asyncio.run(ex.execute("unknown", "do.stuff", {}))
        assert result["status"] == "simulated"
        assert result["note"].startswith("Agent unknown")

    def test_default_execute_simulated(self):
        from apps.decide.execution.executor import AgentExecutor
        import asyncio
        ex = AgentExecutor()
        result = asyncio.run(ex.execute("unknown_agent", "plan", {}))
        assert result["status"] == "simulated"
