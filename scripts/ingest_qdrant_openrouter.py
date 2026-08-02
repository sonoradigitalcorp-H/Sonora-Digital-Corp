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

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "tenants" / "Aztrotech" / "knowledge"
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "sdc_knowledge")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "64"))
TENANT_ID = "aztrotech"

EMBED_DIM = 384  # paraphrase-multilingual-MiniLM-L12-v2 (FastEmbed ONNX)
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

client = QdrantClient(url=QDRANT_URL, prefer_grpc=False)

# Lazy-load embedding model
_embed_model = None


def get_embed_model():
    global _embed_model
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
    vec = list(model.embed([text]))[0].tolist()
    return vec


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        if end == len(text):
            break
        start = end - overlap
    return chunks


def point_id(text: str, source: str, chunk_idx: int) -> str:
    h = hashlib.sha256(f"{source}:{chunk_idx}:{text}".encode()).hexdigest()
    # UUID v4 format from hash (deterministic)
    return f"{h[:8]}-{h[8:12]}-4{h[13:16]}-8{h[17:20]}-{h[20:32]}"


def ingest_file(filepath: Path) -> int:
    content = filepath.read_text(encoding="utf-8")
    chunks = chunk_text(content)
    inserted = 0

    for i, chunk in enumerate(chunks):
        pid = point_id(chunk, filepath.name, i)
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
                "source": filepath.name,
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

    md_files = list(KNOWLEDGE_DIR.glob("*.md"))
    if not md_files:
        print(f"No hay archivos .md en {KNOWLEDGE_DIR}")
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