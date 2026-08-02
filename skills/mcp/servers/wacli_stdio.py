#!/usr/bin/env python3
"""WACLI MCP Server (stdio, FastMCP) — WhatsApp messaging via wacli.

Tools:
  whatsapp_check_status   — Estado de autenticación
  whatsapp_send_text      — Enviar mensaje de texto
  whatsapp_send_file      — Enviar archivo (PDF, imagen, audio, documento)
  whatsapp_send_voice     — Enviar nota de voz (convierte MP3 a OGG Opus)
  whatsapp_get_contacts   — Listar contactos conocidos
  whatsapp_create_wa_me_link — Generar enlace wa.me con ref/UTM
  whatsapp_create_qr      — Generar QR para enlace wa.me

Requiere: wacli instalado en ~/.local/bin/wacli y autenticado.
Cuenta: 5216623538272 (personal)
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastmcp import FastMCP

WACLI = os.path.expanduser("~/.local/bin/wacli")
STORE = os.getenv("WACLI_STORE", os.path.expanduser("~/.wacli/accounts/personal"))
PHONE = os.getenv("WACLI_PHONE", "5216623538272")

mcp = FastMCP("sdc-wacli")


def _wacli(args: list, timeout: int = 60) -> dict:
    if not os.path.exists(WACLI):
        return {"success": False, "error": "wacli not found"}
    cmd = [WACLI] + args + ["--store", STORE, "--json"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip()
        if out:
            return json.loads(out)
        return {"success": False, "error": r.stderr.strip() or "no output"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "timeout"}
    except json.JSONDecodeError:
        return {"success": False, "error": f"invalid json: {r.stdout[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _ensure_to(to: str) -> str:
    to = to.strip()
    if to.endswith("@s.whatsapp.net"):
        return to
    if to.startswith("521") and len(to) == 13:
        return f"{to}@s.whatsapp.net"
    if to.startswith("52") and len(to) == 12:
        return f"{to}@s.whatsapp.net"
    if to.startswith("662") and len(to) == 10:
        return f"521{to}@s.whatsapp.net"
    if to.startswith("66") and len(to) == 12:
        return f"{to}@s.whatsapp.net"
    if len(to) == 10:
        return f"52{to}@s.whatsapp.net"
    return f"521662{to}@s.whatsapp.net"


@mcp.tool(description="Estado de autenticación de WhatsApp (wacli)")
def whatsapp_check_status() -> str:
    result = _wacli(["auth", "status"])
    data = result.get("data", {})
    if result.get("success") and data.get("authenticated"):
        return json.dumps({"status": "authenticated", "phone": data.get("phone", PHONE)})
    return json.dumps({"status": "unauthenticated", "detail": result.get("error", "unknown")})


@mcp.tool(description="Envía un mensaje de texto por WhatsApp. to: número (ej. 6622681111 o 5216622681111)")
def whatsapp_send_text(to: str, message: str) -> str:
    to = _ensure_to(to)
    result = _wacli(["send", "text", "--message", message, "--to", to, "--post-send-wait", "3s"])
    data = result.get("data", {}) if result.get("success") else {}
    return json.dumps({
        "sent": bool(data.get("sent", False)),
        "id": data.get("id", ""),
        "to": to,
        "error": result.get("error"),
    }, ensure_ascii=False)


@mcp.tool(description="Envía un archivo por WhatsApp (PDF, imagen, audio, documento). file_path debe ser absoluto")
def whatsapp_send_file(to: str, file_path: str, caption: str = "") -> str:
    to = _ensure_to(to)
    if not os.path.exists(file_path):
        return json.dumps({"sent": False, "error": f"file not found: {file_path}"})
    args = ["send", "file", "--file", file_path, "--to", to, "--post-send-wait", "5s"]
    if caption:
        args += ["--caption", caption]
    result = _wacli(args)
    data = result.get("data", {}) if result.get("success") else {}
    return json.dumps({
        "sent": bool(data.get("sent", False)),
        "id": data.get("id", ""),
        "to": to,
        "error": result.get("error"),
    }, ensure_ascii=False)


@mcp.tool(description="Envía una nota de voz por WhatsApp (convierte MP3/audio a OGG Opus)")
def whatsapp_send_voice(to: str, file_path: str) -> str:
    to = _ensure_to(to)
    if not os.path.exists(file_path):
        return json.dumps({"sent": False, "error": f"file not found: {file_path}"})
    ext = os.path.splitext(file_path)[1].lower()
    ogg_path = file_path
    cleanup = False
    if ext != ".ogg":
        tmp = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
        ogg_path = tmp.name
        tmp.close()
        subprocess.run([
            "ffmpeg", "-y", "-i", file_path,
            "-c:a", "libopus", "-b:a", "16k", "-ar", "16000", ogg_path,
        ], capture_output=True, timeout=120)
        cleanup = True
    result = _wacli([
        "send", "file", "--file", ogg_path,
        "--mime", "audio/ogg; codecs=opus", "--ptt",
        "--to", to, "--post-send-wait", "5s",
    ])
    if cleanup and os.path.exists(ogg_path):
        os.unlink(ogg_path)
    data = result.get("data", {}) if result.get("success") else {}
    return json.dumps({
        "sent": bool(data.get("sent", False)),
        "id": data.get("id", ""),
        "to": to,
        "error": result.get("error"),
    }, ensure_ascii=False)


@mcp.tool(description="Lista contactos conocidos de WhatsApp")
def whatsapp_get_contacts() -> str:
    result = _wacli(["contacts", "list"])
    if result.get("success"):
        data = result.get("data", [])
        return json.dumps({"contacts": data, "count": len(data)}, ensure_ascii=False)
    return json.dumps({"contacts": [], "count": 0, "error": result.get("error")})


@mcp.tool(description="Genera enlace wa.me del número del sistema con ref/UTM opcionales")
def whatsapp_create_wa_me_link(text: str = "", ref_code: str = "", utm_source: str = "", utm_medium: str = "", utm_campaign: str = "") -> str:
    from urllib.parse import urlencode
    params = {}
    parts = []
    if ref_code:
        parts.append(ref_code)
    if text:
        parts.append(text)
    if parts:
        params["text"] = " | ".join(parts)
    for k, v in [("utm_source", utm_source), ("utm_medium", utm_medium), ("utm_campaign", utm_campaign)]:
        if v:
            params[k] = v
    query = urlencode(params)
    link = f"https://wa.me/{PHONE}?{query}" if query else f"https://wa.me/{PHONE}"
    return json.dumps({"link": link, "phone": PHONE, "ref_code": ref_code})


@mcp.tool(description="Genera un QR PNG para un enlace wa.me o datos arbitrarios")
def whatsapp_create_qr(data: str = "", ref_code: str = "", output_path: str = "") -> str:
    try:
        import qrcode
    except ImportError:
        return json.dumps({"created": False, "error": "qrcode not installed"})
    if not data:
        link = json.loads(whatsapp_create_wa_me_link(ref_code=ref_code))
        data = link["link"]
    if not output_path:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        output_path = tmp.name
        tmp.close()
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#111827", back_color="white")
    img.save(output_path)
    return json.dumps({"created": True, "path": output_path, "data": data})


if __name__ == "__main__":
    mcp.run(transport="stdio")
