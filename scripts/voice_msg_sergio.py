#!/usr/bin/env python3
"""Genera y envía el mensaje de audio a Sergio D explicando el stack de voz.

Usa scripts/voice_note.py (pipeline correcto: edge-tts → resample 16k → OGG/Opus).
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.voice_note import make_voice_note  # noqa: E402

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

if __name__ == "__main__":
    print(f"Enviando audio a {TO_NUMBER}...")
    result = make_voice_note(SCRIPT, TO_NUMBER)
    if result.get("success") or result.get("data", {}).get("sent"):
        print("Audio enviado correctamente.")
    else:
        print(f"Error: {result}")
