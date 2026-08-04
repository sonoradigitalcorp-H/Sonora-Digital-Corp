#!/usr/bin/env python3
"""Ingestión Qdrant con embeddings locales (FastEmbed ONNX) — Simple, idempotente, autónomo.

Lee knowledge/*.md → chunk 512/64 → embeddings local multilingual (384-dim) → upsert Qdrant.
Idempotente: hash SHA256(chunk+metadata) = point_id (UUID v4) → re-ejecutable sin duplicados.
"""

import hashlib
import json
import os
import sys
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

KNOWLEDGE_DIR = Path(os.getenv(
    "KNOWLEDGE_DIR",
    str(Path(__file__).resolve().parent.parent / "tenants" / "Aztrotech" / "knowledge"),
))
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "64"))
TENANT_ID = os.getenv("TENANT_ID", "aztrotech")
# Colección por tenant (coherente con rag_per_tenant: kb_<tenant_id>)
COLLECTION = os.getenv("QDRANT_COLLECTION", f"kb_{TENANT_ID.replace('-', '_')}")

EMBED_DIM = int(os.getenv("EMBEDDING_DIM", "384"))  # all-minilm (Ollama) / paraphrase-multilingual (FastEmbed)
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-minilm")
EMBED_BACKEND = os.getenv("EMBED_BACKEND", "ollama")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

client = QdrantClient(url=QDRANT_URL, prefer_grpc=False)

# Lazy-load embedding model
_embed_model = None


def get_embed_model():
    global _embed_model
    if EMBED_BACKEND == "ollama":
        return "ollama"
    if _embed_model is None:
        from fastembed import TextEmbedding
        print(f"Cargando modelo embedding: {EMBED_MODEL}...")
        _embed_model = TextEmbedding(model_name=EMBED_MODEL)
    return _embed_model


def ensure_collection():
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION not in collections:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
        print(f"Collection '{COLLECTION}' creada ({EMBED_DIM} dims)")
    else:
        # Verificar dimensión
        info = client.get_collection(COLLECTION)
        if info.config.params.vectors.size != EMBED_DIM:
            print(f"Recreando collection: dimensión distinta ({info.config.params.vectors.size} vs {EMBED_DIM})")
            client.delete_collection(COLLECTION)
            client.create_collection(
                collection_name=COLLECTION,
                vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
            )
        else:
            print(f"Collection '{COLLECTION}' ya existe ({EMBED_DIM} dims)")


def get_embedding(text: str) -> list[float]:
    model = get_embed_model()
    if model == "ollama":
        import httpx
        resp = httpx.post(f"{OLLAMA_URL}/api/embeddings", json={"model": EMBED_MODEL, "prompt": text}, timeout=30)
        resp.raise_for_status()
        return list(resp.json().get("embedding", []))
    vec = list(model.embed([text]))[0].tolist()
    return vec


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    if len(words) <= size:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        chunk = " ".join(words[start:start + size])
        chunks.append(chunk)
        start += size - overlap
    return chunks


def point_id(text: str, source: str, chunk_idx: int) -> str:
    h = hashlib.sha256(f"{source}:{chunk_idx}:{text}".encode()).hexdigest()
    # UUID v4 format from hash (deterministic)
    return f"{h[:8]}-{h[8:12]}-4{h[13:16]}-8{h[17:20]}-{h[20:32]}"


def ingest_file(filepath: Path) -> int:
    content = filepath.read_text(encoding="utf-8")
    chunks = chunk_text(content)
    inserted = 0
    source = str(filepath.relative_to(KNOWLEDGE_DIR))

    for i, chunk in enumerate(chunks):
        pid = point_id(chunk, source, i)
        # Verificar si ya existe (idempotencia)
        existing = client.retrieve(collection_name=COLLECTION, ids=[pid])
        if existing:
            continue

        vector = get_embedding(chunk)
        point = PointStruct(
            id=pid,
            vector=vector,
            payload={
                "text": chunk,
                "source": source,
                "chunk_index": i,
                "tenant_id": TENANT_ID,
            },
        )
        client.upsert(collection_name=COLLECTION, points=[point])
        inserted += 1

    return inserted


def main():
    print(f"=== Ingesta Qdrant Local (sentence-transformers) ===")
    print(f"Knowledge dir: {KNOWLEDGE_DIR}")
    print(f"Qdrant: {QDRANT_URL}")
    print(f"Collection: {COLLECTION}")
    print(f"Embed model: {EMBED_MODEL} ({EMBED_DIM} dims)")
    print(f"Chunk: {CHUNK_SIZE}/{CHUNK_OVERLAP}")
    print()

    ensure_collection()

    # Recorrer *.md, *.txt, *.jsonl (recursivo para bases grandes)
    md_files = [p for p in KNOWLEDGE_DIR.rglob("*") if p.suffix in (".md", ".txt", ".jsonl") and p.is_file()]
    md_files.sort()
    if not md_files:
        print(f"No hay archivos .md/.txt/.jsonl en {KNOWLEDGE_DIR}")
        sys.exit(1)

    total_inserted = 0
    for f in md_files:
        print(f"Procesando {f.name}...")
        n = ingest_file(f)
        total_inserted += n
        print(f"  Insertados: {n} chunks nuevos")

    print(f"\n=== COMPLETADO ===")
    print(f"Total chunks insertados: {total_inserted}")

    # Verificar
    info = client.get_collection(COLLECTION)
    print(f"Points en colección: {info.points_count}")


if __name__ == "__main__":
    main()