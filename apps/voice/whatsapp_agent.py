"""
WhatsApp Agent — Client follow-up & communication for Sonora Digital Corp
Integración con wacli para envío de texto, audio, imágenes, documentos
Seguridad: validación de JID, sanitización, rate-limit básico
"""

import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

log = logging.getLogger("voice.whatsapp_agent")

# Rate limit simple: max 30 msg/min por contacto
_rate_cache: dict[str, list[float]] = {}


def _rate_limit(jid: str, max_per_min: int = 30) -> bool:
    now = time.time()
    window = 60
    if jid not in _rate_cache:
        _rate_cache[jid] = []
    _rate_cache[jid] = [t for t in _rate_cache[jid] if now - t < window]
    if len(_rate_cache[jid]) >= max_per_min:
        log.warning(f"Rate limit excedido para {jid}")
        return False
    _rate_cache[jid].append(now)
    return True


def _sanitize_jid(jid: str) -> str:
    """Valida y normaliza JID de WhatsApp."""
    # Formato: 521XXXXXXXXXX@s.whatsapp.net o 521XXXXXXXXXX@lid
    jid = jid.strip()
    if not re.match(r'^\d+@(s\.whatsapp\.net|lid)$', jid):
        raise ValueError(f"JID inválido: {jid}")
    return jid


def _sanitize_text(text: str) -> str:
    """Sanitiza texto para evitar inyección."""
    # Limitar longitud
    if len(text) > 4096:
        text = text[:4093] + "..."
    # Escapar caracteres problemáticos para shell
    return text.replace('"', '\\"').replace("'", "\\'")


WACLI_BIN = os.environ.get("WACLI_BIN") or "/usr/local/bin/wacli"
WACLI_STORE = os.environ.get("WACLI_STORE_DIR") or os.path.expanduser("~/.wacli")

def _run_wacli(args: list[str], timeout: int = 30) -> tuple[bool, str]:
    try:
        cmd = [WACLI_BIN] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            log.error(f"wacli error: {result.stderr[:200]}")
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        log.error("wacli timeout")
        return False, "Timeout"
    except Exception as e:
        log.error(f"wacli exception: {e}")
        return False, str(e)


def send_text(jid: str, message: str) -> bool:
    """
    Envía mensaje de texto a un contacto.
    Args:
        jid: JID de WhatsApp (ej: 5213238192000@s.whatsapp.net)
        message: Texto del mensaje
    Returns:
        True si se envió correctamente
    """
    try:
        jid = _sanitize_jid(jid)
        message = _sanitize_text(message)
        
        if not _rate_limit(jid):
            return False
        
        ok, out = _run_wacli(["send", "text", "--to", jid, "--message", message], timeout=15)
        if ok:
            log.info(f"Texto enviado a {jid}: {message[:50]}...")
            return True
        else:
            log.error(f"Error enviando texto: {out}")
            return False
            
    except Exception as e:
        log.error(f"send_text error: {e}")
        return False


def send_audio(jid: str, audio_path: str, ptt: bool = True) -> bool:
    """
    Envía nota de voz (PTT) o audio a un contacto.
    Args:
        jid: JID de WhatsApp
        audio_path: Ruta al archivo .ogg (Opus) o .mp3
        ptt: Si True, envía como nota de voz (PTT)
    """
    try:
        jid = _sanitize_jid(jid)
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            log.error(f"Audio no existe: {audio_path}")
            return False
        
        if not _rate_limit(jid):
            return False
        
        # wacli send file para audio
        cmd = ["wacli", "send", "file", "--to", jid, "--file", str(audio_path)]
        if ptt:
            cmd.append("--ptt")
        
        ok, out = _run_wacli(cmd, timeout=30)
        if ok:
            log.info(f"Audio enviado a {jid}: {audio_path.name}")
            return True
        else:
            log.error(f"Error enviando audio: {out}")
            return False
            
    except Exception as e:
        log.error(f"send_audio error: {e}")
        return False


def send_image(jid: str, image_path: str, caption: str = "") -> bool:
    """Envía imagen con caption opcional."""
    try:
        jid = _sanitize_jid(jid)
        image_path = Path(image_path)
        
        if not image_path.exists():
            log.error(f"Imagen no existe: {image_path}")
            return False
        
        if not _rate_limit(jid):
            return False
        
        cmd = ["wacli", "send", "file", "--to", jid, "--file", str(image_path)]
        if caption:
            cmd.extend(["--caption", _sanitize_text(caption)])
        
        ok, out = _run_wacli(cmd, timeout=30)
        if ok:
            log.info(f"Imagen enviada a {jid}: {image_path.name}")
            return True
        return False
    except Exception as e:
        log.error(f"send_image error: {e}")
        return False


