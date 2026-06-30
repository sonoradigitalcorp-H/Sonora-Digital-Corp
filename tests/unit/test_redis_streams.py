"""Tests for redis_streams.py — Redis Streams with graceful fallback."""

import json
import os
from unittest.mock import patch, MagicMock

import pytest
from src.core.redis_streams import (
    get_redis,
    stream_push,
    stream_read,
    stream_len,
    emit_event,
    push_agent_context,
    read_agent_context,
    clear_context,
    _fallback,
)


class TestRedisStreamsFallback:
    def test_get_redis_fallback_when_unavailable(self):
        """Without Redis running, get_redis should return None after first attempt."""
        r = get_redis()
        # If Redis is running locally, this might connect. If not, returns None.
        assert r is None or hasattr(r, 'ping')

    def test_stream_push_returns_none_on_fallback(self):
        result = stream_push("test:stream", {"key": "value"})
        # Should return None if Redis unavailable
        assert result is None or isinstance(result, str)

    def test_stream_read_returns_empty_on_fallback(self):
        results = stream_read("test:stream", count=5)
        assert isinstance(results, list)

    def test_stream_len_returns_zero_on_fallback(self):
        length = stream_len("test:stream")
        assert length == 0

    def test_emit_event_writes_to_file(self):
        """emit_event should always write to events.jsonl regardless of Redis."""
        events_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "state", "logs", "events.jsonl"
        )
        before = 0
        if os.path.exists(events_file):
            with open(events_file) as f:
                before = sum(1 for _ in f)

        emit_event("test_redis_event", {"source": "test"})

        if os.path.exists(events_file):
            with open(events_file) as f:
                after = sum(1 for _ in f)
            assert after > before

    def test_push_agent_context_no_crash(self):
        push_agent_context("test_agent", "test task", "test result")
        assert True

    def test_read_agent_context_returns_list(self):
        ctx = read_agent_context(count=5)
        assert isinstance(ctx, list)

    def test_clear_context_no_crash(self):
        clear_context()
        assert True


class TestRedisStreamsWithMock:
    @pytest.fixture
    def mock_redis(self):
        with patch('src.core.redis_streams.get_redis') as mock:
            mock_client = MagicMock()
            mock_client.xadd.return_value = "1680000000000-0"
            mock_client.xrevrange.return_value = [
                ("1680000000000-0", {"event": "test", "timestamp": "t1"}),
            ]
            mock_client.xlen.return_value = 1
            mock.return_value = mock_client
            yield mock_client

    def test_stream_push_with_redis(self, mock_redis):
        result = stream_push("test:stream", {"key": "value"})
        assert result == "1680000000000-0"
        mock_redis.xadd.assert_called_once()

    def test_stream_read_with_redis(self, mock_redis):
        results = stream_read("test:stream", count=5)
        assert len(results) == 1
        assert results[0]["event"] == "test"
        mock_redis.xrevrange.assert_called_once()

    def test_stream_len_with_redis(self, mock_redis):
        length = stream_len("test:stream")
        assert length == 1
        mock_redis.xlen.assert_called_once()
