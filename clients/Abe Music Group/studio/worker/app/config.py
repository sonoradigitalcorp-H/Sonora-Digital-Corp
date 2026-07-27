from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    seedance_api_key: str = "sk_test_mock"
    seedance_base_url: str = "http://studio-mock:3099"
    redis_url: str = "redis://redis:6379"
    studio_api_url: str = "http://studio-api:3020"
    poll_interval: int = 10
    log_level: str = "INFO"
    class Config:
        env_file = ".env"
        env_prefix = "STUDIO_"

settings = Settings()
