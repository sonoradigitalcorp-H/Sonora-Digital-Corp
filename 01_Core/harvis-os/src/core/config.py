"""Harvis OS Configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    VERSION: str = "0.1.0"
    APP_NAME: str = "Harvis OS"
    DEBUG: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # PostgreSQL
    POSTGRES_URL: str = "postgresql://harvis:harvis@localhost:5432/harvis"

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"

    # Neo4j
    NEO4J_URL: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "harvis"

    # Ollama
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

    # Logging
    LOG_LEVEL: str = "INFO"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Voice API (seguridad: si no se configura, los endpoints POST devuelven 503)
    VOICE_API_TOKEN: str = ""

    # Timeouts
    MCP_TIMEOUT: int = 30000
    AGENT_TIMEOUT: int = 600

    # Health Check
    HEALTH_CHECK_INTERVAL: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()


settings = get_settings()
