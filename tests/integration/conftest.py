"""Integration test configuration.
Tests connect to real running services on localhost.
Skip if required services are not available.
"""
import urllib.request
import pytest

# Ignore legacy broken integration test files
collect_ignore_glob = [
    "test_api_stability.py",
    "test_api_status.py",
    "test_api_voice.py",
    "test_unification_e2e.py",
]


def service_reachable(host: str, port: int, path: str = "/", timeout: int = 3) -> bool:
    try:
        urllib.request.urlopen(f"http://{host}:{port}{path}", timeout=timeout)
        return True
    except Exception:
        return False


def neo4j_reachable() -> bool:
    return service_reachable("localhost", 7474)


def qdrant_reachable() -> bool:
    return service_reachable("localhost", 6333)


def comfyui_reachable() -> bool:
    return service_reachable("localhost", 8188)


require_neo4j = pytest.mark.skipif(not neo4j_reachable(), reason="Neo4j not available")
require_qdrant = pytest.mark.skipif(not qdrant_reachable(), reason="Qdrant not available")
require_comfyui = pytest.mark.skipif(not comfyui_reachable(), reason="ComfyUI not available")
