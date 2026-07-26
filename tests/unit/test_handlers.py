"""Tests for all capability handlers (HAS-005)"""
import importlib.util
import shutil
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent


def _load_handler(cap_id: str):
    handler_path = REPO / "capabilities" / cap_id / "skills" / "handler.py"
    if not handler_path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"test_{cap_id}", handler_path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.asyncio
async def test_score_artist():
    mod = _load_handler("score-artist")
    result = await mod.execute({
        "artist_id": "test-001",
        "artist_name": "Test Artist",
        "streams": 1000000,
        "monthly_listeners": 50000,
        "revenue": 50000,
        "social_followers": 25000,
        "engagement_rate": 0.05,
        "playlist_adds": 5000,
        "trend_growth": 0.15,
    })
    assert result["artist_id"] == "test-001"
    assert "overall" in result
    assert 0 <= result["overall"] <= 100


@pytest.mark.asyncio
async def test_score_artist_low_scores():
    mod = _load_handler("score-artist")
    result = await mod.execute({
        "artist_id": "low", "streams": 0, "monthly_listeners": 0,
        "revenue": 0, "social_followers": 0, "engagement_rate": 0,
    })
    assert result["overall"] < 30


@pytest.mark.asyncio
async def test_manage_crm_add_contact():
    mod = _load_handler("manage-crm")
    result = await mod.execute({"action": "add_contact", "name": "John", "email": "john@test.com"})
    assert result["action"] == "add_contact"
    assert "contact" in result


@pytest.mark.asyncio
async def test_manage_crm_add_lead():
    mod = _load_handler("manage-crm")
    result = await mod.execute({"action": "add_lead", "name": "Lead", "artist_name": "Artist"})
    assert result["action"] == "add_lead"
    assert "lead" in result


@pytest.mark.asyncio
async def test_manage_crm_update_lead():
    mod = _load_handler("manage-crm")
    result = await mod.execute({"action": "update_lead", "lead_id": "nonexistent"})
    assert "error" in result


@pytest.mark.asyncio
async def test_manage_crm_list():
    mod = _load_handler("manage-crm")
    result = await mod.execute({"action": "list_contacts"})
    assert result["action"] == "list_contacts"


@pytest.mark.asyncio
async def test_publish_track():
    mod = _load_handler("publish-track")
    result = await mod.execute({"title": "Test Track", "artist_name": "Test", "platforms": ["spotify"]})
    assert result["status"] == "completed"
    assert result["title"] == "Test Track"


@pytest.mark.asyncio
async def test_process_payment_charge():
    mod = _load_handler("process-payment")
    result = await mod.execute({"action": "charge", "amount": 100, "description": "Test"})
    assert result["status"] == "succeeded"
    assert result["amount"] == 100


@pytest.mark.asyncio
async def test_process_payment_refund():
    mod = _load_handler("process-payment")
    result = await mod.execute({"action": "refund", "charge_id": "ch_test", "amount": 50})
    assert result["status"] == "refunded"


@pytest.mark.asyncio
async def test_process_payment_payout():
    mod = _load_handler("process-payment")
    result = await mod.execute({"action": "payout", "amount": 1000})
    assert result["status"] == "pending"


@pytest.mark.asyncio
async def test_generate_video():
    mod = _load_handler("generate-video")
    result = await mod.execute({"artist_name": "Test", "type": "lipsync", "duration_seconds": 10})
    assert result["video_id"] is not None
    assert result["type"] == "lipsync"
