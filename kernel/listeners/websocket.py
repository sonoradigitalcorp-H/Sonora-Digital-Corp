"""WebSocket Listener — Kernel entry point via WebSocket (HAS-004)
Provides real-time bidirectional communication with the Experience Layer.
"""
import json
import logging

from kernel.main import HermesKernel


logger = logging.getLogger("kernel.ws")


class WebSocketListener:
    def __init__(self, kernel: HermesKernel):
        self.kernel = kernel
        self._connections: dict[str, object] = {}

    async def handle(self, websocket, client_id: str):
        import websockets
        self._connections[client_id] = websocket
        try:
            async for message in websocket:
                data = json.loads(message)
                results = await self.kernel.process(data)
                await websocket.send(json.dumps(results))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self._connections.pop(client_id, None)
