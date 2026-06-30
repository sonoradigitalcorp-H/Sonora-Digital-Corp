"""
Redis Streams — Sistema nervioso para comunicación entre agentes.
XADD para publicar, XREVRANGE/XREAD para consumir.
Fallback degradado si Redis no está disponible.
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Optional

log = logging.getLogger("jarvis.redis_streams")

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
EVENTS_FILE = os.path.join(BASE_DIR, "state", "logs", "events.jsonl")

_client = None
_fallback = False


def get_redis():
    global _client, _fallback
    if _fallback:
        return None
    if _client is not None:
        return _client
    try:
        import redis
        _client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD or None,
            socket_connect_timeout=2,
            socket_timeout=2,
            decode_responses=True,
        )
        _client.ping()
        log.info(f"Redis connected: {REDIS_HOST}:{REDIS_PORT}")
        return _client
    except redis.AuthenticationError:
        log.warning("Redis auth failed, trying without password")
        try:
            _client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                socket_connect_timeout=2,
                socket_timeout=2,
                decode_responses=True,
            )
            _client.ping()
            log.info(f"Redis connected (no auth): {REDIS_HOST}:{REDIS_PORT}")
            return _client
        except Exception:
            _fallback = True
            return None
    except ImportError:
        log.warning("redis-py not installed, Redis streams disabled")
        _fallback = True
        return None
    except Exception as e:
        log.warning(f"Redis unavailable ({e}), falling back to local storage")
        _fallback = True
        return None


def stream_push(stream: str, data: dict, maxlen: int = 1000) -> Optional[str]:
    """Push an entry to a Redis Stream. Returns entry ID or None."""
    client = get_redis()
    if client is None:
        return None
    try:
        return client.xadd(stream, data, maxlen=maxlen, approximate=True)
    except Exception as e:
        log.warning(f"Redis XADD {stream} failed: {e}")
        return None


def stream_read(stream: str, count: int = 10, reverse: bool = True) -> list[dict]:
    """Read entries from a Redis Stream.
    If reverse=True, returns most recent first (XREVRANGE).
    If reverse=False, returns oldest first (XRANGE).
    """
    client = get_redis()
    if client is None:
        return []
    try:
        if reverse:
            results = client.xrevrange(stream, max="+", min="-", count=count)
        else:
            results = client.xrange(stream, min="-", max="+", count=count)
        entries = []
        for entry_id, fields in results:
            entry = {"id": entry_id, **fields}
            entries.append(entry)
        return entries
    except Exception as e:
        log.warning(f"Redis XREVRANGE {stream} failed: {e}")
        return []


def stream_len(stream: str) -> int:
    """Get the length of a Redis Stream."""
    client = get_redis()
    if client is None:
        return 0
    try:
        return client.xlen(stream)
    except Exception:
        return 0


def emit_event(event: str, payload: dict, stream: str = "events:pipeline"):
    """Publish an event to Redis Stream + events.jsonl simultaneously."""
    ts = datetime.now(timezone.utc).isoformat()
    entry = json.dumps({"event": event, "timestamp": ts, "payload": payload})

    # Always write to events.jsonl (backward compat)
    try:
        os.makedirs(os.path.dirname(EVENTS_FILE), exist_ok=True)
        with open(EVENTS_FILE, "a") as f:
            f.write(entry + "\n")
    except OSError:
        pass

    # Also push to Redis Stream
    client = get_redis()
    if client is not None:
        try:
            client.xadd(stream, {
                "event": event,
                "timestamp": ts,
                "payload": json.dumps(payload),
            }, maxlen=1000, approximate=True)
        except Exception:
            pass


def push_agent_context(agent: str, task: str, result_summary: str) -> None:
    """Push an agent interaction to the context:history stream."""
    client = get_redis()
    if client is None:
        return
    try:
        client.xadd("context:history", {
            "agent": agent,
            "task": task[:500],
            "result_summary": str(result_summary)[:500],
            "timestamp": str(time.time()),
        }, maxlen=1000, approximate=True)
    except Exception:
        pass


def read_agent_context(count: int = 10) -> list[dict]:
    """Read recent agent context from the context:history stream."""
    return stream_read("context:history", count=count, reverse=True)


def clear_context() -> None:
    """Delete the context:history stream."""
    client = get_redis()
    if client is None:
        return
    try:
        client.delete("context:history")
    except Exception:
        pass
