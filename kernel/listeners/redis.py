"""Redis Listener — Kernel entry point via Redis Streams (HAS-004)
Listens for incoming requests on Redis streams and processes them.
"""
import json
import logging

from kernel.main import HermesKernel


logger = logging.getLogger("kernel.redis")


class RedisListener:
    def __init__(self, kernel: HermesKernel, redis_url: str = "redis://localhost:6379/0"):
        self.kernel = kernel
        self.redis_url = redis_url
        self._running = False

    async def start(self, stream: str = "kernel:requests", group: str = "kernel-workers"):
        import redis.asyncio as aioredis
        self._running = True
        self.r = await aioredis.from_url(self.redis_url)
        try:
            await self.r.xgroup_create(stream, group, id="0", mkstream=True)
        except Exception:
            pass
        logger.info(f"Listening on Redis stream '{stream}' (group '{group}')")
        while self._running:
            try:
                messages = await self.r.xreadgroup(group, self.kernel.config.get("worker_id", "worker-1"), {stream: ">"}, count=1, block=5000)
                if messages:
                    for stream_name, entries in messages:
                        for msg_id, data in entries:
                            await self._handle(stream_name, msg_id, data)
            except Exception as e:
                logger.error(f"Redis listener error: {e}")

    async def _handle(self, stream: str, msg_id: str, data: dict):
        try:
            payload = {k.decode(): json.loads(v.decode()) if isinstance(v, bytes) else v.decode() for k, v in data.items()}
            results = await self.kernel.process(payload)
            await self.r.xadd(f"{stream}:results", {"task_id": msg_id, "result": json.dumps(results)})
            await self.r.xack(stream, "kernel-workers", msg_id)
        except Exception as e:
            logger.error(f"Handler error: {e}")

    async def stop(self):
        self._running = False