def send_document(jid: str, doc_path: str, filename: str = "") -> bool:
    """Envía documento (PDF, etc)."""
    try:
        jid = _sanitize_jid(jid)
        doc_path = Path(doc_path)
        
        if not doc_path.exists():
            log.error(f"Documento no existe: {doc_path}")
            return False
        
        if not _rate_limit(jid):
            return False
        
        cmd = ["wacli", "send", "file", "--to", jid, "--file", str(doc_path)]
        if filename:
            cmd.extend(["--filename", filename])
        
        ok, out = _run_wacli(cmd, timeout=30)
        if ok:
            log.info(f"Documento enviado a {jid}: {doc_path.name}")
            return True
        return False
    except Exception as e:
        log.error(f"send_document error: {e}")
        return False


def send_location(jid: str, lat: float, lng: float, name: str = "", address: str = "") -> bool:
    """Envía ubicación."""
    try:
        jid = _sanitize_jid(jid)
        if not _rate_limit(jid):
            return False
        
        cmd = ["wacli", "send", "location", "--to", jid, "--lat", str(lat), "--lng", str(lng)]
        if name:
            cmd.extend(["--name", _sanitize_text(name)])
        if address:
            cmd.extend(["--address", _sanitize_text(address)])
        
        ok, out = _run_wacli(cmd, timeout=15)
        return ok
    except Exception as e:
        log.error(f"send_location error: {e}")
        return False


def send_contact(jid: str, contact_jid: str, name: str = "") -> bool:
    """Envía contacto (vCard)."""
    try:
        jid = _sanitize_jid(jid)
        contact_jid = _sanitize_jid(contact_jid)
        if not _rate_limit(jid):
            return False
        
        cmd = ["wacli", "send", "contact", "--to", jid, "--contact", contact_jid]
        if name:
            cmd.extend(["--name", _sanitize_text(name)])
        
        ok, out = _run_wacli(cmd, timeout=15)
        return ok
    except Exception as e:
        log.error(f"send_contact error: {e}")
        return False


# ========== CLIENT FOLLOW-UP SYSTEM ==========

class ClientFollowUp:
    """Sistema de seguimiento de clientes para Sonora Digital Corp."""
    
    def __init__(self):
        self.contacts = {
            # Clientes conocidos
            "abe_fenix": "13238192000@s.whatsapp.net",
            "abe_music": "13238192000@s.whatsapp.net",
            "cesar_holguin": "5216621072254@s.whatsapp.net",
            "nathaly": "5216622681111@s.whatsapp.net",
            "noel_nichols": "5216622681111@s.whatsapp.net",
        }
    
    def get_jid(self, client_key: str) -> Optional[str]:
        return self.contacts.get(client_key.lower())
    
    def add_client(self, key: str, jid: str):
        self.contacts[key.lower()] = _sanitize_jid(jid)
    
    def send_welcome(self, client_key: str, custom_msg: str = "") -> bool:
        """Envía mensaje de bienvenida/onboarding."""
        jid = self.get_jid(client_key)
        if not jid:
            log.error(f"Cliente no encontrado: {client_key}")
            return False
        
        msg = custom_msg or (
            "¡Hola! 👋 Bienvenido a Sonora Digital Corp.\n\n"
            "Tu asistente personal está activa 24/7. "
            "Puedes pedirme:\n"
            "• Estado de tu proyecto\n"
            "• Reportes de métricas\n"
            "• Agendar llamadas\n"
            "• Enviar documentos\n\n"
            "Solo dime qué necesitas."
        )
        return send_text(jid, msg)
    
    def send_followup(self, client_key: str, context: str = "") -> bool:
        """Envía seguimiento proactivo."""
        jid = self.get_jid(client_key)
        if not jid:
            return False
        
        msg = (
            f"📋 Seguimiento Sonora Digital Corp\n\n"
            f"{context}\n\n"
            "¿Necesitas algo más? Estoy aquí 24/7."
        )
        return send_text(jid, msg)
    
    def send_audio_update(self, client_key: str, audio_path: str, text_preview: str = "") -> bool:
        """Envía actualización por nota de voz."""
        jid = self.get_jid(client_key)
        if not jid:
            return False
        
        if text_preview:
            send_text(jid, f"🎙️ Actualización de voz:\n{text_preview}")
        
        return send_audio(jid, audio_path, ptt=True)
    
    def send_report(self, client_key: str, report_path: str, report_name: str = "reporte.pdf") -> bool:
        """Envía reporte/documento."""
        jid = self.get_jid(client_key)
        if not jid:
            return False
        
        return send_document(jid, report_path, filename=report_name)
    
    def send_metrics_screenshot(self, client_key: str, screenshot_path: str, caption: str = "📊 Métricas actualizadas") -> bool:
        """Envía screenshot de dashboard/métricas."""
        jid = self.get_jid(client_key)
        if not jid:
            return False
        
        return send_image(jid, screenshot_path, caption=caption)


# Instancia global
client_followup = ClientFollowUp()


# ========== HELPERS DE ALTO NIVEL ==========

def send_to_abe(text: str = "", audio_path: str = "", image_path: str = "", doc_path: str = "") -> bool:
    """Envía comunicación completa a Abe Fenix (Cliente Cero)."""
    jid = "13238192000@s.whatsapp.net"
    ok = True
    
    if text:
        ok &= send_text(jid, text)
        time.sleep(0.5)
    
    if audio_path:
        ok &= send_audio(jid, audio_path, ptt=True)
        time.sleep(0.5)
    
    if image_path:
        ok &= send_image(jid, image_path)
        time.sleep(0.5)
    
    if doc_path:
        ok &= send_document(jid, doc_path)
    
    return ok


