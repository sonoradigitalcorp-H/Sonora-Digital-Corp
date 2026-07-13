from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    seedance_api_key: str = "sk_test_mock"
    seedance_base_url: str = "http://studio-mock:3099"
    redis_url: str = "redis://redis:6379"
    storage_path: str = "/data/videos"
    storage_public_url: str = "http://localhost:3020/static"
    webhook_base_url: str = "http://studio-webhook:3021"
    mock_mode: bool = True
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_prefix = "STUDIO_"

settings = Settings()
