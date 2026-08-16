#!/usr/bin/env python3
"""Telegram/WhatsApp Webhook SUPERPOWERED — Hermosillo Contabilidad (@HermosilloCont_bot)

Nivel senior devops/prompt-engineer. Modelado en el sistema Aztrotech (onboarding_engine,
feedback_loop, asset_generation) adaptado para el tenant hermosillo-cont.

CAPACIDADES:
- Onboarding PROACTIVO: propone servicios, muestra beneficios + assets visuales,
  hace preguntas de calificación SIN esperar a que el cliente pida.
- Voz (DaliaNeural): confirma citas por audio al cliente (Telegram) y WhatsApp.
- WhatsApp dual: notificaciones a número de empresa (Business) y personal (jefa).
- Seguridad: rate limiting por chat, prompt injection protection, sanitización.
- Determinista: captura lead, scoring cold/warm/hot, agenda cita, escala, propone.
- Model routing: nemotron free (clasificación), edge-tts (voz), whisper (STT).
- Canal: polling (getUpdates) o webhook HTTP. 24/7 en VPS OVH.

SDD 0006 — T1.5. Regla de oro: NUNCA inventar precios, derivar a Nathaly.
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import subprocess
import tempfile
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE / "01_Core_Platform" / "05_Shared_Libraries" / "SDK_Python"))
_TENANTS_PATH = os.environ.get("HERMES_TENANTS_PATH", str(Path.home() / ".hermes" / "tenants"))
sys.path.insert(0, _TENANTS_PATH)

TOKEN = os.environ.get("TELEGRAM_HERMOSILLOCONT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"

# ─── Config jefa Nathaly ────────────────────────────────────────────
NATHALY_PHONE_PERSONAL = "6622681111"      # +526622681111 (personal de la jefa)
NATHALY_PHONE_EMPRESA = "6623498589"       # +526623498589 (WhatsApp Business)
NATHALY_CHAT_ID = os.environ.get("NATHALY_CHAT_ID", "")

WACLI_STORE_PERSONAL = str(Path.home() / ".config/wacli")                    # sesión de Luis
WACLI_STORE_EMPRESA = str(Path.home() / ".config/wacli/nathaly_business")    # sesión Nathaly Biz

# ─── Imports locales ────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lead_classifier_hermosillo import classify_intent_hermosillo  # noqa: E402
from onboarding_hermosillo import OnboardingHermosillo, get_paquetes, formato_paquetes  # noqa: E402

# RAG KB (knowledge_store.json local — embeddings VPS OVH all-minilm)
from seeder_rag_hermosillo import get_rag_context  # noqa: E402
from assets_hermosillo import get_asset  # noqa: E402
from security_hermosillo import (  # noqa: E402
    rate_limited, sanitize_for_llm, handle_trivial_command, is_ignorable_command,
)
from tenant_router import init_registry  # noqa: E402

DB_PATH = Path(os.environ.get("HERMOSILLO_DB_PATH",
    str(BASE / "01_Core_Platform" / "03_Agentic_Infrastructure" / "Databases" / "leads_hermosillo_cont.db")))
ENGINE = OnboardingHermosillo(str(DB_PATH))

# ─── Voz ─────────────────────────────────────────────────────────────
EDGE_TTS_VOICE = "es-MX-DaliaNeural"
EDGE_TTS_RATE = "+4%"      # ágil, rápida, natural (cliente pidió que no sea lenta)
EDGE_TTS_PITCH = "+2Hz"    # suavidad sutil

_ASSETS_DIR = Path(os.environ.get("HERMOSILLO_ASSETS_DIR", str(Path(__file__).resolve().parent / "assets")))
_ASSETS_DIR.mkdir(exist_ok=True)

# =====================================================================
# TELEGRAM API
# =====================================================================

def tg(method: str, payload: dict) -> dict:
    import requests
    try:
        r = requests.post(f"{API}/{method}", json=payload, timeout=25)
        return r.json() if r.status_code == 200 else {"ok": False, "error": r.text[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def tg_send_text(chat_id, text):
    for part in [text[i:i + 4000] for i in range(0, len(text), 4000)]:
        tg("sendMessage", {"chat_id": chat_id, "text": part})


def tg_send_voice(chat_id: str, text: str) -> bool:
    """edge-tts (DaliaNeural) → ffmpeg → OGG → Telegram sendVoice."""
    try:
        import asyncio, requests, edge_tts
        fd, ogg_path = tempfile.mkstemp(suffix=".ogg")
        os.close(fd)
        mp3_path = ogg_path.replace(".ogg", ".mp3")

        async def _gen():
            c = edge_tts.Communicate(text, EDGE_TTS_VOICE, rate=EDGE_TTS_RATE, pitch=EDGE_TTS_PITCH)
            await c.save(mp3_path)
        asyncio.run(_gen())

        r = subprocess.run(["ffmpeg", "-y", "-i", mp3_path, "-c:a", "libopus", "-b:a", "24k", ogg_path],
                           capture_output=True, timeout=30)
        if r.returncode != 0:
            return False
        with open(ogg_path, "rb") as f:
            resp = requests.post(f"{API}/sendVoice", files={"voice": ("v.ogg", f, "audio/ogg")},
                                 data={"chat_id": chat_id}, timeout=30)
        ok = resp.status_code == 200 and resp.json().get("ok", False)
        for p in (mp3_path, ogg_path):
            try:
                os.unlink(p)
            except OSError:
                pass
        return ok
    except Exception as e:
        print(f"[TTS] {e}")
        return False


def tg_send_photo(chat_id: str, photo_path: str, caption: str) -> bool:
    import requests
    try:
        with open(photo_path, "rb") as f:
            resp = requests.post(f"{API}/sendPhoto",
                                 files={"photo": ("a.jpg", f, "image/jpeg")},
                                 data={"chat_id": chat_id, "caption": caption[:1000]}, timeout=30)
        return resp.status_code == 200 and resp.json().get("ok", False)
    except Exception as e:
        return False


def tg_download(file_id: str):
    r = tg("getFile", {"file_id": file_id})
    if not r.get("ok"):
        return None
    fp = r["result"]["file_path"]
    url = f"https://api.telegram.org/file/bot{TOKEN}/{fp}"
    import requests
    try:
        resp = requests.get(url, timeout=30)
        suffix = Path(fp).suffix or ".ogg"
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        with open(path, "wb") as f:
            f.write(resp.content)
        return path
    except Exception:
        return None


def tg_stt(audio_path: str) -> str:
    """STT con whisper local. Retorna '' si falla."""
    try:
        result = subprocess.run(
            ["whisper", audio_path, "--model", "tiny", "--language", "es",
             "--output_format", "txt", "--output_dir", "/tmp"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            txts = list(Path("/tmp").glob(f"{Path(audio_path).stem}.txt"))
            if txts:
                return txts[0].read_text().strip()
    except Exception as e:
        print(f"[STT] {e}")
    return ""


def tts_to_ogg(text: str) -> bytes | None:
    """edge-tts (DaliaNeural) → MP3 bytes (navegador lo reproduce). Retorna None si falla."""
    try:
        import asyncio, edge_tts
        fd, mp3 = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        async def _g():
            c = edge_tts.Communicate(text, EDGE_TTS_VOICE, rate=EDGE_TTS_RATE, pitch=EDGE_TTS_PITCH)
            await c.save(mp3)
        asyncio.run(_g())
        data = Path(mp3).read_bytes()
        try:
            os.unlink(mp3)
        except OSError:
            pass
        return data
    except Exception as e:
        print(f"[TTS_MP3] {e}")
        return None


# =====================================================================
# WACLI (WhatsApp)
# =====================================================================

def wa_text(to_phone: str, text: str, store: str = WACLI_STORE_EMPRESA) -> bool:
    try:
        r = subprocess.run(
            ["/home/mystic/.local/bin/wacli", "send", "text",
             "--store", store, "--to", f"+{to_phone}", "--message", text],
            capture_output=True, text=True, timeout=30)
        return r.returncode == 0 and "sent" in r.stdout.lower()
    except Exception as e:
        print(f"[WA_TEXT] {e}")
        return False


def wa_voice(to_phone: str, text: str, store: str = WACLI_STORE_EMPRESA) -> bool:
    """Nota de voz WhatsApp: edge-tts → ffmpeg → wacli send voice."""
    try:
        import asyncio, edge_tts
        fd, ogg_path = tempfile.mkstemp(suffix=".ogg")
        os.close(fd)
        mp3_path = ogg_path.replace(".ogg", ".mp3")

        async def _g():
            c = edge_tts.Communicate(text, EDGE_TTS_VOICE, rate=EDGE_TTS_RATE, pitch=EDGE_TTS_PITCH)
            await c.save(mp3_path)
        asyncio.run(_g())

        r = subprocess.run(["ffmpeg", "-y", "-i", mp3_path, "-c:a", "libopus", "-b:a", "24k", ogg_path],
                           capture_output=True, timeout=30)
        if r.returncode != 0:
            return False
        result = subprocess.run(
            ["/home/mystic/.local/bin/wacli", "send", "voice", "--store", store,
             "--to", f"+{to_phone}", "--file", ogg_path],
            capture_output=True, text=True, timeout=60)
        ok = result.returncode == 0
        for p in (mp3_path, ogg_path):
            try:
                os.unlink(p)
            except OSError:
                pass
        return ok
    except Exception as e:
        print(f"[WA_VOICE] {e}")
        return False


# =====================================================================
# NOTIFICACIONES A LA JEFA (Nathaly) — doble canal
# =====================================================================

def notify_jefa(evento: str, texto: str, critico: bool = False, con_voz: bool = False, ambos_siempre: bool = False):
    """Notifica a Nathaly (jefa): Business + Personal con texto y opcional voz.

    - siempre_siempre=True → AMBOS números SIEMPRE (leads).
    - critico=True → AMBOS + voz.
    - default (critico=False, siempre_siempre=False) → solo Business texto.
    """
    if con_voz:
        wa_voice(NATHALY_PHONE_EMPRESA, f"{evento}. {texto[:180]}", store=WACLI_STORE_EMPRESA)
    body = f"🔔 *{evento}*\n{texto}" if critico else f"📎 {evento}\n{texto}"
    # Business (empresa)
    wa_text(NATHALY_PHONE_EMPRESA, body, store=WACLI_STORE_EMPRESA)
    # Personal: si crítico o ambos_siempre o con_voz
    if critico or ambos_siempre or con_voz:
        if con_voz:
            wa_voice(NATHALY_PHONE_PERSONAL, f"{evento}. {texto[:180]}", store=WACLI_STORE_EMPRESA)
        wa_text(NATHALY_PHONE_PERSONAL, f"🚨 {evento}\n{texto}" if critico else f"📎 {evento}\n{texto}",
                store=WACLI_STORE_EMPRESA)
    if NATHALY_CHAT_ID:
        tg("sendMessage", {"chat_id": NATHALY_CHAT_ID, "text": f"🔔 {evento}\n{texto}"})


def notify_lead_audio(tel_cliente: str, texto: str):
    """Confirmación por voz al cliente (número que dio en el lead)."""
    wa_voice(tel_cliente, texto, store=WACLI_STORE_EMPRESA)


# =====================================================================
# ASSETS (imágenes de beneficio por servicio)
# =====================================================================

def show_asset(chat_id: str, servicio: str) -> bool:
    """Envía foto asset del servicio (si existe local) + texto beneficio."""
    asset = get_asset(servicio)
    if not asset:
        return False
    img = _ASSETS_DIR / f"{asset['id']}.jpg"
    if img.exists():
        return tg_send_photo(chat_id, str(img), asset["beneficio"])
    return False


# =====================================================================
# PIPELINE PRINCIPAL
# =====================================================================

def limpiar_salida(texto: str) -> str:
    """Limpia la respuesta para el cliente: SIN emojis, asteriscos, signos de
    admiración ni markdown. Voz + texto consistente y profesional."""
    if not texto:
        return texto
    import re
    # Quitar emojis (unicode pictographs/símbolos)
    texto = re.sub(
        r"[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF"
        r"\U00002190-\U000021FF\U00002B00-\U00002BFF\U0000FE0F\U00002700-\U000027BF]",
        "", texto)
    # Quitar asteriscos y markdown
    texto = re.sub(r"[*_`#>|~]", "", texto)
    # Quitar signos de admiración e interrogación de cierre excesivo (!!/??) → punto
    texto = re.sub(r"[!¡]{2,}", ".", texto)
    texto = re.sub(r"[?¿]{2,}", ".", texto)
    texto = texto.replace("!", "").replace("¡", "").replace("?", "").replace("¿", "")
    # Normalizar espacios múltiples y espacios antes de puntuación
    texto = re.sub(r"\s+", " ", texto).strip()
    texto = re.sub(r"\s+([.,;:])", r"\1", texto)
    # Asegurar terminación en punto si es frase
    if texto and texto[-1] not in ".:;":
        texto += "."
    return texto


def responde_paquetes() -> str:
    """Devuelve el texto de los 3 paquetes (limpio, sin markdown/emojis)."""
    return limpiar_salida(formato_paquetes())


def saludo_personalizado(chat_id: str, fallback: str) -> str:
    """Si conocemos el nombre del chat, anteponerlo; si no, saludo default."""
    nombre = ENGINE.get_nombre(str(chat_id))
    if not nombre:
        return fallback
    return f"¡Hola {nombre}! 😊 " + fallback.lower()


def enviar_visual_beneficio(chat_id: str):
    """Envía la imagen 'así te beneficiarás' (celular asistente + dashboard)."""
    try:
        imgs = [_ASSETS_DIR / "vision_celular_asistente.jpg", _ASSETS_DIR / "vision_dashboard.jpg"]
        cap = ("💡 Mira cómo se vería tu negocio con nosotros: un asistente IA respondiendo "
               "24/7 a tus clientes y un dashboard claro de tu contabilidad. "
               "Tú recuperas horas cada mes. ¿Te gustaría verlo en una demo de 15 min?")
        if imgs[0].exists():
            tg_send_photo(chat_id, str(imgs[0]), cap)
        elif imgs[1].exists():
            tg_send_photo(chat_id, str(imgs[1]), cap)
        else:
            pass
    except Exception as e:
        print(f"[VISUAL] {e}")


def process_text(chat_id: str, text: str, is_jefa: bool) -> dict:
    """Texto completo: sanitiza → historial → comando/trivial → clasifica con memoria → acción."""
    from security_hermosillo import sanitize_input

    # Registrar mensaje del usuario (conversación real)
    ENGINE.registrar_conversacion(str(chat_id), "user", text)

    text = sanitize_input(text)

    # 0. Comando trivial (sin LLM)
    trivial = handle_trivial_command(text)
    if trivial:
        if is_jefa:
            tg_send_voice(chat_id, trivial)
        else:
            tg_send_text(chat_id, trivial)
        return {"ok": True, "tipo": "trivial"}

    if is_ignorable_command(text):
        return {"ok": True, "tipo": "ignored"}

    # 0b. Detección de paquetes / promociones / planes (determinista, sin LLM)
    low = text.lower()
    if any(k in low for k in ("paquete", "plan", "paquete", "promoc", "cuáles son", "cuales son", "cuánto cobran", "cuanto cobran", "costos", "precios", "tarifas")):
        # Registrar interés de paquetes como intención
        ENGINE.registrar_conversacion(str(chat_id), "bot", "[mostró paquetes]", "")
        paq = responde_paquetes()
        if is_jefa:
            tg_send_voice(chat_id, paq)
        else:
            tg_send_text(chat_id, paq)
        return {"ok": True, "tipo": "paquetes", "texto": paq}

    # 1. Seguridad: prompt injection
    clean, atacado = sanitize_for_llm(text)
    if atacado:
        tg_send_text(chat_id, clean)
        return {"ok": True, "tipo": "security"}

    # 1.5 Historial real de la conversación → contexto LLM (multi-turno)
    historial = ENGINE.historial_chat(str(chat_id), limit=10)
    contexto = [{"rol": m["rol"], "texto": m["texto"][:200]} for m in historial if m.get("texto") and m["texto"] != "…"]

    # 1.6 RAG: recuperar data verificada SAT/servicios relevante al mensaje
    rag_ctx = ""
    try:
        rag_ctx = get_rag_context(clean, top=2)
    except Exception as e:
        print(f"[RAG] {e}")

    # 2. Clasificar intención (nemotron free + fallback deepseek) CON historial + RAG
    cls = classify_intent_hermosillo("hermosillo-cont", clean, context=contexto, okf_context=rag_ctx)
    print(f"[AI] {cls.intencion} conf={cls.confianza} accion={cls.accion_requerida}")

    action = cls.accion_requerida
    campos = cls.campos or {}
    reply = cls.respuesta_sugerida

    # 3. Acciones deterministas
    if action == "capture":
        r = ENGINE.registrar_lead(str(chat_id), campos)
        nombre_det = campos.get("nombre")
        if nombre_det:
            ENGINE.guardar_nombre(str(chat_id), nombre_det)
        servicio = campos.get("servicio")
        # Proactivo: proponer servicio detectado → asset + pregunta
        if servicio and get_asset(servicio):
            show_asset(chat_id, servicio)
            asset = get_asset(servicio)
            reply = f"{asset['beneficio']}\n\n{asset['pregunta']}"
        else:
            reply = (f"{reply}\n\n💡 Podemos ayudarte con: contabilidad, administración, "
                     f"importaciones, marketing y trámites SAT. ¿Cuál te interesa más?")
        # VISIÓN: si ya hay negocio, ofrecer "así se vería con nosotros"
        negocio = campos.get("negocio") or ""
        if negocio:
            try:
                vision_img = _ASSETS_DIR / "vision_celular_asistente.jpg"
                if vision_img.exists():
                    tg_send_photo(chat_id, str(vision_img),
                                  "📊 Así se vería la atención a tu negocio con nosotros: un asistente IA respondiendo 24/7 y dashboard claro. Más horas para ti cada mes. ¿Te gustaría una demo de 15 min?")
                else:
                    enviar_visual_beneficio(chat_id)
            except Exception:
                enviar_visual_beneficio(chat_id)
        # Notificar a la jefa: lead capturado → AMBOS números + audio
        notify_jefa("🟢 NUEVO LEAD", f"{nombre_det or 'Sin nombre'} 🏢 {negocio or ''} — {servicio or 'general'}\n{reply[:180]}",
                    con_voz=True, ambos_siempre=True)
        state[chat_id] = "onboarding"  # estado: siguiente turno captura más datos

    elif action == "schedule":
        r = ENGINE.agendar_cita(str(chat_id), campos.get("fecha", ""), campos.get("hora", ""))
        if r.get("ok"):
            reply = f"¡Cita agendada para el {r.get('fecha')} a las {r.get('hora')}! Te confirmamos. 📅"
            # Confirmación por voz al cliente si dejó teléfono
            tel = campos.get("telefono") or campos.get("whatsapp") or ""
            if tel:
                notify_lead_audio(tel, f"Confirmamos tu cita el {r.get('fecha')} a las {r.get('hora')} con Hermosillo Contabilidad.")
            else:
                try:
                    tg_send_voice(chat_id, reply)
                except Exception:
                    pass
            notify_jefa("📅 Cita agendada", f"{r.get('fecha')} {r.get('hora')} — chat {chat_id}", critico=True)
        else:
            reply = f"Lo siento, {r.get('error','no pude agendar')}. ¿Quieres otra fecha u hora?"

    elif action == "escalar":
        notify_jefa("🚨 ESCALACIÓN", f"Chat {chat_id}: \"{clean[:200]}\"", critico=True)
        reply = "Te paso con Nathaly directamente, en un momento te contacta. 🙌"

    elif action == "precio":
        ENGINE.registrar_lead(str(chat_id), campos)
        reply = ("El costo exacto te lo da Nathaly en una llamada o WhatsApp. "
                 "¿Te agendo una consulta rápida? El diagnóstico inicial es gratis.")

    # 4. Responder (voz si jefa, texto si lead) — con nombre si es saludo
    if cls.intencion == "saludo":
        reply = saludo_personalizado(chat_id, reply)
    reply = limpiar_salida(reply)  # sin emojis/*/!
    if is_jefa:
        tg_send_voice(chat_id, reply)
    else:
        tg_send_text(chat_id, reply)

    # Registrar respuesta del bot (conversación real)
    ENGINE.registrar_conversacion(str(chat_id), "bot", reply)

    return {"ok": True, "res": cls.intencion, "accion": action, "respuesta": reply}


# Estado de conversación por chat (onboarding paso a paso)
import threading
_state_lock = threading.Lock()
state: dict = {}


def handle_update(update: dict) -> dict:
    message = update.get("message") or update.get("edited_message") or {}
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    if not chat_id:
        return {"ok": False, "reason": "sin chat"}

    is_jefa = bool(NATHALY_CHAT_ID) and str(chat_id) == str(NATHALY_CHAT_ID)

    # Anti-spam
    rl_ok, rl_msg = rate_limited(chat_id)
    if not rl_ok:
        tg_send_text(chat_id, rl_msg)
        return {"ok": False, "reason": "rate_limited"}

    # Texto
    if message.get("text", "").strip():
        return process_text(chat_id, message["text"], is_jefa)

    # Voz → STT → texto
    voz = message.get("voice") or message.get("audio")
    if voz:
        path = tg_download(voz["file_id"])
        if not path:
            tg_send_text(chat_id, "No pude descargar tu audio. Intenta de nuevo.")
            return {"ok": False, "reason": "download"}
        texto = tg_stt(path)
        try:
            os.unlink(path)
        except OSError:
            pass
        if texto:
            return process_text(chat_id, texto, is_jefa)
        tg_send_text(chat_id, "🎙️ Recibí tu voz. Por ahora no logré transcribirla. ¿Me lo escribes?")
        return {"ok": True, "tipo": "voz_no_transcrita"}

    # Foto
    if message.get("photo"):
        tg_send_text(chat_id, "📷 Recibida tu foto. ¿Qué documento o factura quieres que revise?")
        return {"ok": True, "tipo": "foto"}

    tg_send_text(chat_id, "🤖 Entiendo texto, voz y fotos. ¿Cómo te ayudo con tus finanzas?")
    return {"ok": False, "reason": "unsupported"}


def chat_json(text: str, chat_sid: str = "") -> dict:
    """Endpoint del orbe: procesa mensaje SIN enviar a Telegram, devuelve respuesta JSON."""
    from security_hermosillo import sanitize_input
    text = sanitize_input(text)
    if not text:
        return {"ok": False, "error": "empty"}
    # sesión para memoria web (por IP o sid)
    sid = chat_sid or "web-" + str(int(time.time() * 1000))
    # Registrar mensaje usuario web
    ENGINE.registrar_conversacion(sid, "user", text, canal="web")
    # Comando trivial
    trivial = handle_trivial_command(text)
    if trivial:
        ENGINE.registrar_conversacion(sid, "bot", trivial, canal="web")
        return {"ok": True, "respuesta": trivial, "tipo": "trivial", "sid": sid}
    if is_ignorable_command(text):
        return {"ok": True, "respuesta": "", "tipo": "ignored", "sid": sid}

    # Paquetes / promociones (web)
    low = (text or "").lower()
    if any(k in low for k in ("paquete", "plan", "promoc", "cuáles son", "cuales son", "costos", "precios", "tarifas", "cuánto cobran", "cuanto cobran")):
        paq = responde_paquetes()
        ENGINE.registrar_conversacion(sid, "bot", paq, canal="web")
        return {"ok": True, "respuesta": paq, "tipo": "paquetes", "sid": sid}

    # Seguridad
    clean, atacado = sanitize_for_llm(text)
    if atacado:
        return {"ok": False, "error": "seguridad", "respuesta": clean, "sid": sid}
    # Historial real web → contexto
    historial = ENGINE.historial_chat(sid, limit=8)
    contexto = [{"rol": m["rol"], "texto": m["texto"][:200]} for m in historial if m.get("texto")]
    # RAG web
    rag_ctx = ""
    try:
        rag_ctx = get_rag_context(clean, top=2)
    except Exception as e:
        print(f"[RAG] {e}")
    # Clasificar con historial + RAG
    cls = classify_intent_hermosillo("hermosillo-cont", clean, context=contexto, okf_context=rag_ctx)
    action = cls.accion_requerida
    campos = cls.campos or {}
    reply = cls.respuesta_sugerida
    if cls.intencion == "saludo" and not action == "capture":
        nombre_web = ENGINE.get_nombre(sid)
        if nombre_web:
            reply = f"¡Hola {nombre_web}! 😊 Bienvenido de vuelta a Hermosillo Contabilidad. ¿En qué te ayudo hoy?"
    if action == "capture":
        r = ENGINE.registrar_lead(sid, campos, canal="web")
        nombre_det = campos.get("nombre")
        if nombre_det:
            ENGINE.guardar_nombre(sid, nombre_det, canal="web")
        servicio = campos.get("servicio")
        if servicio and get_asset(servicio):
            asset = get_asset(servicio)
            reply = f"{asset['beneficio']}\n\n{asset['pregunta']}"
        else:
            reply = f"{reply}\n\n💡 Podemos ayudarte con: contabilidad, administración, importaciones, marketing y trámites SAT. ¿Cuál te interesa más?"
        # Visión: "así se vería tu contabilidad con nosotros"
        negocio = campos.get("negocio") or ""
        if negocio:
            reply += "\n\n📊 *Así se vería tu negocio con nosotros:*\n" + \
                     "• Asistente IA respondiendo 24/7 a tus clientes (en tu celular)\n• Dashboard claro de tu contabilidad\n• Más horas para ti cada mes (libertad de tiempo)\n" + \
                     "🖼️ https://sonoradigitalcorp.com/hermosillo_assets/vision_celular_asistente.jpg\n" + \
                     "¿Te gustaría agendar una demo de 15 min?"
        notify_jefa("🟢 NUEVO LEAD (web)", f"{nombre_det or 'Sin nombre'} 🏢 {negocio or ''} — {servicio or 'general'}", con_voz=True, ambos_siempre=True)
    elif action == "schedule":
        r = ENGINE.agendar_cita(sid, campos.get("fecha", ""), campos.get("hora", ""))
        reply = (f"¡Cita agendada para {r.get('fecha')} {r.get('hora')}! 📅" if r.get("ok")
                 else f"Lo siento, {r.get('error','no pude agendar')}. ¿Otra fecha?")
        notify_jefa("📅 Cita (web)", f"{r.get('fecha')} {r.get('hora')}", critico=True)
    elif action == "escalar":
        notify_jefa("🚨 ESCALACIÓN (web)", f"\"{clean[:150]}\"", critico=True)
        reply = "Te paso con Nathaly, en un momento te contacta. 🙌"
    elif action == "precio":
        ENGINE.registrar_lead(sid, campos, canal="web")
        reply = "El costo exacto te lo da Nathaly en WhatsApp. ¿Te agendo una consulta gratis?"
    # Registrar respuesta bot web
    ENGINE.registrar_conversacion(sid, "bot", reply, canal="web")
    reply = limpiar_salida(reply)
    return {"ok": True, "respuesta": reply, "intencion": cls.intencion, "accion": action, "sid": sid}

class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[WEB] {datetime.utcnow().isoformat()} {fmt % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        # Webhook de Telegram: POST /webhook/<bot_token>
        if self.path.startswith("/webhook/"):
            try:
                length = int(self.headers.get("Content-Length", 0))
                update = json.loads(self.rfile.read(length).decode())
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 400)
                return
            result = handle_update(update)
            self.send_json(result)
            return
        # API del orbe: POST /chat  body={"text": "..."}
        if self.path == "/chat":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length).decode())
                text = body.get("text", "")
                sid = body.get("sid", "")
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 400)
                return
            result = chat_json(text, chat_sid=sid)
            self.send_json(result)
            return
        self.send_json({"ok": False, "error": "not found"}, 404)

    def do_GET(self):
        if self.path == "/health":
            self.send_json({"status": "ok", "tenant": "hermosillo-cont", "bot": "@HermosilloCont_bot"})
        elif self.path.startswith("/chat/audio?text="):
            # Voz: texto → DaliaNeural MP3 → byte stream (para el orbe hablado)
            from urllib.parse import unquote, urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            text = qs.get("text", [""])[0][:400]
            mp3 = tts_to_ogg(text)
            if mp3:
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(len(mp3)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(mp3)
            else:
                self.send_json({"ok": False, "error": "tts"}, 500)
        else:
            self.send_json({"ok": False, "error": "not found"}, 404)


def run_webhook(port: int):
    init_registry()
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    print(f"[WEBHOOK] escuchando :{port}")
    server.serve_forever()


# =====================================================================
# POLLING (fallback sin URL pública)
# =====================================================================

def run_polling():
    init_registry()
    print("[POLL] @HermosilloCont_bot polling...")
    offset = 0
    while True:
        try:
            import requests
            r = requests.get(f"{API}/getUpdates",
                             params={"timeout": 25, "offset": offset,
                                     "allowed_updates": '["message"]'}, timeout=35)
            data = r.json()
            for upd in data.get("result", []):
                offset = upd["update_id"] + 1
                handle_update(upd)
        except KeyboardInterrupt:
            print("\n[POLL] stop.")
            break
        except Exception as e:
            print(f"[POLL] error: {e}")
            time.sleep(3)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Webhook Hermosillo Cont SUPERPOWERED")
    ap.add_argument("--port", type=int, default=5291)
    ap.add_argument("--poll", action="store_true", help="modo polling")
    args = ap.parse_args()
    if args.poll:
        run_polling()
    else:
        run_webhook(args.port)