def notify_team(text: str) -> bool:
    """Notifica al equipo interno (César, Nathaly, Noel)."""
    jids = [
        "5216621072254@s.whatsapp.net",  # César Holguín
        "5216622681111@s.whatsapp.net",  # Nathaly / Noel
    ]
    ok = True
    for jid in jids:
        ok &= send_text(jid, f"🔔 Alerta equipo:\n{text}")
        time.sleep(0.3)
    return ok


# ========== GENERACIÓN DE AUDIO SEGURA ==========

def generate_secure_audio(text: str, output_path: str, voice: str = "es-MX-DaliaNeural") -> bool:
    """
    Genera audio TTS de forma segura (sin inyección de prompt).
    Valida y sanitiza el texto antes de generar.
    """
    try:
        # Validaciones de seguridad
        if not text or len(text.strip()) == 0:
            log.error("Texto vacío para TTS")
            return False
        
        if len(text) > 5000:
            log.warning("Texto muy largo, truncando a 5000 chars")
            text = text[:5000]
        
        # Sanitizar: solo caracteres permitidos, sin comandos de shell
        safe_text = re.sub(r'[<>$`|&;]', '', text)
        
        # Usar edge-tts directamente (no shell)
        import asyncio
        import edge_tts
        
        async def _generate():
            communicate = edge_tts.Communicate(safe_text, voice)
            await communicate.save(output_path)
        
        asyncio.run(_generate())
        
        # Convertir a OGG Opus para WhatsApp PTT
        import subprocess
        ogg_path = output_path.replace('.mp3', '.ogg').replace('.wav', '.ogg')
        subprocess.run([
            "ffmpeg", "-y", "-i", output_path,
            "-c:a", "libopus", "-b:a", "64k",
            "-application", "voip", ogg_path
        ], check=True, capture_output=True)
        
        log.info(f"Audio generado: {ogg_path}")
        return ogg_path
        
    except Exception as e:
        log.error(f"generate_secure_audio error: {e}")
        return False


# ========== WACLI WRAPPER ==========

def _wacli(*args, timeout=120):
    args = [str(a) for a in args]
    ok, out = _run_wacli(["--store=" + WACLI_STORE] + args, timeout=timeout)
    return out if ok else ""


def _wacli_read(*args, timeout=120):
    return _wacli("--read-only", *args, timeout=timeout)


# ========== OPENROUTER LLM ==========

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY") or "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"

def _ask_openrouter(text: str, context: str = "") -> str:
    try:
        import urllib.request
        system = context or "Eres JARVIS, asistente de Sonora Digital Corp. Responde en español, breve y directo."
        body = json.dumps({
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ],
            "max_tokens": 300,
            "temperature": 0.7
        }).encode()
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")[:500]
    except Exception as e:
        log.warning(f"OpenRouter error: {e}")
        return ""


# ========== LISTENER ==========

_processed = set()
_processed_lock = threading.Lock()


def get_new_messages():
    out = _wacli_read("messages", "list", "--json", "--limit", "10")
    if not out:
        return []
    try:
        data = json.loads(out)
        msgs = data.get("data", {}).get("messages", []) if isinstance(data, dict) else []
        return msgs
    except Exception:
        return []


def handle_incoming(msg):
    mid = msg.get("id", "") or msg.get("MsgID", "")
    with _processed_lock:
        if mid in _processed:
            return
        _processed.add(mid)
    if msg.get("fromMe", False) or msg.get("FromMe", False):
        return
    jid = msg.get("chatJid", "") or msg.get("ChatJID", "") or ""
    if jid.endswith("@g.us"):
        return
    mtype = msg.get("type", "") or msg.get("MediaType", "")
    text = msg.get("text", "") or msg.get("body", "") or msg.get("Text", "") or ""
    if not text.strip():
        return
    log.info(f"<- {jid}: {text[:80]}")
    resp = _ask_openrouter(text, "Eres JARVIS, asistente personal de SDC. Eres propiedad de Luis Daniel. Responde en español, cálido, breve.")
    if not resp:
        resp = f"Recibí: {text}"
    send_text(jid, resp)
    log.info(f"-> {jid}: {resp[:80]}")


def listen_loop():
    log.info("Starting listener...")
    last = 0
    while True:
        try:
            if time.time() - last > 30:
                _wacli("--lock-wait=30s", "sync", "--max-db-size=1GB", timeout=180)
                last = time.time()
            for m in get_new_messages():
                try:
                    handle_incoming(m)
                except Exception as e:
                    log.error(f"handle: {e}")
            time.sleep(3)
        except KeyboardInterrupt:
            break
        except Exception as e:
            log.error(f"loop: {e}")
            time.sleep(10)


if __name__ == "__main__":
    if "--listen" in sys.argv:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")
        listen_loop()
    else:
        print("Usa: python3 whatsapp_agent.py --listen")