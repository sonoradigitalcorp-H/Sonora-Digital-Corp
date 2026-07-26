import os
import uuid
import logging
from io import BytesIO
from pathlib import Path
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("aztrotech.storage")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "149.56.46.173:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "aztrotech")
MINIO_PUBLIC_URL = os.getenv("MINIO_PUBLIC_URL", "http://149.56.46.173:9000")

_client = None
MEXICO_TZ = timezone(timedelta(hours=-6))


def _get_client():
    global _client
    if _client is None:
        from minio import Minio
        _client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False,
        )
    return _client


async def save_file(file_data: bytes, filename: str, folder: str = "") -> dict:
    client = _get_client()

    ext = Path(filename).suffix or ".bin"
    object_name = f"{folder}/{uuid.uuid4().hex}{ext}" if folder else f"{uuid.uuid4().hex}{ext}"
    object_name = object_name.lstrip("/")

    content_type = _guess_mime(ext)

    try:
        client.put_object(
            MINIO_BUCKET,
            object_name,
            data=BytesIO(file_data),
            length=len(file_data),
            content_type=content_type,
        )
    except Exception as e:
        logger.error(f"MinIO upload error: {e}")
        raise

    url = f"{MINIO_PUBLIC_URL}/{MINIO_BUCKET}/{object_name}"
    now = datetime.now(MEXICO_TZ).isoformat()

    logger.info(f"Saved {filename} → {object_name} ({len(file_data)} bytes)")
    return {
        "url": url,
        "path": object_name,
        "size": len(file_data),
        "mime": content_type,
        "created_at": now,
    }


async def save_photo(photo_bytes: bytes) -> dict:
    return await save_file(photo_bytes, "photo.jpg", "photos")


async def save_video(video_bytes: bytes) -> dict:
    return await save_file(video_bytes, "video.mp4", "videos")


async def save_audio(audio_bytes: bytes) -> dict:
    return await save_file(audio_bytes, "audio.ogg", "audio")


async def save_document(doc_bytes: bytes, filename: str) -> dict:
    return await save_file(doc_bytes, filename, "documents")


def get_url(path: str) -> str:
    return f"{MINIO_PUBLIC_URL}/{MINIO_BUCKET}/{path.lstrip('/')}"


def list_files(folder: str = "", prefix: str = "") -> list[dict]:
    client = _get_client()
    objects = client.list_objects(MINIO_BUCKET, prefix=f"{folder}/{prefix}" if folder else prefix)
    result = []
    for obj in objects:
        result.append({
            "name": obj.object_name,
            "size": obj.size,
            "last_modified": obj.last_modified.isoformat() if obj.last_modified else "",
            "url": get_url(obj.object_name),
        })
    return result


def _guess_mime(ext: str) -> str:
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
        ".mp4": "video/mp4", ".webm": "video/webm", ".mov": "video/quicktime",
        ".mp3": "audio/mpeg", ".ogg": "audio/ogg", ".wav": "audio/wav",
        ".m4a": "audio/mp4", ".f4a": "audio/mp4",
        ".pdf": "application/pdf", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".json": "application/json", ".txt": "text/plain",
    }.get(ext.lower(), "application/octet-stream")
