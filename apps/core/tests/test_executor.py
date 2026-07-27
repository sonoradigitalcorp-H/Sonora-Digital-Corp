"""Tests for Executor (HAS-004)"""
import pytest
from kernel.executor import Executor
from kernel.models import KernelTask


@pytest.mark.asyncio
async def test_execute_task():
    executor = Executor()
    task = KernelTask(id="t1", mission="test", description="test", capability="sync-artist-data")
    result = await executor.execute(task, "builder")
    assert result.status == "success"
    assert result.duration_ms >= 0


@pytest.mark.asyncio
async def test_execution_log():
    executor = Executor()
    task = KernelTask(id="t2", mission="test2", description="test2")
    await executor.execute(task, "mystic")
    stats = executor.get_stats()
    assert stats["total"] == 1
    assert stats["succeeded"] == 1
