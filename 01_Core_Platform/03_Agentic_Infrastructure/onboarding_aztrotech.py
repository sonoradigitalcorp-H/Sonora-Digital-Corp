#!/usr/bin/env python3
"""onboarding_aztrotech.py — Onboarding de Aztrotech (bot @Aztro_tech_bot).

TEXTO por defecto (rápido, cero espera). VOZ solo si el usuario la pide
(edge-tts es-MX-DaliaNeural, rápida y ligera — NO F5-TTS, no tarda).

Flujo:
  1. Bienvenida (texto) con ejemplos de Aztrotech + web aztrotech.mx
  2. Confirmar cita (fecha/hora)
  3. Avisar a César por WhatsApp con el lead + audio de abordaje

Uso:
    python3 onboarding_aztrotech.py --chat 5738935134              # texto bienvenida
    python3 onboarding_aztrotech.py --chat ... --voz --bienvenida  # edita con voz DaliaNeutral
    python3 onboarding_aztrotech.py --voz --text "Hola" --chat ...
"""
import argparse, os, subprocess, sys
from pathlib import Path

import requests

BOT = "aztroc"
TELE = Path.home() / ".openclaw" / "secrets" / "telegram-aztroc.token"
CHAT_CESAR = "6621072254"
CHAT = "5738935134"
VOICE_REPLY = Path(__file__).parent / "voice_reply.py"
VOICE = VOICE_REPLY

HDR = (
    "Hola, gracias por escribir a AZTROTECH. 👋 Soy el asistente virtual de ventas. "
    "Te cuento rápido qué hacemos y, si quieres, agendamos una cita sin compromiso."
)
OBJETIVO = (
    "En Aztrotech te ayudamos a automatizar tu atención y ventas con IA "
    "pensada para negocios. 💙 Más información en nuestra web: " + AZTROWEB if (AZTROWEB := "https://aztrotech.mx") else ""
    "Si gustas, dime qué día y a qué hora te acomodo una cita."
)
VIDEO = "También te comparto una nota de voz/video para que veas de qué va." if False else "¿Te mando el video de qué hace? Pídemelo y te lo paso. 📲"


def send_text(text: str, chat: str):
    token = TELE.read_text().strip()
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat, "text": text}, timeout=60)
    d = r.json()
    print(f"[TXT {'OK' if d.get('ok') else 'FAIL'}] {chat}: {text[:60]}...")
    return d.get("ok")


def send_voice(text: str, chat: str):
    r = subprocess.run([sys.executable, str(VOICE), "--bot", BOT, "--chat", chat,
                        "--text", text, "--voice", "es-MX-DaliaNeural"],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chat", default=CHAT)
    ap.add_argument("--text", help="texto a enviar (default hdr)")
    ap.add_argument("--voz", action="store_true", help="enviar como voz DaliaNeutral")
    ap.add_argument("--bienvenida", action="store_true", help="guion: hdr + objetivo + web")
    ap.add_argument("--notificar", action="store_true")
    ap.add_argument("--lead", default="", dest="lead")
    ap.add_argument("--empresa", default="")
    ap.add_argument("--servicio", default="")
    ap.add_argument("--fecha", default="")
    ap.add_argument("--hora", default="")
    a = ap.parse_args()

    def emit(text):
        (send_voice if a.voz else send_text)(text, a.chat)

    if a.text:
        emit(a.text)
    elif a.bienvenida:
        emit(HDR)
        emit(OBJETIVO)
    else:
        emit(HDR)

    if a.notificar:
        resumen = (
            f"📋 Nuevo lead de Aztrotech: {a.lead} ({a.empresa}). "
            f"Servicio: {a.servicio}. Cita: {a.fecha} {a.hora}. "
            "Abordar por beneficios: ROI, ahorro, seguimiento 24/7."
        )
        print("RESUMEN A CESAR:", resumen)
        send_text(resumen, CHAT)

    print("LISTO")


if __name__ == "__main__":
    main()