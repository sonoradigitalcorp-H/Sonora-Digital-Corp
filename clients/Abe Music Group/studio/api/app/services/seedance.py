import httpx
from app.config import settings

class SeedanceClient:
    def __init__(self):
        self.base = settings.seedance_base_url
        self.headers = {
            "Authorization": f"Bearer {settings.seedance_api_key}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=120)

    async def create_generation(self, payload: dict) -> dict:
        r = await self.client.post(
            f"{self.base}/v1/videos/generations",
            headers=self.headers,
            json=payload
        )
        r.raise_for_status()
        return r.json()

    async def get_task(self, task_id: str) -> dict:
        r = await self.client.get(
            f"{self.base}/v1/tasks/{task_id}",
            headers=self.headers
        )
        r.raise_for_status()
        return r.json()

seedance = SeedanceClient()
