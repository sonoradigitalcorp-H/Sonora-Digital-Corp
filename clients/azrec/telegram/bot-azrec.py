#!/usr/bin/env python3
"""
AzREC Telegram Bot — Sales Assistant + Community
Based on existing Telegram bot infrastructure at jarvis/telegram_bot/
"""
import logging, json, os, sys
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

log = logging.getLogger("azrec.telegram")

# Config
TOKEN = os.getenv("AZREC_TELEGRAM_TOKEN", "")  # Set this!
SHOPIFY_URL = "https://sonoradigitalcorp.com/azrec"
GROUP_ID = os.getenv("AZREC_GROUP_ID", "")  # For community group

# Products catalog (sync with Shopify)
PRODUCTS = {
    "gorra_classic": {
        "name": "Gorra AzREC Classic",
        "price": "$399 MXN",
        "desc": "Clasica negra con logo bordado. Algodon 100%, ajustable.",
        "url": "https://sonoradigitalcorp.com/azrec/productos/gorra-classic.html",
        "emoji": "🧢"
    },
    "gorra_sunset": {
        "name": "Gorra Sonora Sunset",
        "price": "$449 MXN",
        "desc": "Naranja quemado con bordado 'Sonora' en dorado.",
        "url": "https://sonoradigitalcorp.com/azrec/productos/gorra-sunset.html",
        "emoji": "🧢"
    },
    "playera_classic": {
        "name": "Playera AzREC Classic",
        "price": "$349 MXN",
        "desc": "Algodon premium, logo frontal. S-3XL.",
        "url": "https://sonoradigitalcorp.com/azrec/productos/playera-classic.html",
        "emoji": "👕"
    },
    "hoodie": {
        "name": "Hoodie AzREC",
        "price": "$699 MXN",
        "desc": "Algodon peluche, bolsillo canguro, logo bordado.",
        "url": "https://sonoradigitalcorp.com/azrec/productos/hoodie.html",
        "emoji": "🧥"
    },
    "tote": {
        "name": "Tote Bag 'Desierto'",
        "price": "$249 MXN",
        "desc": "Lona gruesa con diseno del desierto de Sonora.",
        "url": "https://sonoradigitalcorp.com/azrec/productos/tote-bag.html",
        "emoji": "🛍️"
    },
    "stickers": {
        "name": "Stickers Pack (5)",
        "price": "$99 MXN",
        "desc": "Vinil termico. Logo + Sonora + Cactus + Mas.",
        "url": "https://sonoradigitalcorp.com/azrec/productos/stickers.html",
        "emoji": "🎨"
    }
}

