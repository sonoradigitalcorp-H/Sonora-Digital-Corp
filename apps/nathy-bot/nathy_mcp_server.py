"""
Nathy MCP Server — Skills para OpenClaw.

Expone herramientas para:
- Postear al canal de Telegram
- Enviar audio a clientes
- Consultar resumen de clientes
- Registrar clientes
- Postear actualizaciones contables automáticas

Registrar en OpenClaw: skill-creator add --url http://localhost:8765/mcp
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

sys.path.insert(0, str(Path(__file__).parent))
from nathy_bot import _load_clientes, _save_clientes, _text_to_audio, post_to_channel, send_audio_to_channel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nathy.mcp")

app = FastAPI(title="Nathy MCP Server", version="1.0.0")

TOKEN = os.environ.get("NATHY_BOT_TOKEN", "8269193231:AAF70NVpEMsrP_fePAc_qLdNEsJkBIGUy4g")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"


# ─── Schemas ──────────────────────────────────────────────

class PostRequest(BaseModel):
    text: str
    parse_mode: str = "Markdown"


class AudioRequest(BaseModel):
    text: str
    user_id: str = ""


class ClienteRequest(BaseModel):
    user_id: str
    nombre: str


class RedRequest(BaseModel):
    user_id: str
    red: str
    url: str


class FinanzasRequest(BaseModel):
    user_id: str
    ingresos_mes: float = 0
    facturas_emitidas: int = 0
    facturas_recibidas: int = 0
    isr_calculado: float = 0
    iva: float = 0
    proxima_declaracion: str = "N/A"


class SendMessageRequest(BaseModel):
    chat_id: str
    text: str
    parse_mode: str = "Markdown"


# ─── Endpoints ────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "nathy-mcp", "version": "1.0.0"}


@app.get("/tools")
async def list_tools():
    return {
        "tools": [
            {"name": "nathy/post", "description": "Postear al canal de Telegram"},
            {"name": "nathy/audio", "description": "Enviar audio al canal o a un usuario"},
            {"name": "nathy/cliente_add", "description": "Registrar un nuevo cliente"},
            {"name": "nathy/cliente_red", "description": "Agregar red social a cliente"},
            {"name": "nathy/cliente_finanzas", "description": "Actualizar finanzas de cliente"},
            {"name": "nathy/cliente_resumen", "description": "Obtener resumen de cliente"},
            {"name": "nathy/clientes_list", "description": "Listar todos los clientes"},
            {"name": "nathy/send_message", "description": "Enviar mensaje directo a un usuario de Telegram"},
            {"name": "nathy/send_audio", "description": "Enviar nota de voz a un usuario con resumen"},
        ]
    }


@app.post("/tools/nathy/post")
async def tool_post(req: PostRequest):
    ok = await post_to_channel(req.text, req.parse_mode)
    return {"success": ok, "message": "Posteado al canal" if ok else "Error"}


@app.post("/tools/nathy/audio")
async def tool_audio(req: AudioRequest):
    if req.user_id:
        ogg = _text_to_audio(req.text)
        if ogg:
            async with httpx.AsyncClient() as client:
                with open(ogg, "rb") as f:
                    await client.post(
                        f"{TELEGRAM_API}/sendVoice",
                        params={"chat_id": req.user_id},
                        files={"voice": f},
                    )
            os.unlink(ogg)
            return {"success": True, "message": "Audio enviado"}
        return {"success": False, "error": "No se pudo generar audio"}
    else:
        ok = await send_audio_to_channel(req.text)
        return {"success": ok, "message": "Audio al canal enviado" if ok else "Error"}


@app.post("/tools/nathy/cliente_add")
async def tool_cliente_add(req: ClienteRequest):
    clientes = _load_clientes()
    clientes[req.user_id] = {
        "nombre": req.nombre, "ingresos_mes": 0, "facturas_emitidas": 0,
        "facturas_recibidas": 0, "isr_calculado": 0, "iva": 0,
        "proxima_declaracion": "N/A", "redes": {},
        "ultima_actualizacion": datetime.now().isoformat()[:10],
    }
    _save_clientes(clientes)
    return {"success": True, "cliente": req.nombre}


@app.post("/tools/nathy/cliente_red")
async def tool_cliente_red(req: RedRequest):
    clientes = _load_clientes()
    if req.user_id not in clientes:
        return {"success": False, "error": "Cliente no encontrado"}
    clientes[req.user_id].setdefault("redes", {})[req.red] = req.url
    _save_clientes(clientes)
    return {"success": True, "red": req.red, "url": req.url}


@app.post("/tools/nathy/cliente_finanzas")
async def tool_cliente_finanzas(req: FinanzasRequest):
    clientes = _load_clientes()
    if req.user_id not in clientes:
        return {"success": False, "error": "Cliente no encontrado"}
    clientes[req.user_id].update({
        "ingresos_mes": req.ingresos_mes,
        "facturas_emitidas": req.facturas_emitidas,
        "facturas_recibidas": req.facturas_recibidas,
        "isr_calculado": req.isr_calculado,
        "iva": req.iva,
        "proxima_declaracion": req.proxima_declaracion,
        "ultima_actualizacion": datetime.now().isoformat()[:10],
    })
    _save_clientes(clientes)
    # Auto-postear al canal
    c = clientes[req.user_id]
    await post_to_channel(
        f"📊 *{c['nombre']}* — Finanzas actualizadas\n"
        f"Ingresos: ${req.ingresos_mes:,.2f} | "
        f"ISR: ${req.isr_calculado:,.2f} | "
        f"Próxima decl: {req.proxima_declaracion}"
    )
    return {"success": True, "message": f"Finanzas de {c['nombre']} actualizadas"}


@app.get("/tools/nathy/cliente_resumen")
async def tool_cliente_resumen(user_id: str):
    clientes = _load_clientes()
    if user_id not in clientes:
        return {"success": False, "error": "Cliente no encontrado"}
    c = clientes[user_id]
    return {"success": True, "cliente": c}


@app.get("/tools/nathy/clientes_list")
async def tool_clientes_list():
    clientes = _load_clientes()
    return {"success": True, "clientes": [
        {"id": uid, "nombre": c["nombre"], "ingresos": c.get("ingresos_mes", 0),
         "proxima_declaracion": c.get("proxima_declaracion", "N/A")}
        for uid, c in clientes.items()
    ]}


@app.post("/tools/nathy/send_message")
async def tool_send_message(req: SendMessageRequest):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": req.chat_id, "text": req.text, "parse_mode": req.parse_mode},
        )
        return {"success": r.status_code == 200}


@app.post("/tools/nathy/send_audio")
async def tool_send_audio(req: AudioRequest):
    ogg = _text_to_audio(req.text)
    if not ogg:
        return {"success": False, "error": "No se pudo generar audio"}
    async with httpx.AsyncClient() as client:
        with open(ogg, "rb") as f:
            r = await client.post(
                f"{TELEGRAM_API}/sendVoice",
                params={"chat_id": req.user_id},
                files={"voice": f},
            )
    os.unlink(ogg)
    return {"success": r.status_code == 200, "message": "Audio enviado"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("NATHY_MCP_PORT", "8765"))
    uvicorn.run(app, host="0.0.0.0", port=port)
