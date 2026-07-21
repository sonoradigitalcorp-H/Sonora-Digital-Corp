import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from core.database import db
from core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    orders = db.list_orders(limit=50)
    metrics = db.get_todays_metrics()
    pending = [o for o in orders if o.get("status") == "awaiting_approval"]
    completed = [o for o in orders if o.get("status") == "completed"]
    failed = [o for o in orders if o.get("status") == "failed"]

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clon Digital - Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-100">
    <div class="max-w-6xl mx-auto p-6">
        <header class="flex justify-between items-center mb-8">
            <h1 class="text-3xl font-bold">🎬 Clon Digital</h1>
            <div class="text-sm text-gray-400">
                <span id="status-badge" class="px-3 py-1 rounded-full bg-green-800">Conectado</span>
            </div>
        </header>

        <div class="grid grid-cols-4 gap-4 mb-8">
            <div class="bg-gray-800 p-4 rounded-lg">
                <div class="text-2xl font-bold">{metrics.get('orders_completed', 0)}</div>
                <div class="text-gray-400 text-sm">Completados hoy</div>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg">
                <div class="text-2xl font-bold">{len(pending)}</div>
                <div class="text-gray-400 text-sm">Pendientes</div>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg">
                <div class="text-2xl font-bold">${metrics.get('revenue', 0):.2f}</div>
                <div class="text-gray-400 text-sm">Ingresos hoy</div>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg">
                <div class="text-2xl font-bold">${metrics.get('total_cost', 0):.3f}</div>
                <div class="text-gray-400 text-sm">Costo hoy</div>
            </div>
        </div>

        <div class="mb-8">
            <h2 class="text-xl font-bold mb-4">⏳ Pendientes de aprobación</h2>
            <div id="pending-list">
                {"".join(_render_order_card(o) for o in pending) if pending else
                 '<p class="text-gray-500">No hay órdenes pendientes</p>'}
            </div>
        </div>

        <div>
            <h2 class="text-xl font-bold mb-4">📜 Historial</h2>
            <div class="space-y-2">
                {_render_order_row(o) for o in completed[:10]}
            </div>
        </div>
    </div>

    <script>
        const ws = new WebSocket(`wss://${{location.host}}/api/v1/ws`);
        ws.onmessage = (event) => {{
            const data = JSON.parse(event.data);
            if (data.type === 'order_update' || data.type === 'order.ready') {{
                setTimeout(() => location.reload(), 1000);
            }}
        }};
        ws.onclose = () => {{
            document.getElementById('status-badge').textContent = 'Desconectado';
            document.getElementById('status-badge').className = 'px-3 py-1 rounded-full bg-red-800';
        }};
    </script>
</body>
</html>"""
    return HTMLResponse(html)


@router.get("/api/orders/{order_id}/approve")
async def approve_order(order_id: str):
    from core.orchestrator import orchestrator
    await orchestrator.handle_approval(order_id, True)
    return {"status": "approved"}


@router.get("/api/orders/{order_id}/reject")
async def reject_order(order_id: str, reason: str = ""):
    from core.orchestrator import orchestrator
    await orchestrator.handle_approval(order_id, False, reason)
    return {"status": "rejected"}


def _render_order_card(order: dict) -> str:
    oid = order.get("id", "")
    name = order.get("client_name", "?")
    phone = order.get("client_phone", "?")
    script = order.get("script", "")[:80]
    video_url = order.get("video_url", "")
    cost = order.get("total_cost", 0)

    return f"""
    <div class="bg-gray-800 p-4 rounded-lg mb-3 border-l-4 border-yellow-500">
        <div class="flex justify-between items-start">
            <div>
                <div class="font-bold text-lg">{name}</div>
                <div class="text-sm text-gray-400">{phone}</div>
                <div class="text-sm mt-1 text-gray-300">"{script}"</div>
                <div class="text-xs text-gray-500 mt-1">${cost:.2f} costo | {oid}</div>
            </div>
            <div class="flex gap-2">
                <a href="/api/orders/{oid}/approve"
                   class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm font-bold">
                   ✅ Aprobar
                </a>
                <a href="/api/orders/{oid}/reject?reason=no+gusta"
                   class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded text-sm font-bold">
                   ❌ Rechazar
                </a>
            </div>
        </div>
        {f'<video src="{video_url}" controls class="mt-2 max-h-40 rounded"></video>' if video_url else ''}
    </div>"""


def _render_order_row(order: dict) -> str:
    status_colors = {
        "completed": "text-green-400",
        "failed": "text-red-400",
        "delivering": "text-blue-400",
    }
    sc = status_colors.get(order.get("status", ""), "text-gray-400")
    return f"""
    <div class="bg-gray-800 px-4 py-2 rounded flex justify-between items-center text-sm">
        <span>{order.get('client_name', '?')}</span>
        <span class="{sc}">{order.get('status', '?')}</span>
        <span class="text-gray-500">${order.get('total_cost', 0):.2f}</span>
    </div>"""
