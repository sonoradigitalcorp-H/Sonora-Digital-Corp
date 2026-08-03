#!/usr/bin/env python3
"""
Lead Responder — Respuesta automática a leads que escriben a la línea de negocio (5216623538272).

Flujo:
  - Escucha mensajes entrantes (no del fundador).
  - Clasifica el lead como COLD / WARM / HOT con un LLM.
  - Envía alerta por Telegram al bot personal de Sonora Digital Corp.
  - NO contesta la pregunta: responde SIEMPRE en audio avisando que enseguida se comunica,
    da el link de la página y cierra amable. (Regla: nunca contesto contenido, solo aviso.)
  - Registra el costo estimado (LLM + TTS) de cada respuesta de audio para monitoreo.

Regla de oro de seguridad: NO se envía NADA a números que no estén en ALLOWED,
salvo la respuesta a un lead que acaba de escribir (que se confirma contra la cola
de mensajes entrantes reales). El fundador siempre queda exento del bucle.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

# ─── Constantes ─────────────────────────────────────────────
WACLI = os.environ.get("WACLI_PATH") or os.path.expanduser("~/.local/bin/wacli")
if not os.path.exists(WACLI):
    WACLI = "/usr/local/bin/wacli"
STORE = os.environ.get("WACLI_STORE") or os.path.expanduser("~/.wacli/accounts/personal")

BUSINESS_LINE = "5216623538272"          # La línea donde escriben los leads
FOUNDER_PHONE = "5216623538272"          # El dueño (no se le responde automáticamente)

SITE_LINK = os.environ.get("SDC_SITE_LINK", "https://sonoradigitalcorp.com")

SEEN_PATH = REPO / "state" / "whatsapp" / "lead_responded.json"
COST_LOG = REPO / "state" / "whatsapp" / "lead_costs.jsonl"
LEADS_LOG = REPO / "state" / "whatsapp" / "leads.jsonl"
EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
LLM_MODEL = os.environ.get("SDC_LEAD_LLM", "deepseek/deepseek-v4-flash")

# Credenciales Telegram para alertas
TELEGRAM_TOKEN = os.environ.get("ABE_TELEGRAM_TOKEN", "")
TELEGRAM_CHAT = os.environ.get("ABE_TELEGRAM_CHAT", "")

# Costos unitarios (USD aprox, ajustables vía env)
COST_PER_LLM_1K_IN = float(os.environ.get("SDC_COST_LLM_IN", "0.001"))
COST_PER_LLM_1K_OUT = float(os.environ.get("SDC_COST_LLM_OUT", "0.002"))
COST_TTS_PER_CHAR = float(os.environ.get("SDC_COST_TTS_CHAR", "0.000004"))


def _load_env():
    """Cargar infra/.env.backup si existe (sin sobreescribir vars ya presentes)."""
    global TELEGRAM_TOKEN, TELEGRAM_CHAT, OPENROUTER_KEY
    envf = REPO / "infra" / ".env.backup"
    if envf.exists():
        for line in envf.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k in ("ABE_TELEGRAM_TOKEN", "ABE_TELEGRAM_CHAT", "OPENROUTER_API_KEY", "SONORA_BOT_TOKEN", "SDC_SITE_LINK"):
                    os.environ.setdefault(k, v)
    TELEGRAM_TOKEN = os.environ.get("ABE_TELEGRAM_TOKEN", TELEGRAM_TOKEN)
    TELEGRAM_CHAT = os.environ.get("ABE_TELEGRAM_CHAT", TELEGRAM_CHAT)
    OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", OPENROUTER_KEY)


def _wacli(args: list, timeout: int = 30) -> dict:
    if not os.path.exists(WACLI):
        return {"success": False, "error": "wacli not found"}
    cmd = [WACLI] + args + ["--store", STORE, "--json", "--read-only"]
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


def _load_seen() -> set:
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not SEEN_PATH.exists():
        return set()
    try:
        with open(SEEN_PATH) as f:
            return set(json.load(f).get("ids", []))
    except Exception:
        return set()


def _save_seen(seen: set) -> None:
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_PATH, "w") as f:
        json.dump({"ids": sorted(seen), "updated": datetime.now(timezone.utc).isoformat()}, f)


def _log_jsonl(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _emit_event(event: str, payload: dict) -> None:
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {"event": event, "timestamp": datetime.now(timezone.utc).isoformat(), "payload": payload}
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _send_telegram(text: str) -> bool:
    """Enviar alerta al bot personal de Sonora Digital Corp."""
    token = os.environ.get("ABE_TELEGRAM_TOKEN", TELEGRAM_TOKEN)
    chat = os.environ.get("ABE_TELEGRAM_CHAT", TELEGRAM_CHAT)
    if not token or not chat:
        return False
    try:
        data = urllib.parse.urlencode({"chat_id": chat, "text": text, "parse_mode": "Markdown"})
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data.encode(), method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


def _classify_lead(text: str, name: str = "") -> str:
    """Clasificar lead: cold / warm / hot."""
    key = os.environ.get("OPENROUTER_API_KEY", OPENROUTER_KEY)
    if not key:
        return "warm"
    system = (
        "Clasifica el siguiente mensaje de WhatsApp de un posible cliente de una agencia digital "
        "(Sonora Digital Corp) en una sola etiqueta: HOT, WARM o COLD. "
        "HOT = intención clara de comprar, presupuesto, listo para contratar, pregunta por precio/planes hoy. "
        "WARM = interés real pero más genérico, quiere saber servicios, aún explorando. "
        "COLD = saludo, curiosidad, o sin intención de compra. "
        "Responde SOLO con una palabra: HOT, WARM o COLD."
    )
    try:
        import httpx
        body = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": f"Mensaje de {name or 'un contacto'}: {text[:800]}"},
            ],
            "max_tokens": 5,
            "temperature": 0,
        }
        r = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=body, timeout=15)
        content = r.json()["choices"][0]["message"]["content"].strip().upper()
        for label in ("HOT", "WARM", "COLD"):
            if label in content:
                return label
    except Exception:
        pass
    return "warm"


def _llm_cost_est(in_chars: int, out_chars: int) -> float:
    in_toks = in_chars / 4
    out_toks = out_chars / 4
    return (in_toks / 1000) * COST_PER_LLM_1K_IN + (out_toks / 1000) * COST_PER_LLM_1K_OUT


def _tts_cost_est(chars: int) -> float:
    return chars * COST_TTS_PER_CHAR


def _make_audio(text: str) -> str:
    """Generar nota de voz OGG/Opus desde texto con edge-tts + conversión."""
    mp3_path = None
    try:
        edge = shutil.which("edge-tts") or os.path.expanduser("~/.local/bin/edge-tts")
        mp3_path = f"/tmp/sdc_lead_{int(time.time())}.mp3"
        subprocess.run([edge, "--voice", "es-MX-DaliaNeural", "--text", text[:1500],
                        "--write-media", mp3_path], capture_output=True, timeout=40)

        ogg_path = mp3_path.replace(".mp3", ".ogg")
        # Generar OGG/Opus con pyav (ffmpeg del sistema puede estar roto)
        _mp3_to_ogg_opus(mp3_path, ogg_path)
        if os.path.exists(ogg_path) and os.path.getsize(ogg_path) > 500:
            return ogg_path
    except Exception:
        pass
    finally:
        try:
            if mp3_path:
                os.unlink(mp3_path)
        except OSError:
            pass
    return ""


def _mp3_to_ogg_opus(src: str, dst: str) -> None:
    import av
    import numpy as np
    import librosa

    in_c = av.open(src)
    in_s = in_c.streams.audio[0]
    orig_rate = in_s.rate or 24000

    # Decodificar todo a un arreglo mono
    chunks = []
    for frame in in_c.decode(in_s):
        arr = frame.to_ndarray()
        if arr.ndim > 1:
            arr = arr.mean(axis=0)
        chunks.append(arr.astype("float32"))
    in_c.close()
    audio = np.concatenate(chunks) if len(chunks) > 1 else chunks[0]

    # Resamplear a 16k mono (evita duplicar muestras)
    mono = librosa.resample(audio, orig_sr=orig_rate, target_sr=16000)

    # Encodear a OGG/Opus
    out_c = av.open(dst, "w")
    out_s = out_c.add_stream("libopus", rate=16000)
    out_s.layout = "mono"
    out_s.bit_rate = 16000

    frame_size = 16000 * 2  # 2s por frame (libopus maneja el remuestreo interno)
    pts = 0
    for start in range(0, len(mono), frame_size):
        seg = mono[start:start + frame_size]
        if len(seg) == 0:
            continue
        frm = av.AudioFrame.from_ndarray(
            np.ascontiguousarray(seg).reshape(1, -1), format="flt", layout="mono")
        frm.sample_rate = 16000
        frm.pts = pts
        pts += len(seg)
        for p in out_s.encode(frm):
            out_c.mux(p)
    for p in out_s.encode(None):
        out_c.mux(p)
    out_c.close()


def _send_voice(to: str, text: str) -> dict:
    """Enviar nota de voz. Regresa costo estimado del TTS."""
    to_jid = to if "@s.whatsapp.net" in to else f"{to}@s.whatsapp.net"
    ogg = _make_audio(text)
    if not ogg:
        return {"success": False, "error": "audio gen failed"}
    try:
        cmd = [WACLI, "send", "voice", "--file", ogg, "--to", to_jid,
               "--post-send-wait", "5s", "--store", STORE, "--json"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        out = r.stdout.strip()
        result = json.loads(out) if out else {"success": False, "error": r.stderr.strip() or "no output"}
        result["cost_tts"] = _tts_cost_est(len(text))
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        try:
            os.unlink(ogg)
        except OSError:
            pass


def _responder_script(name: str = "") -> str:
    """El guion de audio que SIEMPRE se manda al contacto (nunca contesta el contenido)."""
    if name:
        greeting = f"Hola {name},"
    else:
        greeting = "Hola,"
    return (
        f"{greeting} recibí tu mensaje, en un momento me comunico contigo. "
        "Si es urgente, llámame. ¡Un abrazo!"
    )


def _process(msg: dict, seen: set) -> bool:
    msg_id = msg.get("MsgID") or msg.get("id") or msg.get("message_id")
    if not msg_id or msg_id in seen:
        return False
    seen.add(msg_id)

    raw_sender = msg.get("SenderJID") or msg.get("sender") or ""
    # Solo DMs persona-a-persona (ignorar grupos/newsletters)
    if "@s.whatsapp.net" not in raw_sender:
        return False

    sender = raw_sender.split("@")[0]
    if sender == FOUNDER_PHONE or (FOUNDER_PHONE and FOUNDER_PHONE in str(msg.get("FromMe", "").lower())):
        return False  # nunca responder al fundador

    text = (msg.get("Text") or msg.get("DisplayText") or msg.get("text") or "").strip()
    # Ignorar medios sin texto (sticker, imagen, audio recibido)
    if not text or text.lower().startswith("sent "):
        return False
    name = msg.get("SenderName") or msg.get("chat_name") or ""

    # 1. Clasificar lead
    label = _classify_lead(text, name)

    # 2. Log del lead
    _log_jsonl(LEADS_LOG, {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "from": sender, "name": name, "text": text[:300], "label": label,
    })

    # 3. Alerta Telegram al bot personal
    emoji = {"HOT": "🔥", "WARM": "🌤️", "COLD": "🧊"}.get(label, "🔵")
    alert = (
        f"{emoji} *Lead {label}* — Sonora Digital Corp\n"
        f"*Tel:* +{sender}\n"
        f"*Nombre:* {name or '—'}\n"
        f"*Mensaje:* {text[:300]}\n"
        f"_Te están hablando, responde pronto._"
    )
    ok_tg = _send_telegram(alert)
    _emit_event("lead:detected", {"from": sender, "name": name, "label": label, "telegram_sent": ok_tg})

    # 4. Responder SOLO con audio (no contesta el contenido)
    script = _responder_script(name)
    result = _send_voice(sender, script)
    sent = bool(result.get("success") or result.get("data", {}).get("sent", False))
    # costo del LLM de clasificación + TTS
    llm_cost = _llm_cost_est(len(text), 5)
    tts_cost = result.get("cost_tts", 0.0)
    total_cost = llm_cost + tts_cost

    _log_jsonl(COST_LOG, {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message_id": msg_id, "from": sender, "label": label,
        "llm_cost_usd": round(llm_cost, 6), "tts_cost_usd": round(tts_cost, 6),
        "total_cost_usd": round(total_cost, 6), "voice_sent": sent,
    })
    print(f"[lead-responder] {sender} '{text[:40]}' → {label} | voz={sent} | costo=${total_cost:.4f}", flush=True)
    return True


def run(interval: int = 3, limit: int = 50, once: bool = False) -> None:
    print(f"[lead-responder] Iniciado, intervalo={interval}s, línea={BUSINESS_LINE}", flush=True)
    seen = _load_seen()
    while True:
        result = _wacli(["messages", "list", "--from-them", "--limit", str(limit)])
        if result.get("success"):
            data = result.get("data", [])
            msgs = data if isinstance(data, list) else data.get("messages", []) if isinstance(data, dict) else []
            new_count = 0
            for m in msgs:
                if _process(m, seen):
                    new_count += 1
            if new_count:
                _save_seen(seen)
                print(f"[lead-responder] {new_count} leads atendidos", flush=True)
        if once:
            break
        time.sleep(interval)


def main():
    _load_env()
    p = argparse.ArgumentParser()
    p.add_argument("--interval", type=int, default=3)
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--once", action="store_true")
    a = p.parse_args()
    run(interval=a.interval, limit=a.limit, once=a.once)


if __name__ == "__main__":
    main()
