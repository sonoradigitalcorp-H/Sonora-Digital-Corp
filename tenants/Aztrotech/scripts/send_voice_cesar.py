#!/usr/bin/env python3
"""Send voice message to César via Telegram."""
import os
import sys
import subprocess
import httpx
import asyncio

# César's Telegram
CESAR_CHAT_ID = "5738935134"
NOTIF_BOT_TOKEN = os.getenv("NOTIF_BOT_TOKEN")

# Message script
MESSAGE = """
Buenas noches César, soy Luis Daniel. Te hablo porque quiero contarte algo que me tiene muy emocionado.

Mira, lo que estamos construyendo contigo es algo que va más allá de un simple bot o una página web. Piensa en el universo por un momento. En la mecánica cuántica hay un fenómeno que se llama superposición, donde una partícula puede estar en todos los estados posibles al mismo tiempo hasta que alguien la observa. 

Eso es exactamente lo que estamos haciendo con Aztrotech. Tu negocio ahora mismo está en una superposición: puede ser una empresa local en Hermosillo, o puede ser una potencia tecnológica que atiende clientes en todo el mundo. Y nosotros estamos aquí para ser los observadores que colapsen esa onda hacia la realidad que tú sueñas.

Hemos construido un sistema completo. Tu asistente virtual ya está hablando con clientes, calificando leads, agendando citas. No es un chatbot simple, es un agente con memoria, que recuerda a cada persona, que entiende el contexto, que aprende de cada conversación.

Estamos afinando los últimos detalles, personalizando los manuales, ajustando cada proceso para que cuando lo entreguemos, sea 100% Aztrotech, 100% tú.

Y aquí viene lo que me emociona más: podemos crear cualquier agente, para cualquier cliente, para cualquier idea que tengas. Si mañana alguien te dice "quiero un sistema que haga X", nosotros lo construimos. No hay límites.

Además, estamos trabajando en una fusión real entre Sonora Digital Corp y Aztrotech. No una fusión de papeles, sino de capacidades. Tú tienes la visión, nosotros la infraestructura. Juntos somos imparables.

Ahora, tengo una pregunta para ti: para los mensajes de voz que te enviemos, ¿prefieres que usemos tu voz clonada, la que ya tenemos, o prefieres otra voz para la recepcionista virtual? Podemos configurar lo que tú quieras.

César, lo que estamos construyendo es como tener un agente cuántico: está en todas partes al mismo tiempo, atendiendo, vendiendo, escalando. Tus sueños más grandes, los que a veces te parecen imposibles, están a un paso de convertirse en realidad.

Un abrazo grande, y hablamos pronto.
"""

async def generate_audio():
    """Generate audio from text using TTS."""
    output_path = "/tmp/msg_cesar.mp3"
    
    # Use edge-tts directly
    result = subprocess.run([
        "/home/mystic/.local/bin/edge-tts",
        "--voice", "es-MX-JorgeNeural",  # Male voice for Luis Daniel
        "--text", MESSAGE.strip(),
        "--write-media", output_path
    ], capture_output=True, timeout=60)
    
    if result.returncode == 0 and os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"Audio generated: {output_path} ({size} bytes)")
        return output_path
    else:
        print(f"Error: {result.stderr.decode()}")
        return None

async def send_voice(audio_path):
    """Send voice message via Telegram."""
    if not NOTIF_BOT_TOKEN:
        print("No NOTIF_BOT_TOKEN configured")
        return False
    
    url = f"https://api.telegram.org/bot{NOTIF_BOT_TOKEN}/sendVoice"
    
    with open(audio_path, "rb") as f:
        files = {"voice": ("mensaje_luis_daniel.mp3", f, "audio/mpeg")}
        data = {"chat_id": CESAR_CHAT_ID, "caption": "🎧 Mensaje de Luis Daniel para ti"}
        
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, files=files, data=data)
            print(f"Telegram response: {resp.status_code}")
            if resp.status_code == 200:
                print("Voice message sent successfully!")
                return True
            else:
                print(f"Error: {resp.text}")
                return False

async def main():
    print("Generating audio...")
    audio_path = await generate_audio()
    
    if audio_path:
        print("Sending to César via Telegram...")
        await send_voice(audio_path)
    else:
        print("Failed to generate audio")

if __name__ == "__main__":
    asyncio.run(main())
