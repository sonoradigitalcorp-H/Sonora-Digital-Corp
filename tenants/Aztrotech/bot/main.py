import os
import yaml
import logging
from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler
from router import ModelRouter
from handlers.telegram import TelegramHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def load_config():
    path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    with open(path) as f:
        cfg = yaml.safe_load(f)
    cfg["openrouter"]["api_key"] = os.getenv("OPENROUTER_API_KEY")
    if not cfg["openrouter"]["api_key"]:
        raise ValueError("OPENROUTER_API_KEY env var required")
    return cfg


def main():
    config = load_config()
    router = ModelRouter(config)

    # ── Conversation Engine (RAG-first + memoria + guardrails) ──
    # Se crea/arranca dentro del loop del bot vía post_init
    try:
        from conversation_engine import create_engine, EngineConfig
        engine = create_engine(EngineConfig(tenant_id="aztrotech"))
        logger.info("ConversationEngine creado (se arrancará en post_init)")
    except Exception as e:
        logger.warning(f"Engine no disponible, modo simple: {e}")
        engine = None

    async def post_init(application):
        if engine is not None:
            try:
                await engine.start()
                logger.info("ConversationEngine iniciado (RAG-first)")
            except Exception as e:
                logger.warning(f"Engine start falló: {e}")

    handler = TelegramHandler(config, router, engine=engine)

    app = (
        Application.builder()
        .token(config["channels"]["telegram"]["bot_token"])
        .post_init(post_init)
        .build()
    )

    app.add_handler(CallbackQueryHandler(handler.handle_callback))
    app.add_handler(MessageHandler(filters.VOICE, handler.handle_voice_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_message))

    logger.info("Aztrotech AI iniciado")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
