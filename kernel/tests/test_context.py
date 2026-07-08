"""Tests for ContextEngine (HAS-004)"""
import pytest
from kernel.context import ContextEngine


@pytest.mark.asyncio
async def test_build_context():
    engine = ContextEngine()
    ctx = await engine.build({"input": "hello", "channel": "api", "tenant": "test"})
    assert ctx.input == "hello"
    assert ctx.channel == "api"
    assert ctx.tenant == "test"


@pytest.mark.asyncio
async def test_loads_constitution():
    engine = ContextEngine()
    ctx = await engine.build({"input": "test"})
    assert len(ctx.constitution_rules) > 0


def test_session_store():
    engine = ContextEngine()
    engine.append_session("conv-1", {"role": "user", "content": "hello"})
    assert len(engine._get_session("conv-1")) == 1
