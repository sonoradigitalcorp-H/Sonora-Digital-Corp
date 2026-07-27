import asyncio
import logging
from datetime import datetime

from apps.core.config import settings
from apps.core.models import Order, Client, OrderCreate
from apps.core.database import db
from agents.video_agent import VideoAgent
from agents.voice_agent import VoiceAgent
from agents.messaging_agent import MessagingAgent

logger = logging.getLogger(__name__)

video_agent = VideoAgent()
voice_agent = VoiceAgent()
messaging_agent = MessagingAgent()


class Orchestrator:
    def __init__(self):
        self._approvals = {}
        self._photos = {}
        self._websockets = set()

    async def create_order(self, data: OrderCreate) -> Order:
        order = Order(data)
        db.save_order(order.to_dict())

        client_data = db.get_client(data.client_phone)
        if not client_data:
            client = Client(phone=data.client_phone, name=data.client_name)
            db.save_client(client.to_dict())
        else:
            client_obj = Client(phone=client_data["phone"], name=client_data["name"])
            for k, v in client_data.items():
                if hasattr(client_obj, k):
                    setattr(client_obj, k, v)
            client_obj.total_orders = int(client_data.get("total_orders", 0)) + 1
            client_obj.last_order_at = datetime.utcnow().isoformat()
            db.save_client(client_obj.to_dict())

        db.increment_counter("orders_created")
        logger.info(f"Order {order.id} created for {data.client_name}")

        return order

    async def process_order(self, order_id: str):
        order_data = db.get_order(order_id)
        if not order_data:
            logger.error(f"Order {order_id} not found")
            return

        client_data = db.get_client(order_data["client_phone"])
        if not client_data:
            logger.error(f"Client not found for order {order_id}")
            return

        try:
            await self._step_check_photo(order_data, client_data)
            await self._step_generate_audio(order_data)
            await self._step_generate_video(order_data)
            await self._step_request_approval(order_data)
            await self._step_deliver(order_data, client_data)
        except Exception as e:
            logger.error(f"Order {order_id} failed: {e}")
            db.update_order_status(order_id, "failed", {"error": str(e)})
            await voice_agent.call_me(f"La orden {order_id} falló: {str(e)}")
            await self._broadcast({
                "type": "order.error",
                "order_id": order_id,
                "message": str(e),
            })

    async def _step_check_photo(self, order_data: dict, client_data: dict):
        order_id = order_data["id"]
        phone = order_data["client_phone"]

        if order_data.get("photo_url"):
            db.update_order_status(order_id, "photo_ready")
            return

        db.update_order_status(order_id, "requesting_photo")
        msg = (
            f"Hola {order_data['client_name']}! 👋\n\n"
            f"Para crear tu video personalizado, necesito una foto clara de tu rostro.\n\n"
            f"📸 *Requisitos:*\n"
            f"• Foto frontal, bien iluminada\n"
            f"• Sin lentes oscuros ni sombrero\n"
            f"• Mira directamente a la cámara\n\n"
            f"¡Envíamela por aquí mismo!"
        )
        await messaging_agent.send_whatsapp(phone, msg)
        db.increment_counter("photos_requested")

        for _ in range(300):
            if order_id in self._photos:
                photo_url = self._photos.pop(order_id)
                db.update_order_status(order_id, "photo_ready", {"photo_url": photo_url})
                client_data["photo_url"] = photo_url
                db.save_client(client_data)
                logger.info(f"Photo received for order {order_id}")
                return
            await asyncio.sleep(1)

        await voice_agent.call_me(
            f"La orden {order_id} de {order_data['client_name']} lleva "
            f"5 minutos esperando foto. ¿La llamo al cliente?"
        )

    async def _step_generate_audio(self, order_data: dict):
        order_id = order_data["id"]
        script = order_data["script"]
        phone = order_data["client_phone"]

        db.update_order_status(order_id, "generating_audio")

        client_data = db.get_client(phone)
        ref_audio = client_data.get("voice_ref_url") if client_data else None

        result = await video_agent.generate_tts(
            text=script,
            reference_audio=ref_audio,
        )

        audio_url = result["audio_url"]
        cost = result.get("cost", 0.01)
        db.update_order_status(order_id, "audio_ready", {
            "audio_url": audio_url,
        })
        db.increment_counter("audio_cost", cost)
        db.increment_counter("total_cost", cost)
        logger.info(f"Audio generated for {order_id}: ${cost}")

    async def _step_generate_video(self, order_data: dict):
        order_id = order_data["id"]
        photo_url = order_data["photo_url"]
        audio_url = order_data["audio_url"]

        db.update_order_status(order_id, "generating_video")
        db.increment_counter("videos_generated")

        result = await video_agent.generate_talking_head(
            image_url=photo_url,
            audio_url=audio_url,
            model=order_data.get("style", "realistic"),
        )

        video_url = result["video_url"]
        cost = result.get("cost", 0.08)
        db.update_order_status(order_id, "video_ready", {
            "video_url": video_url,
        })
        db.increment_counter("video_cost", cost)
        db.increment_counter("total_cost", cost)
        logger.info(f"Video generated for {order_id}: ${cost}")

    async def _step_request_approval(self, order_data: dict):
        order_id = order_data["id"]
        client_name = order_data["client_name"]
        video_url = order_data["video_url"]

        db.update_order_status(order_id, "awaiting_approval")

        msg = (
            f"📹 *Video listo para {client_name}* \n\n"
            f"{video_url}\n\n"
            f"¿Apruebo y entrego? Responde 'sí' o 'no'"
        )
        await messaging_agent.send_whatsapp(settings.owner_phone, msg, media_url=video_url)

        await voice_agent.call_me(
            f"El video para {client_name} está listo. "
            f"¿Lo apruebo y entrego?",
            order_id=order_id,
        )

    async def _step_deliver(self, order_data: dict, client_data: dict):
        order_id = order_data["id"]
        video_url = order_data["video_url"]
        client_phone = order_data["client_phone"]
        client_name = order_data["client_name"]

        db.update_order_status(order_id, "delivering")

        msg = (
            f"🎬 *¡Tu video personalizado está listo!*\n\n"
            f"Hola {client_name}, aquí tienes tu video.\n\n"
            f"Si necesitas otro, solo escríbeme."
        )
        await messaging_agent.send_whatsapp(client_phone, msg, media_url=video_url)

        total_audio = float(db.get_todays_metrics().get("audio_cost", 0))
        total_video = float(db.get_todays_metrics().get("video_cost", 0))

        db.update_order_status(order_id, "completed", {
            "completed_at": datetime.utcnow().isoformat(),
            "total_cost": total_audio + total_video,
        })

        db.increment_counter("orders_completed")
        db.increment_counter("revenue", settings.product_prices.get(
            order_data.get("product_type", "avatar_mensual"), 15.00
        ))

        await voice_agent.call_me(
            f"Video de {client_name} entregado con éxito. "
            f"Llevas {db.get_todays_metrics().get('orders_completed', 0)} videos hoy.",
        )

    async def handle_approval(self, order_id: str, approved: bool, reason: str = ""):
        if approved:
            self._approvals[order_id] = True
            order_data = db.get_order(order_id)
            if order_data:
                db.update_order_status(order_id, "approved", {"approved_by": "owner"})
                client_data = db.get_client(order_data["client_phone"])
                if client_data:
                    await self._step_deliver(order_data, client_data)
        else:
            self._approvals[order_id] = False
            db.update_order_status(order_id, "rejected", {"rejection_reason": reason})
            await messaging_agent.send_whatsapp(
                settings.owner_phone,
                f"❌ Orden {order_id} rechazada: {reason or 'Sin motivo'}",
            )

    async def handle_incoming_photo(self, phone: str, photo_url: str):
        client_data = db.get_client(phone)
        if client_data:
            client_data["photo_url"] = photo_url
            db.save_client(client_data)

        order = None
        for o in db.list_orders(status="requesting_photo"):
            if o["client_phone"] == phone:
                order = o
                break

        if order:
            self._photos[order["id"]] = photo_url
            await messaging_agent.send_whatsapp(
                phone,
                "✅ ¡Foto recibida! En unos minutos tendrás tu video listo. 🎬",
            )
        else:
            await messaging_agent.send_whatsapp(
                phone,
                "✅ ¡Foto recibida! ¿Quieres crear un video? Envíame el texto que quieres que diga.",
            )

    def add_websocket(self, ws):
        self._websockets.add(ws)

    def remove_websocket(self, ws):
        self._websockets.discard(ws)

    async def _broadcast(self, event: dict):
        for ws in self._websockets.copy():
            try:
                await ws.send_json(event)
            except Exception:
                self._websockets.discard(ws)

    async def handle_ws_message(self, data: dict):
        msg_type = data.get("type")
        if msg_type == "approve":
            await self.handle_approval(data["order_id"], True)
            return {"status": "approved"}
        elif msg_type == "reject":
            await self.handle_approval(data["order_id"], False, data.get("reason", ""))
            return {"status": "rejected"}
        return {"status": "unknown"}


orchestrator = Orchestrator()
