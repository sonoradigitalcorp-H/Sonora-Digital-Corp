import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

from config import TOKEN, PRICING, BOT_USERNAME

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Conversation states
NAME, COMPANY, SIZE, PHONE = range(4)

WEB_URL = "https://t.me/Nathy_Conta_bot"

def make_keyboard(*buttons, row_width=2):
    kb = [
        [InlineKeyboardButton(text, callback_data=data)]
        for text, data in buttons
    ]
    return InlineKeyboardMarkup(kb)

MAIN_MENU = make_keyboard(
    ("Servicios", "services"),
    ("Planes", "pricing"),
    ("FAQ", "faq"),
    ("Contactar", "contact"),
    row_width=2,
)

BACK_BTN = make_keyboard(
    ("← Volver al menú", "menu"),
)

async def start(update: Update, context):
    user = update.effective_user
    msg = (
        f"¡Hola {user.first_name}! 👋\n\n"
        "Soy **Nathy Conta**, tu asistente de contabilidad digital.\n\n"
        "Ayudo a pequeñas, medianas y grandes empresas a mantener "
        "su contabilidad al día, sin complicaciones y 100% digital.\n\n"
        "¿Qué te gustaría hacer?"
    )
    await update.message.reply_text(msg, reply_markup=MAIN_MENU, parse_mode="Markdown")

async def menu_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == "menu":
        await query.edit_message_text(
            "¿Qué te gustaría hacer?",
            reply_markup=MAIN_MENU,
        )

    elif action == "services":
        text = (
            "📋 *Nuestros Servicios*\n\n"
            "Adaptamos nuestra contabilidad al tamaño de tu empresa:\n\n"
            "🏢 *Pequeña Empresa*\n"
            "Contabilidad simplificada, IVA/ISR, facturación CFDI.\n\n"
            "🏭 *Mediana Empresa*\n"
            "Gestión integral, nóminas, estados financieros.\n\n"
            "🏛️ *Gran Empresa*\n"
            "Outsourcing total, consolidación, auditoría.\n\n"
            "¿Quieres ver los planes o contactarme directamente?"
        )
        await query.edit_message_text(
            text,
            reply_markup=make_keyboard(
                ("Ver planes", "pricing"),
                ("Contactar", "contact"),
                ("← Volver", "menu"),
            ),
            parse_mode="Markdown",
        )

    elif action == "pricing":
        text = "*Planes Transparentes*\n\nSin letras chiquitas:\n\n"
        for key, plan in PRICING.items():
            text += f"▸ *{plan['name']}* — {plan['price']}\n"
            text += f"  _{plan['for']}_\n"
            for f in plan["features"]:
                text += f"  ✓ {f}\n"
            text += "\n"
        text += "¿Te interesa alguno? Cuéntame de tu negocio y te recomiendo el mejor."
        await query.edit_message_text(
            text,
            reply_markup=make_keyboard(
                ("Quiero el Profesional", "pick_profesional"),
                ("Cotización personalizada", "contact"),
                ("← Volver", "menu"),
            ),
            parse_mode="Markdown",
        )

    elif action == "pick_profesional":
        await query.edit_message_text(
            "¡Excelente elección! El Plan Profesional es el más solicitado. 🎯\n\n"
            "Para empezar, ¿me regalas tu nombre para poder atenderte mejor?",
            reply_markup=make_keyboard(("← Cancelar", "menu")),
        )
        return NAME

    elif action == "faq":
        text = (
            "❓ *Preguntas Frecuentes*\n\n"
            "**¿Cómo subo mis facturas?**\n"
            "Las compartes directamente por este chat. Las recibo y proceso.\n\n"
            "**¿Hay contrato mínimo?**\n"
            "No. Puedes cancelar cuando quieras, sin penalización.\n\n"
            "**¿Atienden todo México?**\n"
            "Sí, 100% digital. Estamos donde estés.\n\n"
            "**¿Qué necesito para empezar?**\n"
            "Solo tu RFC y tus facturas del mes.\n\n"
            "**¿Hablan con el SAT por mí?**\n"
            "Sí, te representamos ante el SAT para todo trámite."
        )
        await query.edit_message_text(
            text,
            reply_markup=BACK_BTN,
            parse_mode="Markdown",
        )

    elif action == "contact":
        text = (
            "¡Encantada de conocerte! 🎉\n\n"
            "Para darte una cotización exacta, cuéntame:\n\n"
            "**¿Cuál es tu nombre?**"
        )
        await query.edit_message_text(
            text,
            reply_markup=make_keyboard(("← Cancelar", "menu")),
            parse_mode="Markdown",
        )
        return NAME

    return ConversationHandler.END

async def ask_name(update: Update, context):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        f"Perfecto, {update.message.text}. ¿Cuál es el nombre de tu empresa o negocio?"
    )
    return COMPANY

async def ask_company(update: Update, context):
    context.user_data["company"] = update.message.text
    await update.message.reply_text(
        "¿Qué tamaño tiene tu empresa?\n\n"
        "1️⃣ Persona física / Freelancer\n"
        "2️⃣ Pequeña (1-10 empleados)\n"
        "3️⃣ Mediana (11-50 empleados)\n"
        "4️⃣ Grande (51+ empleados)",
    )
    return SIZE

SIZE_MAP = {
    "1": "Persona física / Freelancer",
    "2": "Pequeña (1-10 empleados)",
    "3": "Mediana (11-50 empleados)",
    "4": "Grande (51+ empleados)",
}

async def ask_size(update: Update, context):
    text = update.message.text.strip()
    size = SIZE_MAP.get(text, text)
    context.user_data["size"] = size
    await update.message.reply_text(
        "Gracias. Por último, ¿me compartes tu número de teléfono "
        "para que te contacte a la brevedad?"
    )
    return PHONE

async def ask_phone(update: Update, context):
    context.user_data["phone"] = update.message.text
    data = context.user_data
    msg = (
        "✅ *¡Recibido!*\n\n"
        f"**Nombre:** {data.get('name')}\n"
        f"**Empresa:** {data.get('company')}\n"
        f"**Tamaño:** {data.get('size')}\n"
        f"**Teléfono:** {data.get('phone')}\n\n"
        "En las próximas horas me pondré en contacto contigo "
        "para darte una propuesta personalizada. 🚀\n\n"
        "Mientras tanto, si tienes dudas, aquí estoy."
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_MENU)
    logger.info("New lead: %s", data)
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context):
    await update.message.reply_text(
        "Sin problema. Cuando gustes, aquí estoy. 🫶",
        reply_markup=MAIN_MENU,
    )
    context.user_data.clear()
    return ConversationHandler.END

async def error_handler(update: Update, context):
    logger.error("Error: %s", context.error)

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(menu_handler, pattern="^(contact|pick_profesional)$"),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_company)],
            SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_size)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(menu_handler, pattern="^menu$"),
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_error_handler(error_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
