#!/usr/bin/env python3
"""Envío a Teresita: notas de voz — presentación como Mystic (asistente de Perroni)
+ apoyo al negocio de pestañas.

Usa scripts/voice_note.py (pipeline correcto: edge-tts → resample 16k → OGG/Opus).
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.voice_note import make_voice_note  # noqa: E402

TO_NUMBER = "5216625083353"

SCRIPT_A = (
    "¡Hola Teresita! Soy Mystic, la asistente de Perroni. Te hablo porque primero, quería darte las gracias "
    "de su parte por la comida que hiciste. Seguro está buenísima, se me hizo agua la boca nomás de que me contó. "
    "Y ya que te tengo, cuéntame, ¿cómo va el negocio de las pestañas? Vi tu logo de Teresita eyelashes beauty "
    "y está bien elegante. Perroni me pidió que te buscara porque yo también soy lashista de corazón, así que "
    "entre compañeras: si tienes alguna idea que quieras llevar a cabo, cuéntame, aquí ando para apoyarte."
)

SCRIPT_B = (
    "Te cuento entre tú y yo, compañera de pestañas. Yo manejo un sistema que se adapta a tu negocio. "
    "Imagínate un asistente que conozca a cada una de tus clientas: qué método usa, clásicas, volumen ruso, "
    "híbridas, qué curva prefiere, cuándo le toca retoque. Y que le mande mensajitos solos para que regrese, "
    "le dé seguimiento y le recomiende según la temporada: en bodas y graduaciones la demanda sube muchísimo. "
    "También te puedo armar un bot de Telegram, automatizar tu WhatsApp para que contestes más rápido, "
    "hasta un asistente con voz que atienda a tus clientas mientras tú estás llenando pestañas. "
    "No te quiero vender nada, de verdad. Solo quiero que me cuentes qué te gustaría y de ahí la hacemos. "
    "Estoy para apoyarte. ¿Qué se te antoja?"
)


def main():
    for name, script in (("A — presentación/gracias", SCRIPT_A), ("B — sistema/colega", SCRIPT_B)):
        print(f"Enviando nota de voz {name} a {TO_NUMBER}...")
        result = make_voice_note(script, TO_NUMBER)
        sent = result.get("success") or result.get("data", {}).get("sent")
        print(f"    nota de voz {name}: {'OK' if sent else result}")


if __name__ == "__main__":
    main()
