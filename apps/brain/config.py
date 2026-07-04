from pydantic_settings import BaseSettings

class BrainConfig(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "sdc-neo4j-p4ss"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    engram_path: str = "state/engram.db"
    hermes_state_path: str = "/home/ubuntu/.hermes/state.db"
    events_path: str = "state/logs/events.jsonl"
    embed_model: str = "all-MiniLM-L6-v2"
    embed_device: str = "cpu"
    sync_interval_minutes: int = 30

    class Config:
        env_prefix = "BRAIN_"
