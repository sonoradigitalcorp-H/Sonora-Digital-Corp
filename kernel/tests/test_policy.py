"""Tests for PolicyEngine (HAS-004)"""
import pytest
from kernel.policy import PolicyEngine
from kernel.models import KernelTask


@pytest.mark.asyncio
async def test_all_gates_pass():
    engine = PolicyEngine()
    task = KernelTask(id="t1", mission="test", description="test", priority=1, estimated_cost=0.5)
    results = await engine.validate(task)
    assert engine.all_passed(results)


@pytest.mark.asyncio
async def test_cost_gate_fails():
    engine = PolicyEngine({"max_cost_per_task": 0.1})
    task = KernelTask(id="t1", mission="test", description="test", estimated_cost=1.0)
    results = await engine.validate(task)
    passed = [r for r in results if r.passed]
    assert len(passed) < len(results)
    assert results[2].gate == "cost"
    assert not results[2].passed
