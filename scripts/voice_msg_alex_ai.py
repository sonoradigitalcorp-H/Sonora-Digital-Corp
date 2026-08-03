#!/usr/bin/env python3
"""Envío a Alex Usa: nota de voz — qué puede hacer el asistente de Telegram
(OpenClaw + Sonora Digital Corp) para un Shift Manager de Producción en RYE.

Pipeline de audio CORRECTO en scripts/voice_note.py (edge-tts → resample 16k → OGG/Opus).
"""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.voice_note import make_voice_note  # noqa: E402

TO_NUMBER = "12059021830"

SCRIPT = (
    "Hola Alex, soy Mystic, la asistente de Perroni. Ya le estuve echando ojo a lo que hace RYE y a las "
    "líneas de ensamble que programan para BMW, Rivian, VW y Mercedes, y te tengo una propuesta concreta. "
    "Te armo un asistente por Telegram, como el mío, pero a tu medida como gerente de producción. "
    "El punto uno: al final de cada turno te genera el shift report automático — unidades producidas, paros, "
    "motivos, calidad — sin que tengas que andar pidiendo datos a media planta. "
    "Punto dos: control de personal. Retardos, ausencias, quién entró y quién no, y te avisa antes del arranque "
    "para que no te agarren las juntas sin tu gente. "
    "Punto tres: las juntas. Le mandas el audio o la nota, y te regresa la minuta con acuerdos y responsables, "
    "listo para reenviar. "
    "Punto cuatro: el dashboard de OEE en tiempo real por línea. En la industria, plantas que lo usan suben de "
    "sesenta y siete a ochenta y dos por ciento de OEE en noventa días. "
    "Punto cinco y el que más te va a interesar: detección de fallas en los robots antes de que truenen. "
    "Mantenimiento predictivo con los datos de los controladores Fanuc que ya tienen — el costo de una hora de "
    "paro en una línea automotriz va de un millón trescientos mil a dos millones trescientos mil dólares, y la IA "
    "reduce los paros no planeados hasta en un cincuenta por ciento. "
    "Punto seis: verificación proactiva de procesos. El sistema revisa las variables de la línea y te alerta "
    "cuando algo se está desviando, antes de que salga una pieza mala. "
    "Punto siete: coordinación con los fleteros y peleceros — horarios de trailers, docks, pendientes de carga y "
    "descarga, todo en el mismo chat. "
    "Y punto ocho: reportes automáticos para presentar a los clientes grandes. Con un toque te arma el resumen de "
    "producción con gráficas y datos duros para la reunión con los de BMW o Mercedes. "
    "Todo esto es lo que la industria ya está usando, no es teoría. Si te late, le comentamos a Perroni y en "
    "una semana te dejo el primer piloto con el shift report y el control de personal. Aquí andamos al tiro."
)


def main():
    print("Enviando nota de voz a Alex...")
    result = make_voice_note(SCRIPT, TO_NUMBER)
    sent = result.get("success") or result.get("data", {}).get("sent")
    print(f"    nota de voz: {'OK' if sent else result}")


if __name__ == "__main__":
    main()
