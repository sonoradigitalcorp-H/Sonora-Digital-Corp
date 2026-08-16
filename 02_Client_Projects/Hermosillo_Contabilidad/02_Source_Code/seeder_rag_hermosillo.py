#!/usr/bin/env python3
"""seeder_rag_hermosillo.py — Indexa la KB del tenant en un almacén RAG ligero.

Docas md de 02_Source_Code/kb/ → chunks → embeddings (OLLAMA_ENDPOINT all-minilm,
VPS OVH — NUNCA local) → knowledge_store.json (líquido, sin qdrant pesado).

Uso:  python3 seeder_rag_hermosillo.py [--rebuild]
"""

import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
KB_DIR = BASE / "kb"
STORE = BASE / "knowledge_store.json"
CHUNK_WORDS = 90  # ~palabras por chunk

OLLAMA_ENDPOINT = os.environ.get("OLLAMA_ENDPOINT", "http://149.56.46.173:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "all-minilm")


def chunk_text(text: str) -> list[str]:
    """Divide texto en chunks ~260 palabras conservando sentido."""
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    words = text.split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= CHUNK_WORDS:
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    return [c for c in chunks if c.strip()]


def embed(text: str) -> list[float] | None:
    """Embedding vía VPS OVH (all-minilm). Retorna None si falla."""
    body = json.dumps({"model": EMBED_MODEL, "prompt": text}).encode()
    req = urllib.request.Request(f"{OLLAMA_ENDPOINT}/api/embeddings", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            d = json.loads(resp.read())
        return d.get("embedding")
    except Exception as e:
        print(f"  ✗ embed error: {e}")
        return None


def main():
    rebuild = "--rebuild" in sys.argv
    docs = []
    for md in sorted(KB_DIR.rglob("*.md")):
        content = md.read_text()
        meta = {"id": md.stem, "cat": md.parent.name, "file": str(md.relative_to(BASE))}
        for i, chunk in enumerate(chunk_text(content)):
            docs.append({"id": f"{md.stem}:{i}", "text": chunk, "meta": meta})

    print(f"📄 {len(docs)} chunks de la KB para indexar")

    existing = {}
    if STORE.exists() and not rebuild:
        existing = {d["id"]: d for d in json.loads(STORE.read_text()).get("documents", [])}

    out = []
    t0 = time.time()
    for i, d in enumerate(docs):
        if d["id"] in existing and existing[d["id"]].get("embedding"):
            out.append(existing[d["id"]])
            continue
        emb = embed(d["text"])
        if emb is None:
            continue
        d["embedding"] = emb
        out.append(d)
        if (i + 1) % 5 == 0:
            print(f"  ✓ {i + 1}/{len(docs)} embarrado")
        time.sleep(0.05)

    STORE.write_text(json.dumps({"model": EMBED_MODEL, "updated": time.time(),
                                 "source": str(KB_DIR), "dim": len(out[0]["embedding"]) if out else 0,
                                 "documents": out}, ensure_ascii=False, indent=1))
    print(f"✅ {len(out)} documentos indexados en {STORE.name} ({time.time() - t0:.1f}s)")


def search(query: str, top: int = 3) -> list[dict]:
    """Busca por similitud coseno en el store. Retorna top chunks."""
    if not STORE.exists():
        return []
    store = json.loads(STORE.read_text())
    qemb = embed(query)
    if not qemb:
        return []
    scored = []
    for d in store.get("documents", []):
        e = d.get("embedding")
        if not e:
            continue
        dot = sum(a * b for a, b in zip(qemb, e))
        na = sum(x * x for x in qemb) ** 0.5
        nb = sum(x * x for x in e) ** 0.5
        if na and nb:
            scored.append((dot / (na * nb), d))
    scored.sort(key=lambda x: -x[0])
    return [{"score": round(s, 3), "text": d["text"][:600],
             "cat": d["meta"]["cat"], "file": d["meta"]["file"]} for s, d in scored[:top]]


def get_rag_context(query: str, top: int = 2) -> str:
    """Devuelve contexto RAG para inyectar al LLM (antes del clasificador)."""
    hits = search(query, top)
    if not hits:
        return ""
    ctx = "\n\n---Contexto RAG Hermosillo (verificado)---\n"
    for h in hits:
        ctx += f"[{h['cat']}] {h['text']}\n"
    return ctx


if __name__ == "__main__":
    main()