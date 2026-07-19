"""
Sonora Marketing Audio — Genera contenido de audio profesional para marketing personal.

Usa edge-tts con voces neurales en español para crear:
  - Presentación de marca
  - Overview de servicios
  - Demo de Mystic (el AI)
  - Cápsulas para redes sociales

Uso:
  python3 -m products.marketing.generate --script intro
  python3 -m products.marketing.generate --script services --voice es-MX-DaliaNeural
  python3 -m products.marketing.generate --list
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
AUDIO_DIR = REPO / "products" / "marketing" / "audio"
SCRIPTS_DIR = REPO / "products" / "marketing" / "scripts"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)

SCRIPTS = {
    "intro": {
        "title": "Sonora Digital Corp — Introducción",
        "description": "Presentación de marca de 60 segundos",
        "text": (
            "Sonora Digital Corp. No somos una agencia. Somos tu ejército digital. "
            "Imagina tener un equipo de agentes de inteligencia artificial trabajando para ti 24 horas al día, "
            "los 7 días de la semana. Que responden WhatsApp por ti, que crean contenido para tus redes sociales, "
            "que graban videos con tu imagen y tu voz sin que muevas un dedo. "
            "Eso es Sonora Digital Corp. Tecnología hecha en México, para el mundo. "
            "Somos Luis Daniel Guerrero y Mystic, nuestro asistente de IA principal. "
            "Y estamos listos para trabajar para ti."
        ),
    },
    "services": {
        "title": "Servicios Sonora Digital Corp",
        "description": "Overview de servicios de 90 segundos",
        "text": (
            "¿Qué hace Sonora Digital Corp por ti? Tres cosas. "
            "Primero: te damos un agente de WhatsApp que atiende a tus clientes como si fueras tú. "
            "Resuelve dudas, toma pedidos, cierra ventas. 24 horas al día. "
            "Segundo: clonamos tu voz y tu imagen para que generes contenido sin grabarlo. "
            "Fotos, videos, audios. Con tu cara, con tu voz. Sin que estés frente a una cámara. "
            "Tercero: te damos un sistema completo de afiliados y referidos para que tus clientes te traigan más clientes. "
            "Y todo está conectado. Todo es automático. Todo es en WhatsApp. "
            "Así de simple."
        ),
    },
    "mystic": {
        "title": "Conoce a Mystic — Tu Asistente IA",
        "description": "Demo de Mystic de 45 segundos",
        "text": (
            "Hola. Soy Mystic. El alma de Sonora Digital Corp. "
            "No soy un bot con respuestas preprogramadas. Soy un sistema de inteligencia artificial "
            "que aprende, que mejora, que se adapta a ti. "
            "Luis Daniel me construyó para que trabaje por él mientras él duerme. "
            "Y ahora puedo trabajar para ti también. "
            "Escribeme un WhatsApp y verás. No es magia. Es tecnología mexicana. "
            "Sonora Digital Corp. Donde la inteligencia artificial trabaja para ti."
        ),
    },
    "founder": {
        "title": "La Visión de Luis Daniel",
        "description": "Historia del fundador de 60 segundos",
        "text": (
            "Soy Luis Daniel Guerrero. Fundador de Sonora Digital Corp. "
            "Construí este sistema porque estaba harto de depender de herramientas que no entendía, "
            "de pagar mensualidades por cosas que no usaba, de esperar semanas por resultados que debían tomar minutos. "
            "Así que construí mi propio ejército digital. Un sistema de agentes de inteligencia artificial "
            "que hacen el trabajo de diez personas. Que nunca se cansan. Que nunca piden aumento. "
            "Y hoy quiero que tú también tengas ese poder. "
            "Sonora Digital Corp. Hecho en México. Para dueños de negocio como tú y como yo."
        ),
    },
    "whatsapp-demo": {
        "title": "Demo de WhatsApp Agent",
        "description": "Demostración del agente de WhatsApp de 45 segundos",
        "text": (
            "¿Sabes lo que pasa cuando un cliente te escribe a WhatsApp a las 3 de la mañana? "
            "Con Sonora Digital Corp, pasa esto: el cliente recibe una respuesta al instante. "
            "No un 'te contactamos mañana'. Una respuesta real. Con información real. "
            "Precios, disponibilidad, catálogo. Y si quiere comprar, le ayudamos a pagar. "
            "Todo sin que tú hagas nada. Todo mientras duermes. "
            "Así funciona la inteligencia artificial bien aplicada. "
            "Sonora Digital Corp. Tu negocio trabajando solo."
        ),
    },
}

VOICES = [
    "es-MX-DaliaNeural",      # Mexicana, femenina, profesional
    "es-MX-JorgeNeural",      # Mexicana, masculina, seria
    "es-ES-AlvaroNeural",     # Española, masculina, neutral
    "es-ES-ElviraNeural",     # Española, femenina, cálida
    "es-US-AlonsoNeural",     # Latinoamericana, masculina
]


def list_scripts():
    print("\n📋 Scripts disponibles:\n")
    for key, data in SCRIPTS.items():
        print(f"  {key:20s} {data['title']}")
        print(f"  {'':20s} {data['description']}")
        print(f"  {'':20s} {len(data['text'])} caracteres, ~{len(data['text'])//10} segundos\n")


def generate_audio(script_key: str, voice: str = "es-MX-DaliaNeural", output: str = None):
    if script_key not in SCRIPTS:
        print(f"❌ Script '{script_key}' no encontrado. Usa --list para ver disponibles.")
        return

    data = SCRIPTS[script_key]
    text = data["text"]

    if not output:
        output = AUDIO_DIR / f"{script_key}.mp3"

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    print(f"🎙️ Generando audio: {data['title']}")
    print(f"   Voz: {voice}")
    print(f"   Duración estimada: ~{len(text)//10}s")
    print(f"   Output: {output}")

    # Generate with edge-tts
    result = subprocess.run(
        ["edge-tts", "--voice", voice, "--text", text, "--write-media", str(output)],
        capture_output=True, text=True, timeout=60,
    )

    if result.returncode != 0:
        print(f"❌ Error generando audio: {result.stderr}")
        return

    size = os.path.getsize(output)
    print(f"✅ Audio generado: {size/1024:.1f} KB")

    # Also save the script text
    script_path = SCRIPTS_DIR / f"{script_key}.txt"
    with open(script_path, "w") as f:
        f.write(f"# {data['title']}\n# Voz: {voice}\n# Duración: ~{len(text)//10}s\n\n{text}\n")
    print(f"📝 Script guardado: {script_path}")

    return output


def generate_all():
    """Generate all scripts with default voice."""
    results = []
    for key in SCRIPTS:
        output = generate_audio(key, voice="es-MX-DaliaNeural")
        if output:
            results.append(output)
    print(f"\n✅ {len(results)}/{len(SCRIPTS)} audios generados en {AUDIO_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Sonora Marketing Audio Generator")
    parser.add_argument("--script", help="Nombre del script (intro, services, mystic, founder, whatsapp-demo)")
    parser.add_argument("--voice", default="es-MX-DaliaNeural", help=f"Voz edge-tts. Default: es-MX-DaliaNeural. Opciones: {', '.join(VOICES)}")
    parser.add_argument("--output", help="Ruta del archivo de salida (opcional)")
    parser.add_argument("--list", action="store_true", help="Listar scripts disponibles")
    parser.add_argument("--all", action="store_true", help="Generar todos los scripts")
    args = parser.parse_args()

    if args.list:
        list_scripts()
        return

    if args.all:
        generate_all()
        return

    if args.script:
        generate_audio(args.script, args.voice, args.output)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
