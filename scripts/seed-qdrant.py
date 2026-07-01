#!/usr/bin/env python3
"""Seed Qdrant con artistas desde data/abe-music.json.

Uso: python3 scripts/seed-qdrant.py [--recreate]
"""
import argparse
import json
import logging
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning, module="qdrant_client")

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, PointStruct, VectorParams,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("seed-qdrant")

BASE = Path(__file__).resolve().parent.parent
DATA_FILE = BASE / "data" / "abe-music.json"
COLLECTION = "abe-artists"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333


def load_artists() -> list[dict]:
    with open(DATA_FILE) as f:
        data = json.load(f)
    return list(data.get("artists", {}).values())


def artist_to_vector(artist: dict) -> list[float]:
    """Convierte artista a vector numerico para Qdrant.
    Usamos datos del artista como features."""
    return [
        artist.get("streams", 0) / 1e8,
        artist.get("revenue", 0) / 5e5,
        artist.get("followers", 0) / 1e4,
        artist.get("monthly_listeners", 0) / 1e6,
        artist.get("nb_album", 0) / 50,
        artist.get("youtube_views", 0) / 1e8,
        float(artist.get("spotify_monthly_listeners", 0)) / 1e6,
    ]


def artist_payload(artist: dict) -> dict:
    return {
        "id": artist.get("id", ""),
        "nombre": artist.get("nombre", ""),
        "genero": artist.get("genero", ""),
        "streams": artist.get("streams", 0),
        "revenue": artist.get("revenue", 0),
        "followers": artist.get("followers", 0),
        "monthly_listeners": artist.get("monthly_listeners", 0),
        "spotify_monthly_listeners": artist.get("spotify_monthly_listeners", 0),
        "nb_album": artist.get("nb_album", 0),
        "deezer_id": artist.get("deezer_id", 0),
        "apple_music_id": artist.get("apple_music_id", 0),
        "status": artist.get("status", ""),
        "spotify_url": artist.get("spotify_url", ""),
        "apple_music_url": artist.get("apple_music_url", ""),
        "picture": artist.get("picture", ""),
        "last_sync": artist.get("last_sync", ""),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--recreate", action="store_true", help="Borra y recrea la coleccion")
    args = parser.parse_args()

    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Verificar conectividad
    try:
        collections = client.get_collections()
        log.info(f"Qdrant OK: {len(collections.collections)} colecciones existentes")
    except Exception as e:
        log.error(f"Qdrant no accesible: {e}")
        return

    # Recrear si se pide
    if args.recreate:
        try:
            client.delete_collection(COLLECTION)
            log.info(f"Coleccion {COLLECTION} eliminada")
        except Exception:
            pass

    # Crear coleccion si no existe
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=7, distance=Distance.COSINE),
        )
        log.info(f"Coleccion {COLLECTION} creada (7-dim, cosine)")

    # Cargar artistas
    artists = load_artists()
    if not artists:
        log.warning("No artists found in data/abe-music.json")
        return

    # Preparar puntos
    points = []
    for i, artist in enumerate(artists):
        vector = artist_to_vector(artist)
        payload = artist_payload(artist)
        points.append(PointStruct(
            id=i + 1,
            vector=vector,
            payload=payload,
        ))

    # Upsert
    client.upsert(
        collection_name=COLLECTION,
        points=points,
    )

    log.info(f"Seeded {len(points)} artistas en {COLLECTION}")
    for p in points:
        log.info(f"  {p.id}: {p.payload['nombre']} ({p.payload['genero']}) — {p.payload['streams']:,} streams")

    # Test scroll (compatible con Qdrant 1.7)
    log.info("---")
    log.info("Verificando datos en coleccion...")
    count = client.count(collection_name=COLLECTION)
    log.info(f"  {count.count} puntos en {COLLECTION}")
    scroll = client.scroll(collection_name=COLLECTION, limit=5)
    for point in scroll[0]:
        log.info(f"  {point.id}: {point.payload['nombre']} — {point.payload['streams']:,} streams")


if __name__ == "__main__":
    main()
