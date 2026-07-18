#!/usr/bin/env python3
"""Instrumentacion LangFuse para JARVIS y agentes SDC.
Agrega tracing a cualquier agente con 1 decorador.

Requiere: pip install langfuse

Uso:
    from instrument_langfuse import observe_agent

    @observe_agent(name="jarvis", tenant="sdc-core")
    def mi_agente(pregunta: str) -> str:
        ...
"""

import os
from collections.abc import Callable
from functools import wraps

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "pk-lf-sdc-2026")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "sk-lf-sdc-2026-secret")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:3000")

_use_sdk = False
_langfuse = None

try:
    from langfuse import Langfuse
    _langfuse = Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_HOST
    )
    _use_sdk = True
except ImportError:
    pass


class LangFuseTracker:
    """Tracker via REST API de LangFuse (fallback sin SDK)."""

    def __init__(self):
        self.public_key = LANGFUSE_PUBLIC_KEY
        self.base_url = LANGFUSE_HOST

    def trace(self, name: str, input: dict, output: dict = None,
              tenant: str = "sdc-core", agent: str = "generic",
              duration_ms: float = 0, cost_usd: float = 0,
              metadata: dict = None, status: str = "success"):
        import requests
        payload = {
            "name": name,
            "input": input,
            "output": output or {},
            "metadata": {
                "tenant": tenant,
                "agent": agent,
                "duration_ms": duration_ms,
                "cost_usd": cost_usd,
                "status": status,
                **(metadata or {})
            },
            "tags": [tenant, agent]
        }
        try:
            resp = requests.post(
                f"{self.base_url}/api/public/traces",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.public_key}",
                    "Content-Type": "application/json"
                },
                timeout=5
            )
            return resp.ok
        except Exception as e:
            print(f"[LangFuse] Error: {e}")
            return False


_tracker = LangFuseTracker()


def observe_agent(name: str = "agent", tenant: str = "sdc-core"):
    """Decorador que traza cada llamada del agente en LangFuse."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start = time.time()
            input_data = {
                "args": [str(a)[:500] for a in args if not callable(a)],
                "kwargs": {k: str(v)[:500] for k, v in kwargs.items() if not callable(v)}
            }
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start) * 1000
                if _use_sdk and _langfuse:
                    _langfuse.trace(
                        name=name,
                        input=input_data,
                        output={"result": str(result)[:1000]},
                        metadata={"tenant": tenant, "agent": name}
                    )
                else:
                    _tracker.trace(name=name, input=input_data,
                                   output={"result": str(result)[:1000]},
                                   tenant=tenant, agent=name,
                                   duration_ms=duration)
                return result
            except Exception as e:
                duration = (time.time() - start) * 1000
                _tracker.trace(name=name, input=input_data,
                               output={"error": str(e)},
                               tenant=tenant, agent=name,
                               duration_ms=duration,
                               status="error")
                raise
        return wrapper
    return decorator
