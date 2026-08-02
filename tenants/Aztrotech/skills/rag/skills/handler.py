"""rag handler — RAG Knowledge Base
Búsqueda semántica con Ollama embeddings.
"""
import json
import os
import httpx
import numpy as np
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent.parent.parent
INDEX_PATH = REPO / "memory" / "index.json"
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")


async def _embed(text: str) -> list[float]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{OLLAMA_ENDPOINT}/api/embeddings", json={"model": EMBED_MODEL, "prompt": text})
        resp.raise_for_status()
        return resp.json()["embedding"]


def _cosine_sim(a: list[float], b: list[float]) -> float:
    a_np, b_np = np.array(a), np.array(b)
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))


async def execute(context: Any) -> dict:
    input_data = context if isinstance(context, dict) else {}
    action = input_data.get("action", "search")
    top_k = input_data.get("top_k", 5)
    min_score = input_data.get("min_score", 0.65)

    if not INDEX_PATH.exists():
        return {"action": action, "error": "Index not found", "results": []}

    with open(INDEX_PATH) as f:
        index = json.load(f)

    if action == "search":
        query = input_data.get("query", "")
        if not query:
            return {"action": "search", "error": "Query required", "results": []}
        q_emb = await _embed(query)
        scored = []
        for item in index:
            score = _cosine_sim(q_emb, item["embedding"])
            if score >= min_score:
                scored.append({"score": round(score, 4), "source": item["source"], "text": item["text"]})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return {"action": "search", "query": query, "results": scored[:top_k]}

    elif action == "index":
        docs = input_data.get("docs", {})
        new_index = []
        for source, content in docs.items():
            chunks = _chunk_text(content)
            for i, chunk in enumerate(chunks):
                emb = await _embed(chunk)
                new_index.append({"source": source, "chunk_id": i, "text": chunk, "embedding": emb})
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(INDEX_PATH, "w") as f:
            json.dump(new_index, f, indent=2)
        return {"action": "index", "chunks": len(new_index), "sources": list(docs.keys())}

    return {"action": action, "error": f"Unknown action: {action}"}


def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            last_period = text.rfind(".", start, end)
            if last_period > start + chunk_size // 2:
                end = last_period + 1
        chunks.append(text[start:end].strip())
        start = end - overlap if end < len(text) else len(text)
    return chunks
