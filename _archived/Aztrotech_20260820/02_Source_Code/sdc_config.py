"""SDC Centralized Config — single source of truth for API keys, DB connections, MCP.

Usage:
    from sdc_config import get_config, get_db_url
    cfg = get_config()
    print(cfg.openrouter_api_key)

Why: Avoid hardcoded DEFAULTS scattered across conversation_engine.py, persistence.py, server.py.
     All env vars + ~/.hermes/.env loaded once, validated at import.
"""
import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent
HERMES_ENV = Path.home() / ".hermes" / ".env"


def _load_env_file(path: Path, override: bool = False):
    """Carga variables de .env si existen, sin sobreescribir si ya están seteadas."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if override or key not in os.environ:
            os.environ[key] = val


# Load from hermes env first (canonical), then project .env
_load_env_file(HERMES_ENV)
_load_env_file(PROJECT_ROOT / ".env")


@dataclass
class SdccConfig:
    # API Keys
    openrouter_api_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    mercado_pago_token: str = field(default_factory=lambda: os.getenv("MERCADO_PAGO_ACCESS_TOKEN", ""))

    # Databases
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "postgresql://sdc:sdc_local_dev@localhost:5432/sdc"))
    qdrant_url: str = field(default_factory=lambda: os.getenv("QDRANT_URL", "http://localhost:6333"))
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))

    # Telegram
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))

    # Server
    server_host: str = field(default_factory=lambda: os.getenv("SDC_SERVER_HOST", "0.0.0.0"))
    server_port: int = field(default_factory=lambda: int(os.getenv("SDC_SERVER_PORT", "5289")))

    # OpenRouter
    openrouter_base_url: str = field(default_factory=lambda: os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"))

    # Twilio (WhatsApp voice delivery)
    twilio_account_sid: str = field(default_factory=lambda: os.getenv("TWILIO_ACCOUNT_SID", ""))
    twilio_auth_token: str = field(default_factory=lambda: os.getenv("TWILIO_AUTH_TOKEN", ""))

    # Edge TTS voices
    voice_telegram: str = field(default_factory=lambda: os.getenv("VOICE_TELEGRAM", "es-MX-DaliaNeural"))
    voice_whatsapp: str = field(default_factory=lambda: os.getenv("VOICE_WHATSAPP", "es-MX-JorgeNeural"))

    # Obsidian integration
    obsidian_vault_path: Optional[str] = field(default_factory=lambda: os.getenv("OBSIDIAN_VAULT_PATH", ""))

    def validate(self) -> Dict[str, bool]:
        return {
            "openrouter_api_key": bool(self.openrouter_api_key),
            "database_url": bool(self.database_url),
            "telegram_bot_token": bool(self.telegram_bot_token),
            "twilio_configured": bool(self.twilio_account_sid and self.twilio_auth_token),
            "obsidian_configured": bool(self.obsidian_vault_path),
        }


_config: Optional[SdccConfig] = None


def get_config() -> SdccConfig:
    global _config
    if _config is None:
        _config = SdccConfig()
    return _config


def get_db_url() -> str:
    return get_config().database_url


def get_llm_key() -> str:
    return get_config().openrouter_api_key
