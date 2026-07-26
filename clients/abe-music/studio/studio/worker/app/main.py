import asyncio, httpx, time
from config import settings

SEEDANCE_HEADERS = {
    "Authorization": f"Bearer {settings.seedance_api_key}",
    "Content-Type": "application/json"
}

async def poll_loop():
    print(f"[Worker] Starting poll loop every {settings.poll_interval}s")
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            try:
                pending = await client.get(
                    f"{settings.studio_api_url}/studio/tasks/pending"
                )
                if pending.status_code == 200:
                    data = pending.json()
                    print(f"[Worker] {data.get('count', 0)} tasks pending")

                    poll_resp = await client.post(
                        f"{settings.studio_api_url}/studio/poll"
                    )
                    if poll_resp.status_code == 200:
                        pr = poll_resp.json()
                        print(f"[Worker] Polled {pr.get('polled', 0)} tasks")
                else:
                    print(f"[Worker] API returned {pending.status_code}")
            except Exception as e:
                print(f"[Worker] Error: {e}")
            await asyncio.sleep(settings.poll_interval)

async def main():
    print("[Worker] ABE Studio Worker starting...")
    await poll_loop()

if __name__ == "__main__":
    asyncio.run(main())
