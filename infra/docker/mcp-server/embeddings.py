"""
MCP Embedding Service — Generate real embeddings via Ollama.
Docker proof: tries host.docker.internal first, then localhost.
"""

import logging
import requests
from typing import List, Optional

log = logging.getLogger("mcp.embeddings")

EMBED_MODEL = "nomic-embed-text:latest"
EMBED_DIM = 768
OLLAMA_URLS = [
    "http://host.docker.internal:11434",  # Docker → host
    "http://localhost:11434",  # Native
]

_ollama_url = None


def _find_ollama() -> Optional[str]:
    global _ollama_url
    if _ollama_url:
        return _ollama_url
    for url in OLLAMA_URLS:
        try:
            resp = requests.get(f"{url}/api/tags", timeout=2)
            if resp.ok:
                _ollama_url = url
                log.info(f"Ollama found at {url}")
                return url
        except Exception:
            continue
    log.warning("No Ollama instance found")
    return None


def embed_text(text: str, model: str = EMBED_MODEL) -> Optional[List[float]]:
    url = _find_ollama()
    if not url:
        return None
    try:
        resp = requests.post(
            f"{url}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("embedding")
    except Exception as e:
        log.error(f"Embedding failed: {e}")
        return None


def embed_batch(
    texts: List[str], model: str = EMBED_MODEL
) -> List[Optional[List[float]]]:
    return [embed_text(t, model) for t in texts]
