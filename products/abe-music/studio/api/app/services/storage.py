import json, os, aiofiles
from pathlib import Path
from app.config import settings

class StorageService:
    def __init__(self):
        self.path = Path(settings.storage_path)
        self.path.mkdir(parents=True, exist_ok=True)

    async def save_video(self, task_id: str, url: str) -> str:
        import httpx
        ext = ".mp4"
        filename = f"{task_id}{ext}"
        filepath = self.path / filename
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(r.content)
        return f"{settings.storage_public_url}/{filename}"

    def get_path(self, filename: str) -> Path:
        return self.path / filename

storage = StorageService()
