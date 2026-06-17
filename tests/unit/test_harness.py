"""
Tests para src/core/harness.py — SDD pipeline executor.
"""
import sys, asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from src.core.harness import Harness


class TestHarness:

    @pytest.mark.asyncio
    async def test_execute_returns_dict(self):
        h = Harness()
        result = await h.execute("test task")
        assert isinstance(result, dict)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_execute_with_context(self):
        h = Harness()
        result = await h.execute("test", {"user": "test-user"})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_execute_preserves_history(self):
        h = Harness()
        await h.execute("task 1")
        await h.execute("task 2")
        assert len(h._history) >= 1

    @pytest.mark.asyncio
    async def test_execute_multiple_times(self):
        h = Harness()
        for i in range(3):
            result = await h.execute(f"task {i}")
            assert isinstance(result, dict)
