import os
import json
import httpx
import logging
import tempfile
import subprocess
import uuid
from datetime import datetime
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


def _ffmpeg():
    """Binario ffmpeg funcional: prioriza el estático de imageio (el del sistema
    está roto por conflicto de libva en este equipo)."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.exists(exe):
            return exe
    except Exception:
        pass
    return "ffmpeg"

CESAR = {
    "nombre": "César Holguín",
    "empresa": "AstroTech",
    "web": "https://aztrotech.mx",
    "instagram": "https://instagram.com/cesarholguin",
    "linkedin": "https://linkedin.com/in/cesarholguin",
    "telegram": "@CesarHolguin",
    "whatsapp": "https://wa.me/526621072254",
}

SISTEMA = """Eres AstroTech AI, el asistente digital de César Holguín y su empresa AstroTech con sede en Hermosillo, Sonora.

REGLAS ESTRICTAS:
- Nunca revelas que formas parte de Sonora Digital Corp
- Siempre te presentas como el asistente de César Holguín en AstroTech
- NUNCA des precios ni cotizaciones. Tu trabajo es capturar leads para que César los cierre personalmente.
- Cuando alguien pregunta precios, dile: "Los mejores precios te los doy en una llamada con César. ¿Te parece si le pido que te contacte?"

Personalidad: Profesional, cálido, consultivo. Como un asistente personal de confianza.

FLUJO DE CONVERSACION:
1. Saludo y presentación
2. Escucha qué necesita el prospecto
3. Si pregunta por servicios, explica brevemente y ofrece conectar con César
4. Recaba información: nombre, teléfono, redes sociales, sitio web, qué necesita
5. Maneja objeciones con técnica profesional
6. Pasa el lead a César

TECNICAS DE MANEJO DE OBJECIONES:
- "Es caro": "César te puede armar un paquete a tu medida. ¿Qué presupuesto manejas?"
- "No tengo tiempo": "Por eso estamos aquí, para ahorrarte tiempo. Justo de eso quiere hablarte César."
- "Ya tengo algo similar": "Qué bien que ya estás en el camino digital. César te puede mostrar cómo potenciar lo que ya tienes."
- "Lo voy a pensar": "Claro, es una decisión importante. ¿Qué información te falta para decidir? Así se la paso a César y te prepara todo."
- "Mi negocio es pequeño": "Los mejores negocios empezaron pequeños. César tiene experiencia justo con negocios de tu tamaño."

