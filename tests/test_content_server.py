"""Tests for content-server MCP tools."""
import sys
import os
import ast
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SERVER_PATH = BASE / "products" / "content-studio" / "server.py"
SRC = SERVER_PATH.read_text()

os.environ["FAL_KEY"] = "test-fal-key"
os.environ["CONTENT_DB_DSN"] = "postgresql://test:test@localhost:5432/test"
os.environ["STORAGE_BASE"] = "/tmp/test-content-storage"


def _get_func(name: str) -> ast.AsyncFunctionDef:
    tree = ast.parse(SRC)
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"Function '{name}' not found")


def test_tools_declared():
    import re
    tools = re.findall(r'@mcp\.tool\(\)\s*\n\s*(?:async )?def (\w+)', SRC)
    assert len(tools) >= 20, f"Expected >=20 tools, got {len(tools)}: {tools}"
    assert "register_lora_weights" in tools
    assert "edit_image" in tools
    assert "clone_voice" in tools
    assert "ocr_image" in tools


def test_register_lora_weights_params():
    func = _get_func("register_lora_weights")
    args = [a.arg for a in func.args.args]
    assert "artist_id" in args
    assert "path" in args
    assert "scale" in args


def test_list_lora_weights_params():
    func = _get_func("list_lora_weights")
    args = [a.arg for a in func.args.args]
    assert "artist_id" in args


def test_delete_lora_weights_exists():
    import re
    assert re.search(r'async def delete_lora_weights', SRC)


def test_edit_image_params():
    func = _get_func("edit_image")
    args = [a.arg for a in func.args.args]
    assert "image_url" in args
    assert "prompt" in args
    assert "mask_url" in args


def test_clone_voice_params():
    func = _get_func("clone_voice")
    args = [a.arg for a in func.args.args]
    assert "audio_urls" in args
    assert "artist_id" in args


def test_ocr_image_params():
    func = _get_func("ocr_image")
    args = [a.arg for a in func.args.args]
    assert "image_url" in args
    assert "language" in args


def test_webhook_tools_exist():
    import re
    assert re.search(r'async def register_webhook', SRC)
    assert re.search(r'async def list_webhooks', SRC)
    assert re.search(r'async def delete_webhook', SRC)


def test_queue_content_params():
    func = _get_func("queue_content")
    args = [a.arg for a in func.args.args]
    assert "artist_id" in args
    assert "prompt" in args
    assert "media_type" in args


def test_omnivoice_integration():
    assert "OMNIVOICE_URL" in SRC
    assert "/profiles" in SRC
