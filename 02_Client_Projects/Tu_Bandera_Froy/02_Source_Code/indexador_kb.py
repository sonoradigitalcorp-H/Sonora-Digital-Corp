#!/usr/bin/env python3
"""indexador_kb.py — Indexador KB Tu Bandera A.C. con búsqueda semántica + re-rank BM25.

Uso:
  python3 indexador_kb.py --index   # reconstruye la colección Qdrant
  python3 indexador_kb.py --search "fentanilo"  # búsqueda con re-rank
"""
import os
import re
import glob
import hashlib
import math
import argparse
import requests
from collections import Counter

# ─── Configuración ───────────────────────────────────────────────────────────
OLLAMA    = os.getenv("OLLAMA_URL",  "http://127.0.0.1:11434/api/embed")
QDRANT    = os.getenv("QDRANT_URL",  "http://127.0.0.1:6333")
KB        = os.getenv("KB_PATH",     "/opt/hermes/tubandera/kb")
COLLECTION = "tubandera_kb"
EMBED_MODEL = "nomic-embed-text"


# ─── Embeddings ──────────────────────────────────────────────────────────────
def embed(text: str) -> list[float]:
    r = requests.post(OLLAMA, json={"model": EMBED_MODEL, "input": text}, timeout=30)
    r.raise_for_status()
    return r.json()["embeddings"][0]


# ─── BM25 re-rank (sin dependencias pesadas) ─────────────────────────────────
def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]+", text.lower())


class BM25:
    def __init__(self, corpus: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.corpus_tok = [_tokenize(doc) for doc in corpus]
        self.N = len(corpus)
        self.avgdl = sum(len(d) for d in self.corpus_tok) / max(self.N, 1)
        # df por término
        df: dict[str, int] = {}
        for doc in self.corpus_tok:
            for term in set(doc):
                df[term] = df.get(term, 0) + 1
        self.idf: dict[str, float] = {
            term: math.log((self.N - freq + 0.5) / (freq + 0.5) + 1)
            for term, freq in df.items()
        }

    def score(self, query: str, doc_idx: int) -> float:
        query_terms = _tokenize(query)
        doc = self.corpus_tok[doc_idx]
        doc_freq = Counter(doc)
        dl = len(doc)
        score = 0.0
        for term in query_terms:
            if term not in self.idf:
                continue
            tf = doc_freq.get(term, 0)
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            score += self.idf[term] * (numerator / denominator)
        return score

    def rank(self, query: str) -> list[tuple[int, float]]:
        scores = [(i, self.score(query, i)) for i in range(self.N)]
        return sorted(scores, key=lambda x: x[1], reverse=True)


# ─── Chunking ────────────────────────────────────────────────────────────────
def _load_chunks() -> list[dict]:
    docs = []
    for path in glob.glob(f"{KB}/**/*.md", recursive=True):
        try:
            txt = open(path, encoding="utf-8").read()
        except Exception:
            continue
        for block in txt.split("\n## "):
            if block.strip():
                docs.append({
                    "text": block.strip(),
                    "src": os.path.relpath(path, KB)
                })
    return docs


# ─── Indexación ──────────────────────────────────────────────────────────────
def index_kb():
    """Recrea la colección Qdrant con todos los chunks de la KB."""
    docs = _load_chunks()
    print(f"Chunks encontrados: {len(docs)}")

    # Recrear colección
    requests.delete(f"{QDRANT}/collections/{COLLECTION}", timeout=10)
    r = requests.put(
        f"{QDRANT}/collections/{COLLECTION}",
        json={"vectors": {"size": 768, "distance": "Cosine"}},
        timeout=10
    )
    print(f"Colección creada: {r.status_code}")

    points = []
    for d in docs:
        vec = embed(d["text"])
        hid = int(hashlib.md5(d["text"].encode()).hexdigest()[:15], 16)
        points.append({"id": hid, "vector": vec, "payload": {"text": d["text"], "src": d["src"]}})

    ok = 0
    for i in range(0, len(points), 20):
        batch = points[i:i + 20]
        r = requests.put(
            f"{QDRANT}/collections/{COLLECTION}/points",
            json={"points": batch},
            timeout=30
        )
        if r.status_code in (200, 202):
            ok += len(batch)
    print(f"Indexados OK: {ok}")
    return ok


# ─── Búsqueda semántica pura ──────────────────────────────────────────────────
def search_kb(query: str, limit: int = 5) -> list[dict]:
    """Búsqueda semántica coseno en Qdrant. Devuelve chunks con score y src."""
    qv = embed(query)
    r = requests.post(
        f"{QDRANT}/collections/{COLLECTION}/points/search",
        json={"vector": qv, "limit": limit, "with_payload": True},
        timeout=20
    )
    results = r.json().get("result", [])
    return [
        {"text": h["payload"]["text"], "src": h["payload"].get("src", ""), "score": h["score"]}
        for h in results
    ]


# ─── Búsqueda semántica + BM25 re-rank ───────────────────────────────────────
def search_kb_rerank(query: str, top_k: int = 10, rerank_k: int = 3) -> list[dict]:
    """
    1. Recupera top_k chunks por similitud coseno (Qdrant).
    2. Re-rankea con BM25 sobre el texto de esos chunks.
    3. Devuelve rerank_k mejores.

    Args:
        query:    consulta en lenguaje natural
        top_k:    candidatos a recuperar por semántica
        rerank_k: chunks finales a devolver tras re-rank

    Returns:
        Lista de dicts con keys: text, src, cosine_score, bm25_score
    """
    candidates = search_kb(query, limit=top_k)
    if not candidates:
        return []

    texts = [c["text"] for c in candidates]
    bm25 = BM25(texts)
    ranked = bm25.rank(query)

    results = []
    for idx, bm25_score in ranked[:rerank_k]:
        c = candidates[idx]
        results.append({
            "text":         c["text"],
            "src":          c["src"],
            "cosine_score": round(c["score"], 4),
            "bm25_score":   round(bm25_score, 4),
        })
    return results


# ─── Context builder para el LLM ─────────────────────────────────────────────
def build_rag_context(query: str, max_chars: int = 1200) -> str:
    """
    Wrapper listo para usar en vps_ai_server.py.
    Devuelve string con los chunks más relevantes para inyectar al system prompt.
    """
    chunks = search_kb_rerank(query, top_k=10, rerank_k=3)
    if not chunks:
        return ""
    parts = []
    total = 0
    for c in chunks:
        snippet = c["text"][:500]
        if total + len(snippet) > max_chars:
            break
        parts.append(f"[Fuente: {c['src']}]\n{snippet}")
        total += len(snippet)
    return "\n\n---\n\n".join(parts)


# ─── CLI ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indexador KB Tu Bandera A.C.")
    parser.add_argument("--index",  action="store_true", help="Indexar/reindexar KB en Qdrant")
    parser.add_argument("--search", type=str, default="",  help="Buscar query con re-rank")
    parser.add_argument("--top-k",  type=int, default=10,  help="Candidatos semánticos (default 10)")
    parser.add_argument("--k",      type=int, default=3,   help="Resultados finales (default 3)")
    args = parser.parse_args()

    if args.index:
        index_kb()

    if args.search:
        print(f"\n--- BÚSQUEDA (coseno + BM25 re-rank): '{args.search}' ---")
        hits = search_kb_rerank(args.search, top_k=args.top_k, rerank_k=args.k)
        for i, h in enumerate(hits, 1):
            print(f"\n#{i} [cosine={h['cosine_score']} bm25={h['bm25_score']}] src={h['src']}")
            print(h["text"][:200])

    if not args.index and not args.search:
        parser.print_help()
