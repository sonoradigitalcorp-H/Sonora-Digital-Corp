"""
Store API — Ecommerce routes for content creator platform.
Integrates with n8n, Mercado Pago, Bitso, Fal.ai.
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

log = logging.getLogger("jarvis.webui.store")
router = APIRouter(prefix="/api/store", tags=["store"])

# ── Persistence ───────────────────────────────────────────────────
STORE_DIR = Path(__file__).resolve().parent.parent.parent / "data"
PRODUCTS_FILE = STORE_DIR / "store-products.json"
ORDERS_FILE = STORE_DIR / "store-orders.json"

# ── In-memory store (persisted to JSON) ───────────────────────────
products = {}
orders = {}

SEED_PRODUCTS = [
    {
        "id": "seed_001",
        "title": "Consultoría IA para Negocios",
        "description": "Diagnóstico y estrategia personalizada de inteligencia artificial para optimizar tus procesos de negocio. Incluye reporte ejecutivo y roadmap de implementación.",
        "price": 780,
        "currency": "MXN",
        "type": "bundle",
        "prompt": "Consultoría IA - diagnóstico estratégico",
        "style": "professional",
        "format": "pdf",
        "preview_url": "",
        "tags": ["ia", "consultoria", "negocios", "automatizacion"],
        "featured": True,
        "created_at": "2026-01-01T00:00:00",
        "nicho": "general"
    },
    {
        "id": "seed_002",
        "title": "Landing Page Profesional",
        "description": "Diseño y desarrollo de landing page optimizada para conversión. Hosting incluido, dominio personalizado, formulario de captura y analytics.",
        "price": 1380,
        "currency": "MXN",
        "type": "bundle",
        "prompt": "Landing page profesional con diseño moderno",
        "style": "modern",
        "format": "html",
        "preview_url": "",
        "tags": ["landing", "pagina-web", "diseno", "conversion"],
        "featured": True,
        "created_at": "2026-01-01T00:00:00",
        "nicho": "creativo"
    },
    {
        "id": "seed_003",
        "title": "Embudo de Ventas Automatizado",
        "description": "Embudo completo con captura de leads, secuencia de emails automatizada, integración con pasarela de pago y dashboard de conversiones.",
        "price": 2980,
        "currency": "MXN",
        "type": "bundle",
        "prompt": "Embudo de ventas automatizado multicanal",
        "style": "professional",
        "format": "html",
        "preview_url": "",
        "tags": ["embudo", "ventas", "automatizacion", "email-marketing"],
        "featured": True,
        "created_at": "2026-01-01T00:00:00",
        "nicho": "ecommerce"
    },
    {
        "id": "seed_004",
        "title": "Plan de Marketing Digital",
        "description": "Estrategia completa de marketing digital: análisis de competencia, buyer persona, calendario editorial, presupuesto y KPIs medibles.",
        "price": 1380,
        "currency": "MXN",
        "type": "bundle",
        "prompt": "Plan de marketing digital personalizado",
        "style": "professional",
        "format": "pdf",
        "preview_url": "",
        "tags": ["marketing", "estrategia", "social-media", "crecimiento"],
        "featured": True,
        "created_at": "2026-01-01T00:00:00",
        "nicho": "ecommerce"
    },
    {
        "id": "seed_005",
        "title": "Rutina de Ejercicios Personalizada",
        "description": "Plan de entrenamiento diseñado por IA según tu nivel, equipo disponible, objetivos y horario. Incluye videos demostrativos y seguimiento semanal.",
        "price": 780,
        "currency": "MXN",
        "type": "bundle",
        "prompt": "Rutina de ejercicios personalizada con IA",
        "style": "realistic",
        "format": "pdf",
        "preview_url": "",
        "tags": ["fitness", "ejercicio", "salud", "entrenamiento"],
        "featured": True,
        "created_at": "2026-01-01T00:00:00",
        "nicho": "fitness"
    },
    {
        "id": "seed_006",
        "title": "Curso de Educación Digital",
        "description": "Programa educativo completo con módulos interactivos, evaluaciones automatizadas, certificación digital y comunidad de aprendizaje.",
        "price": 1380,
        "currency": "MXN",
        "type": "bundle",
        "prompt": "Curso de educación digital con IA",
        "style": "educational",
        "format": "html",
        "preview_url": "",
        "tags": ["educacion", "curso", "e-learning", "certificacion"],
        "featured": True,
        "created_at": "2026-01-01T00:00:00",
        "nicho": "educacion"
    }
]


def _load_data():
    global products, orders
    try:
        if PRODUCTS_FILE.exists():
            with open(PRODUCTS_FILE, encoding="utf-8") as f:
                products = json.load(f)
        if ORDERS_FILE.exists():
            with open(ORDERS_FILE, encoding="utf-8") as f:
                orders = json.load(f)
    except Exception as e:
        log.warning(f"Error loading store data: {e}")
    if not products:
        _seed_products()


def _save_data():
    try:
        STORE_DIR.mkdir(parents=True, exist_ok=True)
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(orders, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log.warning(f"Error saving store data: {e}")


def _seed_products():
    global products
    for p in SEED_PRODUCTS:
        products[p["id"]] = p
    _save_data()
    log.info(f"Seeded {len(SEED_PRODUCTS)} products")


_load_data()


class Product(BaseModel):
    title: str
    description: str
    price: float
    currency: str = "MXN"
    type: str = "image"  # image, video, bundle, subscription
    prompt: str
    style: str = "realistic"
    format: str = "png"
    preview_url: str = ""
    tags: list = []


class Order(BaseModel):
    product_id: str
    customer_name: str
    email: str
    phone: str = ""
    currency: str = "MXN"  # MXN=SPEI, USDC/BTC=Crypto


class GenerateRequest(BaseModel):
    prompt: str
    style: str = "realistic"
    duration: int = 15
    format: str = "png"


# ── Product Management ────────────────────────────────────────────


@router.get("/products")
async def list_products():
    return {"products": list(products.values())}


@router.get("/featured")
async def get_featured():
    featured = [p for p in products.values() if p.get("featured", False)]
    return {"items": featured[:5]}


@router.post("/products")
async def create_product(product: Product):
    pid = str(uuid.uuid4())[:8]
    product_dict = product.model_dump()
    product_dict["id"] = pid
    product_dict["created_at"] = datetime.now().isoformat()
    product_dict["featured"] = True
    products[pid] = product_dict
    _save_data()
    log.info(f"Product created: {pid} - {product.title}")
    return {"status": "ok", "product": product_dict}


# ── Order Flow ────────────────────────────────────────────────────


@router.post("/order")
async def create_order(order: Order):
    if order.product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[order.product_id]
    oid = str(uuid.uuid4())[:8]

    order_dict = {
        "id": oid,
        "product": product,
        "customer": order.customer_name,
        "email": order.email,
        "phone": order.phone,
        "currency": order.currency,
        "amount": product["price"],
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "payment_url": "",
    }
    orders[oid] = order_dict
    _save_data()

    # Trigger n8n workflow via webhook
    try:
        import requests

        requests.post(
            "http://localhost:5679/webhook/content-order",
            json={
                "order_id": oid,
                "customer": order.customer_name,
                "email": order.email,
                "product": product,
                "price": product["price"],
                "currency": order.currency,
            },
            timeout=5,
        )
    except Exception as e:
        log.warning(f"n8n webhook trigger failed: {e}")

    return {
        "status": "pending",
        "order_id": oid,
        "product": product["title"],
        "amount": product["price"],
    }


@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order": orders[order_id]}


# ── Content Generation Endpoints (for n8n workflows) ──────────────


@router.post("/generate/content")
async def generate_content(req: GenerateRequest):
    """
    Called by n8n workflow to generate content via Fal.ai / ComfyUI.
    Returns the generated file URL.
    """
    try:
        import requests

        # Call OpenClaw fal-ai skill
        resp = requests.post(
            "http://localhost:18789/v1/fal-ai/generate",
            json={
                "prompt": req.prompt,
                "style": req.style,
                "format": "png",
                "model": "fal-ai/flux-pro/v1.1",
            },
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "status": "ok",
                "content_url": data.get("url", ""),
                "id": str(uuid.uuid4())[:8],
            }
    except Exception as e:
        log.error(f"Fal.ai generation failed: {e}")

    return {"status": "error", "error": "Content generation failed. Check Fal.ai key."}


@router.post("/generate/video")
async def generate_video(req: GenerateRequest):
    """Called by n8n workflow to generate video via Fal.ai."""
    try:
        import requests

        resp = requests.post(
            "http://localhost:18789/v1/fal-ai/generate",
            json={
                "prompt": req.prompt,
                "style": "cinematic",
                "duration": req.duration,
                "model": "fal-ai/runway-gen3/turbo",
            },
            timeout=60,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "status": "ok",
                "video_url": data.get("url", ""),
                "filename": f"video_{uuid.uuid4()[:8]}.mp4",
                "platform": "web",
            }
    except Exception as e:
        log.error(f"Video generation failed: {e}")

    return {"status": "error", "error": "Video generation failed"}


@router.post("/generate/preview")
async def generate_preview(data: dict):
    """Generate a teaser preview for social media."""
    item_id = data.get("item_id", "unknown")
    # In production: generate via fal-ai
    return {
        "status": "ok",
        "preview_url": f"/static/previews/{item_id}.jpg",
        "item_id": item_id,
    }


# ── Store Page HTML (simple landing) ──────────────────────────────

STORE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tienda JARVIS — Contenido Exclusivo</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0a0a1a; color: #e0e0e0; font-family: 'Segoe UI', system-ui, sans-serif; min-height: 100vh; }
.header { background: linear-gradient(135deg, #1a0033, #0a0a1a); padding: 40px 20px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); }
.header h1 { font-size: 2.5em; background: linear-gradient(135deg, #00d4ff, #7b2ff7, #ff6b35); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.header p { color: #888; margin-top: 8px; font-size: 1.1em; }
.products { max-width: 1200px; margin: 40px auto; padding: 0 20px; display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px; }
.card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px; transition: all 0.3s; }
.card:hover { border-color: rgba(0,212,255,0.3); transform: translateY(-4px); box-shadow: 0 8px 32px rgba(0,212,255,0.1); }
.card .price { font-size: 1.8em; font-weight: 700; color: #00d4ff; margin: 12px 0; }
.card .tags { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }
.card .tag { background: rgba(123,47,247,0.2); color: #b388ff; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; }
.card .btn { width: 100%; padding: 12px; border: none; border-radius: 8px; background: linear-gradient(135deg, #00d4ff, #7b2ff7); color: #fff; font-size: 1em; cursor: pointer; transition: all 0.3s; }
.card .btn:hover { transform: scale(1.02); filter: brightness(1.2); }
.payment-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 1000; }
.payment-modal.show { display: flex; }
.payment-modal .modal-content { background: #1a1a2e; padding: 40px; border-radius: 16px; max-width: 500px; width: 90%; }
.payment-modal h2 { margin-bottom: 20px; }
.payment-modal .option { display: flex; justify-content: space-between; align-items: center; padding: 16px; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; margin: 8px 0; cursor: pointer; transition: all 0.3s; }
.payment-modal .option:hover { border-color: #00d4ff; background: rgba(0,212,255,0.05); }
.payment-modal .option .method { font-weight: 600; }
.payment-modal .option .desc { color: #888; font-size: 0.9em; }
.payment-modal .close { margin-top: 20px; padding: 12px; width: 100%; border: none; border-radius: 8px; background: rgba(255,255,255,0.1); color: #fff; cursor: pointer; }
</style>
</head>
<body>
<div class="header">
  <h1>✨ Tienda Exclusiva</h1>
  <p>Contenido generado por IA • Pago vía SPEI • Crypto • Sin complicaciones</p>
</div>
<div class="products" id="products">
  <div style="grid-column: 1/-1; text-align: center; padding: 60px; color: #666;">
    <div style="font-size: 3em; margin-bottom: 16px;">📦</div>
    <h2>Cargando productos...</h2>
  </div>
</div>
<div class="payment-modal" id="paymentModal">
  <div class="modal-content">
    <h2>💰 Elegir método de pago</h2>
    <p id="modalProduct" style="color: #888; margin-bottom: 20px;"></p>
    <div class="option" onclick="payWith('SPEI')">
      <div>
        <div class="method">🏦 SPEI</div>
        <div class="desc">Transferencia bancaria México</div>
      </div>
      <div style="color: #4ade80;">~2 min</div>
    </div>
    <div class="option" onclick="payWith('USDC')">
      <div>
        <div class="method">₿ USDC</div>
        <div class="desc">Crypto vía Bitso</div>
      </div>
      <div style="color: #facc15;">~5 min</div>
    </div>
    <div class="option" onclick="payWith('BTC')">
      <div>
        <div class="method">₿ Bitcoin</div>
        <div class="desc">Crypto vía Bitso</div>
      </div>
      <div style="color: #f7931a;">~10 min</div>
    </div>
    <div class="option" onclick="payWith('CARD')">
      <div>
        <div class="method">💳 Tarjeta</div>
        <div class="desc">Débito/Crédito vía Mercado Pago</div>
      </div>
      <div style="color: #00d4ff;">~1 min</div>
    </div>
    <button class="close" onclick="closeModal()">Cancelar</button>
  </div>
</div>
<script>
async function loadProducts() {
  const r = await fetch('/api/store/products');
  const data = await r.json();
  const container = document.getElementById('products');
  if (data.products.length === 0) {
    container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 60px; color: #666;"><div style="font-size: 3em; margin-bottom: 16px;">🎨</div><h2>Crea tu primer producto con JARVIS</h2><p style="margin-top: 8px;">Dile a Hermes: "crea un producto nuevo"</p></div>';
    return;
  }
  container.innerHTML = data.products.map(p => `
    <div class="card">
      <h3>${p.title}</h3>
      <p style="color: #888; margin: 8px 0;">${p.description}</p>
      <div class="price">$${p.price} ${p.currency}</div>
      <div class="tags">${(p.tags||[]).map(t => '<span class="tag">#'+t+'</span>').join('')}<span class="tag">${p.type}</span></div>
      <button class="btn" onclick="openPayment('${p.id}', '${p.title}', ${p.price})">Comprar ahora</button>
    </div>
  `).join('');
}
let currentProduct = null;
function openPayment(pid, title, price) {
  currentProduct = { pid, title, price };
  document.getElementById('modalProduct').textContent = `${title} — $${price} MXN`;
  document.getElementById('paymentModal').classList.add('show');
}
function closeModal() { document.getElementById('paymentModal').classList.remove('show'); }
async function payWith(method) {
  if (!currentProduct) return;
  const r = await fetch('/api/store/order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      product_id: currentProduct.pid,
      customer_name: 'Cliente',
      email: 'cliente@email.com',
      currency: method === 'SPEI' ? 'MXN' : method
    })
  });
  const data = await r.json();
  closeModal();
  alert(`✅ Pedido creado: ${data.order_id}\n\nRecibirás instrucciones de pago por correo.`);
}
loadProducts();
</script>
</body>
</html>
"""


@router.get("/page")
async def store_page():
    from fastapi.responses import HTMLResponse

    return HTMLResponse(STORE_HTML)
