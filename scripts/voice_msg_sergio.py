#!/usr/bin/env python3
"""Genera y envía el mensaje de audio a Sergio D explicando el stack de voz."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

WACLI = os.environ.get("WACLI_PATH") or os.path.expanduser("~/.local/bin/wacli")
STORE = os.environ.get("WACLI_STORE") or os.path.expanduser("~/.wacli/accounts/personal")

TO_NUMBER = "5216624707325"

SCRIPT = (
    "Hola Sergio, soy Mystic, la asistente personal de Perroni. "
    "Te hablo para explicarte rápido el stack open-source para agentes de voz que tenemos en Sonora Digital Corp. "
    "Usamos Whisper de OpenAI para convertir audio a texto, se corre completamente local. "
    "Para texto a voz usamos Edge TTS con la voz de Dalia en español mexicano, es gratis y suena muy natural. "
    "También tenemos OpenVoice V2 para clonación de voz, zero-shot, funciona local y es open-source. "
    "El pipeline completo es: detección de wake word con openWakeWord, "
    "actividad de voz con Energy-VAD, transcripción con Whisper, "
    "procesamiento con LLM local vía Ollama o en la nube con OpenRouter, "
    "y respuesta de voz con Edge TTS. "
    "Para llamadas telefónicas tenemos un orquestador en Go que se integra con FreeSWITCH. "
    "Todo el stack cuesta alrededor de 17 dólares al mes mantenerlo. "
    "En cuanto al sistema de planeación, usamos Spec-Driven Development. "
    "El flujo es: primero declaras la constitución del proyecto con speckit.constitution, "
    "luego especificas la feature con speckit.specify, "
    "después clarificas ambigüedades, generas el plan, lo analizas, "
    "desglosas en tareas, implementas y finalmente verificas con pruebas automatizadas. "
    "El planner del kernel descompone misiones en tareas y las rutea al agente correcto según capacidades. "
    "¿Te gusta? Te paso la documentación completa si quieres, me dices."
)

def send_voice(to: str, text: str) -> dict:
    to = to if "@s.whatsapp.net" in to else f"{to}@s.whatsapp.net"
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, mode="wb")
        mp3_path = tmp.name
        tmp.close()

        subprocess.run([
            "edge-tts", "--voice", "es-MX-DaliaNeural",
            "--text", text,
            "--write-media", mp3_path,
        ], capture_output=True, timeout=60)

        ogg_path = mp3_path.replace(".mp3", ".ogg")
        subprocess.run([
            "ffmpeg", "-y", "-i", mp3_path,
            "-c:a", "libopus", "-b:a", "16k", "-ar", "16000", ogg_path
        ], capture_output=True, timeout=60)

        cmd = [WACLI, "send", "file", "--file", ogg_path,
               "--mime", "audio/ogg; codecs=opus", "--ptt",
               "--to", to, "--post-send-wait", "5s",
               "--store", STORE, "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        out = result.stdout.strip()
        data = json.loads(out) if out else {"success": False, "error": "no output"}

        os.unlink(mp3_path)
        os.unlink(ogg_path)
        return data
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print(f"Enviando audio a {TO_NUMBER}...")
    result = send_voice(TO_NUMBER, SCRIPT)
    if result.get("success") or result.get("data", {}).get("sent"):
        print("Audio enviado correctamente.")
    else:
        print(f"Error: {result}")
