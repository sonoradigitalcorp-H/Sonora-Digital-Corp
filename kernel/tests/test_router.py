"""Tests for AgentRouter (HAS-004)"""
from kernel.router import AgentRouter
from kernel.models import KernelTask


def test_routes_to_mystic_by_default():
    router = AgentRouter()
    task = KernelTask(id="t1", mission="test", description="test")
    agent = router.route(task)
    assert agent is not None


def test_available_capability():
    router = AgentRouter()
    available = router.available("run.tests")
    assert len(available) > 0
