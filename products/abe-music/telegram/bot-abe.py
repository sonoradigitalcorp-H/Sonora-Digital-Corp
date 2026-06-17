#!/usr/bin/env python3
import logging, os, sys, json, urllib.request, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, filters, ContextTypes

log = logging.getLogger("abe.telegram")
TOKEN = os.getenv("ABE_TELEGRAM_TOKEN", "")

API_BASE = os.getenv("ABE_API_BASE", "http://localhost:5174")

FALLBACK_ARTISTS = {
    "hector_rubio": {"name": "Hector Rubio", "genre": "Regional Mexicano", "streams": 193000, "revenue": 9660.0, "releases": 3, "status": "active"},
    "jesus_urquijo": {"name": "Jesus Urquijo", "genre": "Pop Latino", "streams": 245000, "revenue": 12110.0, "releases": 2, "status": "active"},
    "javier_arvayo": {"name": "Javier Arvayo", "genre": "Urbano", "streams": 101000, "revenue": 5110.0, "releases": 2, "status": "signed"},
}

def fetch_data(endpoint):
    try:
        req = urllib.request.Request(f"{API_BASE}{endpoint}", headers={"User-Agent": "ABE-Bot/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception as e:
        log.warning(f"API fetch failed ({endpoint}): {e}")
        return None

def get_artists():
    data = fetch_data("/api/abe/artists")
    if data and "artists" in data:
        return {a["id"]: a for a in data["artists"]}
    return None

def get_dashboard():
    return fetch_data("/api/abe/dashboard/ceo")

def format_num(n):
    return f"{n:,}" if n else "—"

artists_cache = None
dashboard_cache = None

async def refresh_cache():
    global artists_cache, dashboard_cache
    artists_cache = get_artists()
    dashboard_cache = get_dashboard()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await refresh_cache()
    user = update.effective_user
    dc = dashboard_cache
    total_streams = format_num(dc["total_streams"]) if dc else "—"
    total_revenue = f"${format_num(dc['total_revenue'])}" if dc else "—"
    keyboard = [
        [InlineKeyboardButton("🎤 Artistas", callback_data="artistas")],
        [InlineKeyboardButton("📊 Estadísticas", callback_data="stats")],
        [InlineKeyboardButton("ℹ️ Abe Music", callback_data="info")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🎵 *Abe Music*, {user.first_name}!\n\n"
        f"📀 {total_streams} streams totales\n"
        f"💰 {total_revenue} revenue\n\n"
        f"Artistas. Talento. Resultados.",
        parse_mode="Markdown", reply_markup=reply_markup
    )

async def artistas_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    await refresh_cache()
    artists = artists_cache or FALLBACK_ARTISTS
    msg_target = update.message if not edit else update.callback_query
    keyboard = []
    for aid, a in artists.items():
        name = a.get("nombre", a.get("name", "?"))
        streams = a.get("streams", 0)
        keyboard.append([InlineKeyboardButton(
            f"{'🎤' if streams > 150000 else '🎸' if streams > 100000 else '🎵'} {name} — {format_num(streams)} streams",
            callback_data=f"artist:{aid}"
        )])
    keyboard.append([InlineKeyboardButton("← Volver", callback_data="main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🎤 *Artistas Abe Music*\n\nSelecciona un artista:"
    if edit:
        await msg_target.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await msg_target.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await refresh_cache()
    dc = dashboard_cache
    if not dc:
        await update.message.reply_text("❌ No se pudo obtener estadísticas. Intenta más tarde.")
        return
    keyboard = [[InlineKeyboardButton("← Volver", callback_data="main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = (
        "📊 *ABE MUSIC — Estadísticas*\n\n"
        f"🎵 Streams totales: *{format_num(dc['total_streams'])}*\n"
        f"💰 Revenue total: *${format_num(dc['total_revenue'])}*\n"
        f"🎤 Artistas: *{dc['total_artists']}* ({dc['active_artists']} activos)\n"
        f"📀 Lanzamientos: *{dc['total_releases']}*\n\n"
        f"*Revenue Split:*\n"
        f"└ Artistas: ${format_num(dc['revenue_breakdown']['artists_share'])}\n"
        f"└ Label: ${format_num(dc['revenue_breakdown']['label_share'])}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("← Volver", callback_data="main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = (
        "*Abe Music Inc*\n\n"
        "🎵 Representación artística\n"
        "🎸 Corridos · Regional Mexicano · Urbano\n"
        "📍 Compton, CA\n\n"
        "CEO: Abraham Ortega\n"
        "Streaming · Distribución · Management\n\n"
        "Parte del ecosistema *Sonora Digital Corp*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    artists = artists_cache or FALLBACK_ARTISTS

    if data == "main":
        dc = dashboard_cache
        total_streams = format_num(dc["total_streams"]) if dc else "—"
        total_revenue = f"${format_num(dc['total_revenue'])}" if dc else "—"
        keyboard = [
            [InlineKeyboardButton("🎤 Artistas", callback_data="artistas")],
            [InlineKeyboardButton("📊 Estadísticas", callback_data="stats")],
            [InlineKeyboardButton("ℹ️ Abe Music", callback_data="info")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🎵 *Abe Music*\n\n📀 {total_streams} streams\n💰 {total_revenue} revenue",
            parse_mode="Markdown", reply_markup=reply_markup
        )

    elif data == "artistas":
        keyboard = []
        for aid, a in artists.items():
            name = a.get("nombre", a.get("name", "?"))
            streams = a.get("streams", 0)
            keyboard.append([InlineKeyboardButton(
                f"{'🎤' if streams > 150000 else '🎸' if streams > 100000 else '🎵'} {name}",
                callback_data=f"artist:{aid}"
            )])
        keyboard.append([InlineKeyboardButton("← Volver", callback_data="main")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🎤 *Artistas Abe Music*", parse_mode="Markdown", reply_markup=reply_markup)

    elif data == "stats":
        dc = dashboard_cache
        if dc:
            msg = (
                "📊 *ABE MUSIC — Estadísticas*\n\n"
                f"🎵 Streams: *{format_num(dc['total_streams'])}*\n"
                f"💰 Revenue: *${format_num(dc['total_revenue'])}*\n"
                f"🎤 Artistas: *{dc['total_artists']}*\n"
                f"📀 Releases: *{dc['total_releases']}*\n\n"
                f"*Revenue Split:*\n"
                f"└ Artistas: ${format_num(dc['revenue_breakdown']['artists_share'])}\n"
                f"└ Label: ${format_num(dc['revenue_breakdown']['label_share'])}"
            )
        else:
            msg = "❌ Estadísticas no disponibles"
        keyboard = [[InlineKeyboardButton("← Volver", callback_data="main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

    elif data == "info":
        msg = (
            "*Abe Music Inc*\n\n"
            "🎵 Representación artística\n"
            "🎸 Corridos · Regional Mexicano · Urbano\n"
            "📍 Compton, CA\n\n"
            "CEO: Abraham Ortega\n"
            "Streaming · Distribución · Management\n\n"
            "Parte de *Sonora Digital Corp*"
        )
        keyboard = [[InlineKeyboardButton("← Volver", callback_data="main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

    elif data.startswith("artist:"):
        aid = data.replace("artist:", "")
        a = artists.get(aid)
        if not a:
            await query.edit_message_text("❌ Artista no encontrado")
            return
        name = a.get("nombre", a.get("name", "?"))
        genre = a.get("genero", a.get("genre", "?"))
        streams = a.get("streams", 0)
        revenue = a.get("revenue", 0)
        releases = a.get("releases_count", a.get("releases", 0))
        status = a.get("status", "?")
        status_emoji = "🟢" if status == "active" else "🟡" if status == "signed" else "⚪"
        keyboard = [[InlineKeyboardButton("← Artistas", callback_data="artistas")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = (
            f"{status_emoji} *{name}*\n\n"
            f"🎵 Género: {genre}\n"
            f"📊 Streams: *{format_num(streams)}*\n"
            f"💰 Revenue: *${format_num(revenue)}*\n"
            f"📀 Lanzamientos: {releases}\n"
            f"📌 Estado: {status}"
        )
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if any(word in text for word in ["hola", "buenas", "hey", "hi", "hello"]):
        await start(update, context)
    elif any(word in text for word in ["artista", "musica", "music", "talento"]):
        await artistas_menu(update, context)
    elif any(word in text for word in ["stats", "estadistica", "numeros", "streams"]):
        await show_stats(update, context)
    elif any(word in text for word in ["info", "informacion", "abe"]):
        await show_info(update, context)

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    if not TOKEN:
        log.error("ABE_TELEGRAM_TOKEN not set!")
        sys.exit(1)
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("artistas", lambda u,c: artistas_menu(u,c)))
    app.add_handler(CommandHandler("stats", show_stats))
    app.add_handler(CommandHandler("info", show_info))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(filters.TEXT & ~filters.COMMAND, handle_message)
    log.info("ABE Music Bot started — polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
