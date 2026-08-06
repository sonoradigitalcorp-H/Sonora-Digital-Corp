#!/usr/bin/env python3
"""Canal Automation — AstroTech by César Holguín.

Publica contenido automatizado en el canal de Telegram de Aztrotech.
Tipos de contenido rotativos para que no parezca robot:
  - Consejos de IA/automatización (educativo)
  - Caso de éxito del día (social proof)
  - Encuesta interactiva (engagement)
  - Detrás de cámaras / reflexión de César (humano)
  - Anuncio de servicio (venta suave)

Uso:
  python3 scripts/channel_automation.py --channel-id <CHANNEL_ID> --bot-token <TOKEN>
"""

import asyncio
import json
import os
import random
import sys
from datetime import datetime, time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "AZTROTECH_BOT_TOKEN")
CHANNEL_ID = os.getenv("AZTROTECH_CHANNEL_ID", "")

CONTENT_POOL = {
    "educational": [
        "💡 ¿Sabías que el 73% de los negocios que automatizan su atención al cliente ven un aumento del 30% en ventas? El Empleado Digital de AstroTech hace exactamente eso.",
        "🔧 La diferencia entre un chatbot básico y un sistema de IA que realmente vende: uno responde preguntas, el otro entiende intención, clasifica leads y conecta con César en el momento exacto.",
        "📊 Un CRM sin agentes IA es como una tienda sin vendedores. Dejas dinero en la mesa cada vez que un cliente potencial no te contacta a tiempo.",
        "🤖 La IA no reemplaza a César. La IA hace el trabajo pesado (atender, calificar, nutrir) para que César se concentre en cerrar.",
        "🎯 ¿Tu negocio pierde clientes por no contestar a tiempo? Un Empleado Digital atiende 24/7 y solo te avisa cuando hay alguien real interesado.",
    ],
    "social_proof": [
        "🏪 Un restaurante en Culiacán automatizó sus pedidos por WhatsApp con AstroTech. Resultado: 40% más pedidos sin contratar a nadie extra.",
        "🦷 Una clínica dental en Mazatlán reduceó las citas no confirmadas en un 60% con nuestro sistema de recordatorios automáticos.",
        "📦 Una tienda de ropa en Hermosillo pasó de perder 30% de sus ventas por no contestar a cerrar 3 contratos en un mes con el Sistema de Ventas Autónomo.",
    ],
    "poll": [
        "🗳️ Encuesta rápida: ¿Qué es lo que más te cuesta en tu negocio hoy?\n\n1️⃣ Conseguir clientes nuevos\n2️⃣ Contestar a tiempo\n3️⃣ Seguir el seguimiento\n4️⃣ Organizar la operación\n\nResponde con el número 👇",
        "🗳️ Si pudieras automatizar UNA cosa en tu negocio mañana, ¿cuál sería?\n\n1️⃣ Atención al cliente\n2️⃣ Seguimiento de leads\n3️⃣ Facturación\n4️⃣ Agenda de citas\n\nVota 👇",
    ],
    "human": [
        "🧠 Hoy estuve hablando con un cliente que llevaba 6 meses intentando automatizar su negocio solo con herramientas gratuitas. Al final, lo que más le costó no fue el dinero, sino el tiempo perdido en configurar cosas que no funcionaban bien.",
        "💬 Una frase que repito mucho: 'La tecnología buena no se nota'. El mejor sistema de automatización es el que tu cliente no sabe que existe pero funciona perfecto.",
        "📝 No vendo tecnología. Vendo tranquilidad. Que tu negocio funcione mientras tú duermes es el verdadero producto.",
        "🤝 César lleva 15 años ayudando a negocios en Hermosillo a crecer con tecnología. No somos una empresa fría. Somos personas que entienden lo que significa arrancar un negocio.",
    ],
    "soft_sell": [
        "🚀 Si tu negocio todavía no tiene un Empleado Digital que atienda 24/7, es como tener una tienda con la puerta cerrada. César puede mostrarte cómo funciona en una llamada de 15 minutos.",
        "📩 ¿Quieres ver cómo funciona el sistema de ventas autónomo con datos reales? César prepara una demo personalizada sin compromiso. Solo manda 'DEMO' por aquí.",
        "🎯 Este mes tenemos 3 spots disponibles para empresas que quieren arrancar con AstroTech. Si conoces a alguien que necesite automatizar, aquí estamos.",
    ],
}


def pick_content() -> dict:
    """Elige contenido aleatorio con distribución no-robótica."""
    # Distribución ponderada para que no siempre sea lo mismo
    weights = {
        "educational": 30,
        "social_proof": 20,
        "poll": 20,
        "human": 15,
        "soft_sell": 15,
    }
    categories = list(weights.keys())
    weights_list = list(weights.values())
    category = random.choices(categories, weights=weights_list, k=1)[0]
    text = random.choice(CONTENT_POOL[category])
    return {"category": category, "text": text}


async def post_to_channel(bot_token: str, channel_id: str, text: str):
    """Publica un mensaje en el canal de Telegram."""
    import httpx
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json={
            "chat_id": channel_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        })
        data = resp.json()
        if data.get("ok"):
            print(f"✅ Publicado: {data['result']['message_id']}")
        else:
            print(f"❌ Error: {data.get('description', 'unknown')}")


async def schedule_daily_posts(bot_token: str, channel_id: str):
    """Programa posts diarios en horarios naturales (como un humano)."""
    # Horarios que parecen humanos: 9am, 1pm, 4pm, 7pm
    schedule = [
        (9, 0),   # 9am - consejo del día
        (13, 0),  # 1pm - encuesta
        (16, 0),  # 4pm - caso de éxito
        (19, 0),  # 7pm - reflexión humana
    ]

    while True:
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute

        for hour, minute in schedule:
            target_minutes = hour * 60 + minute
            # Publicar si estamos dentro de la ventana de 30 min
            if abs(current_minutes - target_minutes) <= 30:
                content = pick_content()
                print(f"[{now.strftime('%H:%M')}] {content['category']}: {content['text'][:60]}...")
                await post_to_channel(bot_token, channel_id, content["text"])
                # Esperar 1 hora antes de volver a publicar en este slot
                await asyncio.sleep(3600)

        await asyncio.sleep(300)  # Revisar cada 5 min


def main():
    parser = argparse.ArgumentParser(description="Automatización de canal AstroTech")
    parser.add_argument("--channel-id", default=CHANNEL_ID, help="ID del canal de Telegram")
    parser.add_argument("--bot-token", default=BOT_TOKEN, help="Token del bot de Telegram")
    parser.add_argument("--once", action="store_true", help="Publicar un solo post y salir")
    parser.add_argument("--schedule", action="store_true", help="Programar posts diarios")
    args = parser.parse_args()

    if not args.channel_id:
        print("❌ Necesitas definir AZTROTECH_CHANNEL_ID o pasar --channel-id")
        sys.exit(1)

    if args.once:
        content = pick_content()
        print(f"Post: [{content['category']}] {content['text']}")
        asyncio.run(post_to_channel(args.bot_token, args.channel_id, content["text"]))
    elif args.schedule:
        print(f"Programando posts diarios para canal {args.channel_id}...")
        asyncio.run(schedule_daily_posts(args.bot_token, args.channel_id))
    else:
        content = pick_content()
        print(f"Post: [{content['category']}] {content['text']}")


if __name__ == "__main__":
    main()