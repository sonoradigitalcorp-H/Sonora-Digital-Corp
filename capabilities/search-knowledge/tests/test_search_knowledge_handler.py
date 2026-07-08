"""Tests for search-knowledge handler"""
import importlib.util
import pytest
from pathlib import Path


SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"


def _load_handler():
    path = SKILLS_DIR / "handler.py"
    spec = importlib.util.spec_from_file_location("search_knowledge_handler", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.asyncio
async def test_search_returns_structure():
    handler = _load_handler()
    result = await handler.run("test")
    assert result["status"] == "success"
    assert "stores_searched" in result


@pytest.mark.asyncio
async def test_search_long_store():
    handler = _load_handler()
    result = await handler.run("test", stores=["long"])
    assert "long" in result["results"]
