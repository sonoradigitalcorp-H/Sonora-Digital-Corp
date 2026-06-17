"""
JARVIS Embedding Service — Genera embeddings locales con Ollama.
"""

import logging
import json
from typing import List, Optional
import requests

log = logging.getLogger("jarvis.embeddings")

EMBED_MODEL = "nomic-embed-text:latest"
EMBED_DIM = 768
OLLAMA_URL = "http://localhost:11434"


def embed_text(text: str, model: str = EMBED_MODEL) -> Optional[List[float]]:
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
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


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> List[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks
