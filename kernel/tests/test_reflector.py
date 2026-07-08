"""Tests for Reflector (HAS-004)"""
import pytest
from kernel.reflector import Reflector
from kernel.models import ExecutionResult, KernelTask


@pytest.mark.asyncio
async def test_successful_task_high_score():
    reflector = Reflector()
    task = KernelTask(id="t1", mission="test", description="test")
    result = ExecutionResult(task_id="t1", status="success", duration_ms=500)
    reflection = await reflector.reflect(task, result)
    assert reflection["score"] >= 70


@pytest.mark.asyncio
async def test_failed_task_low_score():
    reflector = Reflector()
    task = KernelTask(id="t2", mission="test", description="test")
    result = ExecutionResult(task_id="t2", status="failure", error="connection lost")
    reflection = await reflector.reflect(task, result)
    assert reflection["score"] < 50
