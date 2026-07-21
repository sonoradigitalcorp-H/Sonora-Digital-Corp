"""Integration tests for generate-video capability.
Tests against real ComfyUI instance.
"""
import urllib.request
import json
import pytest

from .conftest import require_comfyui

COMFYUI_URL = "http://localhost:8188"


@require_comfyui
def test_comfyui_connection():
    """Verify ComfyUI is reachable."""
    with urllib.request.urlopen(f"{COMFYUI_URL}/object_info", timeout=5) as resp:
        data = json.loads(resp.read().decode())
        assert isinstance(data, dict)
        assert len(data) > 0


@require_comfyui
def test_comfyui_has_samplers():
    """Verify ComfyUI has expected node types loaded."""
    with urllib.request.urlopen(f"{COMFYUI_URL}/object_info", timeout=5) as resp:
        data = json.loads(resp.read().decode())
    required_nodes = ["KSampler", "VAEDecode", "VAEEncode", "CLIPTextEncode", "EmptyLatentImage"]
    for node in required_nodes:
        assert node in data, f"Missing required node: {node}"


@require_comfyui
def test_comfyui_queue_empty():
    """Verify ComfyUI queue is in valid state."""
    with urllib.request.urlopen(f"{COMFYUI_URL}/queue", timeout=5) as resp:
        data = json.loads(resp.read().decode())
    assert "queue_running" in data
    assert "queue_pending" in data
