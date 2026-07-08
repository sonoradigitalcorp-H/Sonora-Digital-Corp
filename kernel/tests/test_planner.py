"""Tests for Planner (HAS-004)"""
import pytest
from kernel.planner import Planner
from kernel.models import HermesContext


@pytest.mark.asyncio
async def test_direct_sync():
    planner = Planner()
    ctx = HermesContext(input="sync artists data", channel="api")
    tasks = await planner.plan(ctx)
    assert len(tasks) >= 1
    assert tasks[0].capability == "sync-artist-data"


@pytest.mark.asyncio
async def test_research_strategy():
    planner = Planner()
    ctx = HermesContext(input="research the latest trends", channel="api")
    tasks = await planner.plan(ctx)
    assert tasks[0].agent == "researcher"


@pytest.mark.asyncio
async def test_emergency_strategy():
    planner = Planner()
    ctx = HermesContext(input="emergency fix the pipeline", channel="api")
    tasks = await planner.plan(ctx)
    assert tasks[0].priority == 2
