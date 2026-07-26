"""Tests for analyze-artist handler"""
import importlib.util
import pytest
from pathlib import Path


SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"


def _load_handler():
    path = SKILLS_DIR / "handler.py"
    spec = importlib.util.spec_from_file_location("analyze_artist_handler", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.asyncio
async def test_analyze_unknown_artist():
    handler = _load_handler()
    result = await handler.run("nonexistent-id")
    assert result["status"] == "error"


@pytest.mark.asyncio
async def test_momentum_calculation():
    handler = _load_handler()
    assert handler._calc_momentum({"streams": 100_000_000, "followers": 50_000, "revenue": 50_000}) >= 30
    assert handler._calc_momentum({}) == 0


def test_detect_platforms():
    handler = _load_handler()
    platforms = handler._detect_platforms({"spotify_monthly_listeners": 1000, "instagram_followers": 500})
    assert "spotify" in platforms
    assert "instagram" in platforms
    assert "youtube" not in platforms
