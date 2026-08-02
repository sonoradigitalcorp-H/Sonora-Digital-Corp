import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "info")
    secret_key: str = os.getenv("SECRET_KEY", "change-me")

    # fal.ai
    fal_key: str = os.getenv("FAL_API_KEY", "")

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Twilio
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_phone: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    twilio_whatsapp: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

    # Owner
    owner_phone: str = os.getenv("OWNER_PHONE_NUMBER", "")
    owner_name: str = os.getenv("OWNER_NAME", "Admin")

    # fal.ai config
    fal_talking_head_model: str = os.getenv("FAL_TALKING_HEAD_MODEL", "sync-lipsync/v3/image-to-video")
    fal_tts_model: str = os.getenv("FAL_TTS_MODEL", "bytedance/seed-audio-1.0")

    # Costs
    max_video_cost_usd: float = float(os.getenv("MAX_VIDEO_COST_USD", "0.50"))
    daily_budget_usd: float = float(os.getenv("DAILY_BUDGET_USD", "20.00"))

    # Base URL
    base_url: str = os.getenv("BASE_URL", "http://localhost:8000")

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # FAL API
    fal_api_url: str = os.getenv("FAL_API_URL", "http://fal-wrapper:8001")

    # Product pricing
    product_prices = {
        "avatar_mensual": 97.00,
        "video_bienvenida": 15.00,
        "asistente_ventas": 100.00,
    }

settings = Settings()
