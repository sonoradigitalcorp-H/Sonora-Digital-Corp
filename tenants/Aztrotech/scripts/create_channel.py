#!/usr/bin/env python3
"""Crear canal de Telegram para César Holguín (CEO de Aztrotech)."""
import argparse, asyncio, os, sys
sys.path.insert(0, os.path.dirname(__file__))

async def create_channel(api_id, api_hash, channel_name, channel_title, channel_description):
    from telethon import TelegramClient
    session_name = f"channel_creator_{channel_name}"
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()
    me = await client.get_me()
    print(f"Sesión iniciada como: {me.first_name} (@{me.username})")
    channel = await client.create_channel(
        title=channel_title,
        about=channel_description,
        megagroup=False,
    )
    print(f"Canal creado: {channel.title} (id: {channel.id}, username: @{channel.username})")
    BOT_USERNAME = "AztroTechBot"
    try:
        await client.edit_permissions(channel, BOT_USERNAME,
            post_messages=True, edit_messages=True, delete_messages=True,
            pin_messages=True, invite_users=True)
        print(f"Bot @{BOT_USERNAME} añadido como admin del canal")
    except Exception as e:
        print(f"No se pudo añadir el bot automáticamente: {e}")
        print("Añádelo manualmente como administrador con permisos de postear.")
    print("\nPróximos pasos:")
    print("1. Añade el bot @AztroTechBot como admin del canal")
    print("2. Configura el webhook del bot para el canal")
    print("3. Usa scripts/channel_automation.py para contenido automatizado")
    await client.disconnect()

def main():
    parser = argparse.ArgumentParser(description="Crear canal de Telegram para AstroTech")
    parser.add_argument("--api-id", type=int, required=True)
    parser.add_argument("--api-hash", required=True)
    parser.add_argument("--channel-name", default="aztrotech-oficial")
    parser.add_argument("--channel-title", default="AstroTech by César Holguín")
    parser.add_argument("--channel-description", default="Canal oficial de AstroTech. IA, automatización y tecnología para tu negocio.")
    args = parser.parse_args()
    asyncio.run(create_channel(args.api_id, args.api_hash, args.channel_name, args.channel_title, args.channel_description))

if __name__ == "__main__":
    main()
