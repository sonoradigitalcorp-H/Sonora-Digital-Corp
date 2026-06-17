"""
Tests para src/core/llm.py — con mocks (no requiere API real).
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest


class TestLLM:
    def test_ask_returns_content(self):
        with patch("src.core.llm.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "Hello!"}}],
                "usage": {"total_tokens": 10},
                "model": "test-model",
            }
            mock_resp.status_code = 200
            mock_post.return_value = mock_resp

            from src.core.llm import ask
            result = ask("Hi")
            assert "Hello" in result

    def test_ask_returns_empty_on_error(self):
        with patch("src.core.llm.requests.post") as mock_post:
            from requests.exceptions import ConnectionError
            mock_post.side_effect = ConnectionError("API down")

            from src.core.llm import ask
            result = ask("Hi")
            assert result == ""

    def test_list_models_returns_list(self):
        from src.core.llm import list_models
        models = list_models()
        assert len(models) >= 2
        assert any(m["provider"] == "opencode-go" for m in models)
        assert any(m["provider"] == "openrouter" for m in models)

    def test_chat_completion_timeout(self):
        with patch("src.core.llm.requests.post") as mock_post:
            from requests.exceptions import Timeout
            mock_post.side_effect = Timeout("timeout")

            from src.core.llm import chat_completion
            result = chat_completion([{"role": "user", "content": "hi"}])
            assert "error" in result
            assert "Timeout" in result["error"]
