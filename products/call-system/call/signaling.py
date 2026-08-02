import json
import logging
from aiohttp import web

logger = logging.getLogger(__name__)

connected_clients = {}

class SignalingHandler:
    def __init__(self, on_offer_callback):
        self.on_offer = on_offer_callback

    async def handle(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        client_id = id(ws)
        connected_clients[client_id] = ws
        logger.info(f"Cliente {client_id} conectado")

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    msg_type = data.get("type")

                    if msg_type == "offer":
                        await self.on_offer(client_id, ws, data["sdp"])
                    elif msg_type == "candidate":
                        await self.on_offer(client_id, ws, None, data.get("candidate"))
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f"WS error: {ws.exception()}")
        except Exception as e:
            logger.error(f"Error en signaling: {e}")
        finally:
            connected_clients.pop(client_id, None)
            logger.info(f"Cliente {client_id} desconectado")

        return ws
