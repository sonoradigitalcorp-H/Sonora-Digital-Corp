import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from apps.core.config import settings
from apps.core.database import db
from apps.core.orchestrator import orchestrator
from apps.core.models import OrderCreate, OrderResponse
from webhooks.twilio_whatsapp import router as whatsapp_router
from webhooks.twilio_voice import router as voice_router
from dashboard.routes import router as dashboard_router
from agents.voice_agent import VoiceAgent

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Clon Digital starting on {settings.environment}")
    voice = VoiceAgent()
    voice.set_approval_callback(orchestrator.handle_approval)
    yield
    logger.info("Clon Digital shutting down")


app = FastAPI(
    title="Clon Digital API",
    description="Sistema de clon digital autónomo para creación de videos personalizados",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(whatsapp_router)
app.include_router(voice_router)
app.include_router(dashboard_router)


@app.get("/health")
async def health():
    metrics = db.get_todays_metrics()
    return {
        "status": "ok",
        "service": "clon-digital",
        "environment": settings.environment,
        "metrics": metrics,
    }


@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(data: OrderCreate):
    order = await orchestrator.create_order(data)
    import asyncio
    asyncio.create_task(orchestrator.process_order(order.id))
    return OrderResponse(
        order_id=order.id,
        status=order.status,
        client_name=order.client_name,
        client_phone=order.client_phone,
        product_type=order.product_type,
        created_at=order.created_at,
        estimated_cost_usd=order.total_cost or 0.10,
    )


@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: str):
    order = db.get_order(order_id)
    if not order:
        from fastapi import HTTPException
        raise HTTPException(404, "Order not found")
    return order


@app.post("/api/v1/orders/{order_id}/approve")
async def approve_order(order_id: str):
    await orchestrator.handle_approval(order_id, True)
    return {"status": "approved"}


@app.post("/api/v1/orders/{order_id}/reject")
async def reject_order(order_id: str, reason: str = ""):
    await orchestrator.handle_approval(order_id, False, reason)
    return {"status": "rejected"}


@app.post("/api/v1/call/assistant")
async def call_assistant(message: str):
    from agents.voice_agent import VoiceAgent
    va = VoiceAgent()
    sid = await va.call_me(message)
    return {"call_sid": sid, "status": "initiated"}


@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    orchestrator.add_websocket(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            response = await orchestrator.handle_ws_message(data)
            await websocket.send_json(response)
    except WebSocketDisconnect:
        orchestrator.remove_websocket(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        orchestrator.remove_websocket(websocket)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
