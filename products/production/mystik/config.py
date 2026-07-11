from pathlib import Path
from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict


class MystikConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MYSTIK_", env_file=".env")

    host: str = "0.0.0.0"
    port: int = 5200

    opencode_key: str = ""
    openrouter_key: str = ""
    llm_model: str = "deepseek/deepseek-chat"

    whisper_model: str = "base"
    openvoice_model: str = "base"

    twenty_api_url: str = "http://127.0.0.1:3000"
    twenty_api_key: str = ""

    chroma_host: str = "127.0.0.1"
    chroma_port: int = 8001

    omnivoice_url: str = "http://127.0.0.1:3900"
    content_studio_url: str = "http://127.0.0.1:8765"
    abe_crm_url: str = "http://127.0.0.1:5180"

    lobe_url: str = "http://127.0.0.1:3210"
    lobe_api_key: str = "mystik-lobe-key"

    default_tenant: str = "sonora"
    tenant_db_path: str = "state/mystik/tenants.db"


config = MystikConfig()