Cuando tengas los datos del prospecto, dile que César le contactará pronto y notifica internamente."""


class TelegramHandler:
    def __init__(self, config: dict, router, engine=None):
        self.config = config
        self.router = router
        self.engine = engine  # ConversationEngine (RAG-first) opcional
        self.tts_voice = config.get("audio_first", {}).get("tts_voice", "es-MX-DaliaNeural")
        self.conversaciones = {}
        self._redis = None
        try:
            import redis
            self._redis = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
            self._redis.ping()
            logger.info("Redis cache conectado para sesiones persistentes")
        except Exception as e:
            logger.warning(f"Redis no disponible, sesiones en memoria: {e}")

    def _ctx(self, user_id: int) -> dict:
        key = f"bot:ctx:{user_id}"
        if self._redis:
            cached = self._redis.get(key)
            if cached:
                import json as _json
                return _json.loads(cached)
        if user_id not in self.conversaciones:
            self.conversaciones[user_id] = {"voz": False, "datos": {}, "paso": "inicio", "historial": []}
        return self.conversaciones[user_id]

    def _save_ctx(self, user_id: int, ctx: dict):
        if self._redis:
            import json as _json
            self._redis.setex(f"bot:ctx:{user_id}", 86400, _json.dumps(ctx))
        else:
            self.conversaciones[user_id] = ctx

    async def handle_message(self, update: Update, context: CallbackContext):
        msg = update.message
        user = update.effective_user
        texto = (msg.text or "").strip().lower()
        
        # ── Mystic Shield ──
        from security.shield import shield_check
        allowed, reason = shield_check(user.id, texto)
        if not allowed:
            await msg.reply_text(f"🛡️ {reason}")
            logger.warning(f"Shield blocked user {user.id}: {reason}")
            return
        
        ctx = self._ctx(user.id)

        if not texto:
            return

        ctx["historial"].append(("user", texto))

        if any(p in texto for p in ["hola", "buenos días", "buenas", "qué tal", "hey", "buenas tardes"]):
            await self._bienvenida(update, user)
            return

        if any(p in texto for p in ["servicios", "qué ofrecen", "qué hacen", "qué es astrotech"]):
            await self._explicar_servicios(update)
            return

        if any(p in texto for p in ["precio", "cuánto cuesta", "cuanto cuesta", "costo", "valor", "$", "pesos", "dólares"]):
            await self._objecion_precio(update)
            return

        if any(p in texto for p in ["cesar", "hablar con", "contactar", "dueño", "humano", "asesor", "persona"]):
            await self._conectar_con_cesar(update)
            return

        if any(p in texto for p in ["modo voz", "voz", "audio", "escuchar", "modo audio"]):
            ctx["voz"] = True
            self._save_ctx(user.id, ctx)
            await msg.reply_text("Modo voz activado. Te responderé con audio.")
            return

        if any(p in texto for p in ["modo texto", "texto", "escribir", "teclear"]):
            ctx["voz"] = False
            self._save_ctx(user.id, ctx)
            await msg.reply_text("Modo texto activado.")
            return

        if any(p in texto for p in ["redes", "instagram", "linkedin", "facebook", "página", "web", "sitio", "aztrotech"]):
            await self._mostrar_redes(update)
            return

        if any(p in texto for p in ["no me interesa", "no gracias", "después", "ahora no", "estoy ocupado"]):
            await self._objecion_general(update, texto)
            return

        if any(p in texto for p in ["ya tengo", "ya uso", "ya trabajo con", "ya contraté", "tengo uno"]):
            await self._objecion_tiene_algo(update)
            return

        if any(p in texto for p in ["es caro", "no tengo presupuesto", "muy caro", "caro", "no me alcanza"]):
            await self._objecion_precio(update)
            return

        if any(p in texto for p in ["lo pensaré", "lo voy a pensar", "lo pienso", "voy a pensarlo"]):
            await self._objecion_pensar(update)
            return

        if any(p in texto for p in ["pequeño", "negocio pequeño", "soy pequeño", "apenas empiezo", "micro"]):
            await self._objecion_pequeno(update)
            return

        if any(p in texto for p in ["quiero contratar", "me interesa", "quiero", "registrarme", "empezar", "ayuda"]):
            await self._capturar_datos(update)
            return

        await self._respuesta_general(update, texto)

    async def handle_voice_message(self, update: Update, context: CallbackContext):
        msg = update.message
        ctx = self._ctx(update.effective_user.id)

        await msg.reply_text("Escuchando...")

        voice = msg.voice
        ogg_file = await voice.get_file()
        ogg_bytes = await ogg_file.download_as_bytearray()

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
            f.write(ogg_bytes)
            ogg_path = f.name

        wav_path = ogg_path.replace(".ogg", ".wav")
        subprocess.run(
            [_ffmpeg(), "-y", "-i", ogg_path, "-ar", "16000", "-ac", "1", wav_path],
            capture_output=True,
        )

        texto = ""
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            from apps.voice.stt import transcribe as _stt_transcribe
            texto = _stt_transcribe(wav_path, language="es")
        except Exception as e:
            logger.warning(f"STT falló: {e}")
            try:
                import speech_recognition as sr
                r = sr.Recognizer()
                with sr.AudioFile(wav_path) as src:
                    audio = r.record(src)
                texto = r.recognize_google(audio, language="es-ES")
            except Exception:
                texto = ""

        os.unlink(ogg_path)
        if os.path.exists(wav_path):
            os.unlink(wav_path)

        if not texto:
            await msg.reply_text("Gracias. Cuéntame en qué puedo ayudarte.")
            return

        ctx["historial"].append(("user_audio", texto))
        ctx["voz"] = True
        await self._respuesta_general(update, texto)

    async def handle_callback(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == "servicios":
            await self._explicar_servicios(update, edit=True)
        elif data == "redes":
            await self._mostrar_redes(update, edit=True)
        elif data == "contratar":
            await self._capturar_datos(update, edit=True)
        elif data == "cesar":
            await self._conectar_con_cesar(update, edit=True)
        elif data == "voz_on":
            self._ctx(update.effective_user.id)["voz"] = True
            await query.edit_message_text("Modo voz activado. Te responderé con audio.")
        elif data == "voz_off":
            self._ctx(update.effective_user.id)["voz"] = False
            await query.edit_message_text("Modo texto activado.")
        elif data == "inicio":
            await self._bienvenida(update, query, edit=True)

    async def _bienvenida(self, update: Update, user_or_query, edit=False):
        user = getattr(user_or_query, "effective_user", None) or getattr(user_or_query, "from_user", None)
        nombre = (user.first_name or "") if user else ""
        username = (user.username or "") if user else ""
        saludo = f"Hola{' ' + nombre if nombre else ''}"
        msg = (
            f"{saludo}. Soy el asistente digital de **César Holguín** y su empresa AstroTech.\n\n"
            "Estoy aquí para conocerte y ver cómo podemos ayudarte a ti o a tu negocio.\n\n"
            "Cuéntame, ¿a qué te dedicas?"
        )
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Servicios", callback_data="servicios"),
             InlineKeyboardButton("Redes de César", callback_data="redes")],
            [InlineKeyboardButton("Hablar con César", callback_data="cesar")],
            [InlineKeyboardButton("🎤 Modo voz", callback_data="voz_on"),
             InlineKeyboardButton("⌨️ Modo texto", callback_data="voz_off")],
        ])
        if edit:
            await update.callback_query.edit_message_text(msg, parse_mode="Markdown", reply_markup=teclado)
        else:
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=teclado)

    async def _explicar_servicios(self, update: Update, edit=False):
        msg = (
            "AstroTech ofrece tecnología para impulsar tu negocio:\n\n"
            "🤖 Empleado Digital — Agente IA que atiende a tus clientes 24/7 por WhatsApp, Instagram y Facebook\n"
            "📊 Sistema de Ventas — CRM con agentes que califican y cierran leads\n"
            "💻 Desarrollo a Medida — Apps, ERPs y APIs para tu negocio\n"
            "🎯 Empresa 90 Días — Mentoría con César para lanzar o escalar\n"
            "🤝 Socio Estratégico — Relación de largo plazo, revenue share\n\n"
            "¿Te gustaría que César te explique cuál es el mejor para ti?"
        )
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Quiero que César me contacte", callback_data="cesar")],
            [InlineKeyboardButton("Redes de César", callback_data="redes")],
        ])
        if edit:
            await update.callback_query.edit_message_text(msg, reply_markup=teclado)
        else:
            await update.message.reply_text(msg, reply_markup=teclado)

    async def _mostrar_redes(self, update: Update, edit=False):
        msg = (
            "Puedes conocer más de César y AstroTech aquí:\n\n"
            f"🌐 Web: {CESAR['web']}\n"
            f"📸 Instagram: {CESAR['instagram']}\n"
            f"💼 LinkedIn: {CESAR['linkedin']}\n"
            f"✈️ Telegram: {CESAR['telegram']}\n"
            f"📱 WhatsApp: {CESAR['whatsapp']}\n\n"
            "¿Algo más en qué pueda ayudarte?"
        )
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Servicios", callback_data="servicios")],
            [InlineKeyboardButton("Hablar con César", callback_data="cesar")],
        ])
        if edit:
            await update.callback_query.edit_message_text(msg, reply_markup=teclado)
        else:
            await update.message.reply_text(msg, reply_markup=teclado)

    async def _capturar_datos(self, update: Update, edit=False):
        msg = (
            "Excelente. Para que César te contacte con la mejor propuesta, "
            "necesito algunos datos:\n\n"
            "1. Tu nombre completo\n"
            "2. Tu teléfono con código de país\n"
            "3. Tu correo electrónico\n"
            "4. ¿Tienes página web o redes sociales de tu negocio?\n"
            "5. Cuéntame brevemente qué necesitas\n\n"
            "Puedes escribirme todo aquí."
        )
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Hablar con César directo", callback_data="cesar")],
        ])
        if edit:
            await update.callback_query.edit_message_text(msg, reply_markup=teclado)
        else:
            await update.message.reply_text(msg, reply_markup=teclado)

    async def _conectar_con_cesar(self, update: Update, edit=False):
        user = update.effective_user
        nombre = user.first_name or ""
        username = user.username or ""
        user_id = user.id

        msg = (
            "Perfecto. Le notificaré a César para que te contacte personalmente. "
            "Mientras tanto, aquí tienes sus redes por si quieres conocer más:\n\n"
            f"🌐 {CESAR['web']}\n"
            f"📸 {CESAR['instagram']}\n"
            f"📱 WhatsApp: {CESAR['whatsapp']}"
        )
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Servicios", callback_data="servicios")],
        ])
        if edit:
            await update.callback_query.edit_message_text(msg, reply_markup=teclado)
        else:
            await update.message.reply_text(msg, reply_markup=teclado)

        await self._notificar_cesar(update)

    async def _objecion_precio(self, update: Update):
        msg = (
            "Los mejores precios te los doy en una llamada con César, "
            "porque cada negocio es diferente y él te arma algo a tu medida. "
            "¿Te parece si le pido que te contacte?"
        )
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Sí, que me contacte", callback_data="cesar")],
            [InlineKeyboardButton("Ver servicios", callback_data="servicios")],
        ])
        await update.message.reply_text(msg, reply_markup=teclado)

    async def _objecion_general(self, update: Update, texto: str):
        msg = (
            "Entiendo perfectamente. Cuando quieras, aquí estoy. "
            "Mientras, puedes conocer más de César y su trabajo en sus redes."
        )
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Redes de César", callback_data="redes")],
            [InlineKeyboardButton("Servicios", callback_data="servicios")],
        ])
        await update.message.reply_text(msg, reply_markup=teclado)

    async def _objecion_tiene_algo(self, update: Update):
        msg = (
            "Qué bien que ya estás en el camino digital. César te puede mostrar "
            "cómo potenciar lo que ya tienes sin empezar de cero. "
            "¿Te parece si te contacta para mostrarte cómo?"
        )
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Sí, que me contacte", callback_data="cesar")],
        ])
        await update.message.reply_text(msg, reply_markup=teclado)

    async def _objecion_pensar(self, update: Update):
        msg = (
            "Claro, tómate el tiempo que necesites. Dime, ¿qué información "
            "te falta para decidir? Así se la paso a César y te prepara todo "
            "antes de la llamada."
        )
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Que César me explique", callback_data="cesar")],
        ])
        await update.message.reply_text(msg, reply_markup=teclado)

    async def _objecion_pequeno(self, update: Update):
        msg = (
            "Los mejores negocios empezaron pequeños. César tiene mucha experiencia "
            "justo con negocios de tu tamaño y les ha ayudado a crecer. "
            "¿Te parece si te cuenta cómo?"
        )
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Sí, cuéntame", callback_data="cesar")],
        ])
        await update.message.reply_text(msg, reply_markup=teclado)

    async def _respuesta_general(self, update: Update, texto: str):
        ctx = self._ctx(update.effective_user.id)
        user_id = str(update.effective_user.id)

        # ── RAG-FIRST: si el engine está activo, usa el pipeline completo ──
        if self.engine:
            try:
                history = [
                    {"role": "user" if r.startswith("user") else "assistant", "content": c}
                    for r, c in ctx["historial"][-6:]
                ]
                # Resolver identidad cross-canal
                metadata = {"display_name": update.effective_user.first_name}
                internal_id = await self.engine.resolve_user(
                    "telegram", user_id, metadata
                )
                result = await self.engine.process(
                    user_message=texto,
                    internal_user_id=internal_id,
                    platform="telegram",
                    platform_conversation_id=f"tg:{user_id}",
                    history=history,
                    router=self.router,
                )
                reply = result.reply
                ctx["historial"].append(("user", texto))
                ctx["historial"].append(("assistant", reply))

                teclado = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Servicios", callback_data="servicios"),
                     InlineKeyboardButton("Redes de César", callback_data="redes")],
                    [InlineKeyboardButton("Hablar con César", callback_data="cesar")],
                ])
                await update.message.reply_text(reply, reply_markup=teclado)

                # Notificar César si lead hot
                if result.lead_type == "hot":
                    await self._notificar_cesar(update, extra_info=result)

                if ctx.get("voz"):
                    await self._enviar_voz(update, reply)
                return
            except Exception as e:
                logger.error(f"Engine error: {e}, fallback a modo simple")

        # ── Fallback: modo simple (sin engine) ──
        messages = [{"role": "system", "content": SISTEMA}]
        for rol, contenido in ctx["historial"][-6:]:
            messages.append({"role": "user" if rol.startswith("user") else "assistant", "content": contenido})
        messages.append({"role": "user", "content": texto})

        try:
            result = await self.router.call(messages)
            reply = result["choices"][0]["message"]["content"]
            ctx["historial"].append(("assistant", reply))
            teclado = InlineKeyboardMarkup([
                [InlineKeyboardButton("Servicios", callback_data="servicios"),
                 InlineKeyboardButton("Redes de César", callback_data="redes")],
                [InlineKeyboardButton("Hablar con César", callback_data="cesar")],
            ])
            await update.message.reply_text(reply, reply_markup=teclado)
            if ctx.get("voz"):
                await self._enviar_voz(update, reply)
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text(
                "Disculpa, tengo un problema. Le avisaré a César para que te contacte."
            )

    async def _enviar_voz(self, update: Update, texto: str):
        try:
            chat_id = update.effective_chat.id
            token = self.config["channels"]["telegram"]["bot_token"]
            tag = str(hash(texto))[-8:]
            wav = f"/tmp/astrotech-tts-{tag}.wav"
            ogg = wav.replace(".wav", ".ogg")

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "http://localhost:8765/tts",
                    json={"text": texto[:500], "voice": "cesar", "output": wav},
                )
                if resp.status_code == 200 and os.path.exists(wav):
                    subprocess.run([_ffmpeg(), "-y", "-i", wav, "-c:a", "libopus", "-b:a", "16k", ogg],
                                   capture_output=True)
                    os.unlink(wav)
                    if os.path.exists(ogg):
                        async with httpx.AsyncClient() as client2:
                            with open(ogg, "rb") as f:
                                await client2.post(f"https://api.telegram.org/bot{token}/sendVoice",
                                                   data={"chat_id": chat_id}, files={"voice": f})
                        os.unlink(ogg)
        except Exception as e:
            logger.warning(f"Voz no disponible: {e}")

    async def _notificar_cesar(self, update: Update, extra_info=None):
        try:
            user = update.effective_user
            nombre = user.first_name or "Anónimo"
            apellido = user.last_name or ""
            username = user.username or ""
            user_id = user.id
            chat_id = self.config["channels"]["telegram"]["owner_chat_id"]
            token = self.config["channels"]["telegram"]["bot_token"]

            nombre_completo = f"{nombre} {apellido}".strip()
            perfil_link = f"https://t.me/{username}" if username else f"tg://user?id={user_id}"
            wa_lead = "https://wa.me/526621072254"  # WhatsApp de César (placeholder hasta capturar el número real)

            score_line = ""
            if extra_info is not None:
                score_line = (
                    f"\n━━━━━━━━━━━━━━━\n"
                    f"🎯 **Lead {extra_info.lead_type.upper()}** ({round(extra_info.lead_confidence * 100)}%)\n"
                    f"😊 Emoción: {extra_info.dominant_emotion}\n"
                    f"🗣️ Idioma: {extra_info.language}\n"
                    f"💬 Último mensaje: _{getattr(extra_info, 'reply', '')[:120]}_\n"
                )

            msg = (
                f"🔔 **Nuevo Lead**\n\n"
                f"👤 **{nombre_completo}**\n"
                f"🆔 ID: `{user_id}`\n"
                + (f"✈️ @{username}\n" if username else "") +
                score_line +
                f"\n━━━━━━━━━━━━━━━\n\n"
                f"📲 **Contacta ahora:**\n"
                f"📱 WhatsApp César: wa.me/526621072254\n"
                f"🌐 Web: aztrotech.mx\n"
                f"\n━━━━━━━━━━━━━━━\n"
                f"💬 *Hola {nombre}, soy César Holguín de AstroTech. "
                f"Me dijeron que te interesaron nuestros servicios. "
                f"¿Cómo ves si te llamo para contarte?*"
            )
            teclado = {
                "inline_keyboard": [
                    [
                        {"text": "📲 WhatsApp lead", "url": wa_lead},
                        {"text": "✈️ Perfil Telegram", "url": perfil_link},
                    ],
                    [
                        {"text": "✅ Ya contactado", "callback_data": f"lead_done_{user_id}"},
                        {"text": "📋 Ver servicios", "callback_data": "servicios"},
                    ],
                ]
            }
            async with httpx.AsyncClient(timeout=15) as client:
                await client.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown", "reply_markup": teclado},
                )
        except Exception as e:
            logger.warning(f"No se pudo notificar: {e}")
