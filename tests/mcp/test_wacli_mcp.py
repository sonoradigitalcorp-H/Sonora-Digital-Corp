"""Tests for mcp/servers/wacli_mcp.py"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from mcp.servers import wacli_mcp as mcp

# ─── Helpers ─────────────────────────────────────────────────────────

def _mock_wacli(result: dict):
    return patch.object(mcp, "_wacli", return_value=result)


def _mock_emit():
    return patch.object(mcp, "_emit_event")


# ─── _ensure_to ──────────────────────────────────────────────────────

@pytest.mark.parametrize("raw,expected", [
    ("5216622681111", "5216622681111@s.whatsapp.net"),
    ("5216622681111@s.whatsapp.net", "5216622681111@s.whatsapp.net"),
    ("6622681111", "5216622681111@s.whatsapp.net"),
    ("6622681111", "5216622681111@s.whatsapp.net"),
    ("526622681111", "5216622681111@s.whatsapp.net"),
    ("1234567890", "11234567890@s.whatsapp.net"),
])
def test_ensure_to(raw, expected):
    assert mcp._ensure_to(raw) == expected


# ─── Status ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_check_status_authenticated():
    with _mock_wacli({"success": True, "data": {"authenticated": True, "phone": "5216623538272"}}):
        result = await mcp.whatsapp_check_status()
    data = json.loads(result)
    assert data["status"] == "authenticated"
    assert data["phone"] == "5216623538272"


@pytest.mark.asyncio
async def test_check_status_unauthenticated():
    with _mock_wacli({"success": False, "error": "not logged in"}):
        result = await mcp.whatsapp_check_status()
    data = json.loads(result)
    assert data["status"] == "unauthenticated"
    assert "not logged in" in data["detail"]


# ─── Send text ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_text_success():
    with _mock_wacli({"success": True, "data": {"sent": True, "id": "MSG123"}}), _mock_emit():
        result = await mcp.whatsapp_send_text("6622681111", "Hola")
    data = json.loads(result)
    assert data["sent"] is True
    assert data["id"] == "MSG123"
    assert data["to"] == "5216622681111@s.whatsapp.net"


@pytest.mark.asyncio
async def test_send_text_failure():
    with _mock_wacli({"success": False, "error": "timeout"}), _mock_emit():
        result = await mcp.whatsapp_send_text("6622681111", "Hola")
    data = json.loads(result)
    assert data["sent"] is False
    assert data["error"] == "timeout"


# ─── Send file ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_file_missing():
    with _mock_emit():
        result = await mcp.whatsapp_send_file("6622681111", "/tmp/noexiste.pdf")
    data = json.loads(result)
    assert data["sent"] is False
    assert "file not found" in data["error"]


@pytest.mark.asyncio
async def test_send_file_success(tmp_path):
    file_path = tmp_path / "doc.pdf"
    file_path.write_text("fake")
    with _mock_wacli({"success": True, "data": {"sent": True, "id": "FILE123"}}), _mock_emit():
        result = await mcp.whatsapp_send_file("6622681111", str(file_path), "caption")
    data = json.loads(result)
    assert data["sent"] is True
    assert data["id"] == "FILE123"


# ─── wa.me link ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_wa_me_link():
    with _mock_emit():
        result = await mcp.whatsapp_create_wa_me_link(ref_code="REF-ABC123")
    data = json.loads(result)
    assert data["link"] == "https://wa.me/5216623538272?text=REF-ABC123"
    assert data["ref_code"] == "REF-ABC123"


@pytest.mark.asyncio
async def test_create_wa_me_link_with_text_and_ref():
    with _mock_emit():
        result = await mcp.whatsapp_create_wa_me_link(text="Hola", ref_code="REF-ABC123")
    data = json.loads(result)
    assert "wa.me/5216623538272" in data["link"]
    assert "REF-ABC123" in data["link"]
    assert "Hola" in data["link"]


# ─── QR ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_qr(tmp_path):
    output = tmp_path / "qr.png"
    with _mock_emit():
        result = await mcp.whatsapp_create_qr(ref_code="REF-ABC123", output_path=str(output))
    data = json.loads(result)
    assert data["created"] is True
    assert output.exists()


@pytest.mark.asyncio
async def test_create_qr_default_data(tmp_path):
    with _mock_emit():
        result = await mcp.whatsapp_create_qr()
    data = json.loads(result)
    assert data["created"] is True
    assert data["data"].startswith("https://wa.me/5216623538272")


@pytest.mark.asyncio
async def test_read_qr_valid(tmp_path):
    # Create a QR first
    output = tmp_path / "qr.png"
    decoded = MagicMock()
    decoded.data = b"REF-ABC123"
    with _mock_emit(), patch.dict("sys.modules", {"pyzbar": MagicMock(), "pyzbar.pyzbar": MagicMock()}):
        import pyzbar.pyzbar as pyzbar_mod
        pyzbar_mod.decode = MagicMock(return_value=[decoded])
        await mcp.whatsapp_create_qr(data="REF-ABC123", output_path=str(output))
        result = await mcp.whatsapp_read_qr(str(output))
    data = json.loads(result)
    assert data["valid"] is True
    assert data["data"] == "REF-ABC123"


@pytest.mark.asyncio
async def test_read_qr_invalid(tmp_path):
    # Create a non-QR image
    from PIL import Image
    img = Image.new("RGB", (100, 100), "white")
    output = tmp_path / "not-qr.png"
    img.save(output)
    with _mock_emit():
        result = await mcp.whatsapp_read_qr(str(output))
    data = json.loads(result)
    assert data["valid"] is False


# ─── Audio thumbnail ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_audio_thumbnail(tmp_path):
    audio = tmp_path / "audio.mp3"
    audio.write_bytes(b"fake audio data")
    with _mock_wacli({"success": True, "data": {"sent": True, "id": "THUMB123"}}), _mock_emit():
        result = await mcp.whatsapp_send_audio_thumbnail("6622681111", str(audio))
    data = json.loads(result)
    assert data["sent"] is True
    assert data["thumbnail_type"] == "audio_waveform"


@pytest.mark.asyncio
async def test_send_audio_thumbnail_missing():
    with _mock_emit():
        result = await mcp.whatsapp_send_audio_thumbnail("6622681111", "/tmp/noexiste.mp3")
    data = json.loads(result)
    assert data["sent"] is False
    assert "file not found" in data["error"]


# ─── Contacts ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_contacts():
    with _mock_wacli({"success": True, "data": [{"name": "Luis", "phone": "5216622681111"}]}), _mock_emit():
        result = await mcp.whatsapp_get_contacts()
    data = json.loads(result)
    assert data["count"] == 1
    assert data["contacts"][0]["name"] == "Luis"


@pytest.mark.asyncio
async def test_get_contacts_fallback():
    with _mock_wacli({"success": False, "error": "not supported"}), _mock_emit():
        result = await mcp.whatsapp_get_contacts()
    data = json.loads(result)
    assert data["count"] == 0
    assert "not supported" in data["note"]


# ─── Tools registry ───────────────────────────────────────────────────

def test_tools_registry_count():
    assert len(mcp.TOOLS) == 9


def test_tools_have_required_fields():
    for name, tool in mcp.TOOLS.items():
        assert tool["name"] == name
        assert tool["description"]
        assert tool["inputSchema"]
        assert callable(tool["handler"])


# ─── Events file ───────────────────────────────────────────────────────

def test_emit_event_creates_file(tmp_path, monkeypatch):
    events_path = tmp_path / "events.jsonl"
    monkeypatch.setattr(mcp, "EVENTS_PATH", events_path)
    mcp._emit_event("test:event", {"foo": "bar"})
    assert events_path.exists()
    entry = json.loads(events_path.read_text().strip())
    assert entry["event"] == "test:event"
    assert entry["payload"]["foo"] == "bar"