# ========== COMMANDS ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🛍️ Catalogo", callback_data="catalogo"),
         InlineKeyboardButton("🧢 Gorras", callback_data="gorras")],
        [InlineKeyboardButton("👕 Playeras", callback_data="playeras"),
         InlineKeyboardButton("ℹ️ Info", callback_data="info")],
        [InlineKeyboardButton("👥 Grupo AzREC", url=f"https://t.me/AzREC")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🔥 Bienvenido a *AzREC*, {user.first_name}!\n\n"
        "De la A a la Z, del desierto al mundo.\n\n"
        "🧢 *Gorras* | 👕 *Playeras* | 🎧 *Musica*\n"
        "Usa los botones para explorar:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show full catalog"""
    keyboard = []
    for pid, product in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(
            f"{product['emoji']} {product['name']} — {product['price']}",
            callback_data=f"product:{pid}"
        )])
    keyboard.append([InlineKeyboardButton("🛒 Ir a la tienda", url=SHOPIFY_URL)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = "📋 *Catalogo AzREC*\n\nSelecciona un producto:"
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

async def gorras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"🧢 Gorra AzREC Classic — $399", callback_data="product:gorra_classic")],
        [InlineKeyboardButton(f"🧢 Gorra Sonora Sunset — $449", callback_data="product:gorra_sunset")],
        [InlineKeyboardButton("🛒 Ver todas las gorras", url="https://sonoradigitalcorp.com/azrec/catalogo")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🧢 *Gorras AzREC*\n\nEstilo unico, orgullo sonorense.", parse_mode="Markdown", reply_markup=reply_markup)

async def playeras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"👕 Playera Classic — $349", callback_data="product:playera_classic")],
        [InlineKeyboardButton(f"🧥 Hoodie AzREC — $699", callback_data="product:hoodie")],
        [InlineKeyboardButton("🛒 Ver todas las playeras", url="https://sonoradigitalcorp.com/azrec/catalogo")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👕 *Playeras AzREC*\n\nModa con identidad.", parse_mode="Markdown", reply_markup=reply_markup)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "*AzREC* — Sello Musical · Moda · Cultura\n\n"
        "📍 Hermosillo, Sonora, Mexico\n"
        "🎵 De la A a la Z, del desierto al mundo\n\n"
        "*Que somos:*\n"
        "🎧 Sello musical independiente\n"
        "🧢 Gorras y merch de la ciudad\n"
        "🏠 Casa-estudio con cuartos de ensayo\n"
        "🤖 Asistente de ventas 24/7\n\n"
        "*Contacto:*\n"
        "📧 hola@azrec.mx\n"
        "📱 @AlejandroZamora (Telegram)\n"
        "🛍️ azrec.mx"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "*Comandos AzREC:*\n\n"
        "/start — Menu principal\n"
        "/catalogo — Ver todos los productos\n"
        "/gorras — Coleccion de gorras\n"
        "/playeras — Playeras y hoodies\n"
        "/info — Sobre AzREC\n"
        "/ayuda — Este mensaje\n"
        "/tienda — Ir a la tienda\n\n"
        "*Bots internos:*\n"
        "/hermes — Llamar a Hermes (asistente principal)\n"
        "/abe — Llamar a Abe Music\n"
        "/sdc — Llamar a Sonora Digital Corp\n\n"
        "Tambien puedes escribir el nombre de un producto y te dare info!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def tienda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🛍️ Ir a la tienda", url=SHOPIFY_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Visita nuestra tienda online:", reply_markup=reply_markup)

# ========== CALLBACKS ==========

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "catalogo":
        keyboard = []
        for pid, product in PRODUCTS.items():
            keyboard.append([InlineKeyboardButton(
                f"{product['emoji']} {product['name']} — {product['price']}",
                callback_data=f"product:{pid}"
            )])
        keyboard.append([InlineKeyboardButton("🛒 Ir a la tienda", url=SHOPIFY_URL)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("📋 *Catalogo AzREC:*", parse_mode="Markdown", reply_markup=reply_markup)
    
    elif data == "gorras":
        keyboard = [
            [InlineKeyboardButton(f"🧢 Gorra AzREC Classic — $399", callback_data="product:gorra_classic")],
            [InlineKeyboardButton(f"🧢 Gorra Sonora Sunset — $449", callback_data="product:gorra_sunset")],
            [InlineKeyboardButton("🛒 Ver todas", url="https://sonoradigitalcorp.com/azrec/catalogo")],
            [InlineKeyboardButton("← Volver", callback_data="catalogo")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🧢 *Gorras AzREC*", parse_mode="Markdown", reply_markup=reply_markup)
    
    elif data == "playeras":
        keyboard = [
            [InlineKeyboardButton(f"👕 Playera Classic — $349", callback_data="product:playera_classic")],
            [InlineKeyboardButton(f"🧥 Hoodie AzREC — $699", callback_data="product:hoodie")],
            [InlineKeyboardButton("🛒 Ver todas", url="https://sonoradigitalcorp.com/azrec/catalogo")],
            [InlineKeyboardButton("← Volver", callback_data="catalogo")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("👕 *Playeras AzREC*", parse_mode="Markdown", reply_markup=reply_markup)
    
    elif data == "info":
        msg = (
            "*AzREC* — Sello Musical · Moda · Cultura\n\n"
            "📍 Hermosillo, Sonora\n"
            "🎵 De la A a la Z\n\n"
            "Contacto: @AlejandroZamora"
        )
        await query.edit_message_text(msg, parse_mode="Markdown")
    
    elif data.startswith("product:"):
        pid = data.replace("product:", "")
        product = PRODUCTS.get(pid)
        if product:
            keyboard = [
                [InlineKeyboardButton("🛒 Comprar ahora", url=product["url"])],
                [InlineKeyboardButton("← Volver al catalogo", callback_data="catalogo")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            msg = (
                f"{product['emoji']} *{product['name']}*\n\n"
                f"💲 *Precio:* {product['price']}\n"
                f"📝 {product['desc']}\n\n"
                f"[Ver en tienda]({product['url']})"
            )
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

# ========== MESSAGE HANDLER (free text -> product search) ==========

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    # Check if message matches a product
    for pid, product in PRODUCTS.items():
        name_lower = product["name"].lower()
        if any(word in text for word in name_lower.split()):
            keyboard = [
                [InlineKeyboardButton("🛒 Comprar", url=product["url"])],
                [InlineKeyboardButton("📋 Catalogo completo", callback_data="catalogo")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"🔥 *{product['name']}*\n💲 {product['price']}\n{product['desc']}",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            return
    
    # Fallback
    await update.message.reply_text(
        "No entendi. Usa /ayuda para ver los comandos disponibles.",
        parse_mode="Markdown"
    )

# ========== MAIN ==========

def main():
    logging.basicConfig(level=logging.INFO)
    
    if not TOKEN:
        log.error("AZREC_TELEGRAM_TOKEN not set!")
        print("ERROR: Set AZREC_TELEGRAM_TOKEN environment variable")
        print("1. Create bot via @BotFather on Telegram")
        print("2. Set token: export AZREC_TELEGRAM_TOKEN='your_token_here'")
        sys.exit(1)
    
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalogo", catalogo))
    app.add_handler(CommandHandler("gorras", gorras))
    app.add_handler(CommandHandler("playeras", playeras))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("tienda", tienda))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    log.info("AzREC Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
