import json
import os
from database import query_db

DATA_DIR = os.environ.get("ABE_DATA_DIR", "/home/ubuntu/abe-api/data")

TABLE_MAP = {
    "services": "services",
    "artists": "artists",
    "users": "users",
    "contacts": "contacts",
}

class StorageService:
    @staticmethod
    def load(name: str) -> list:
        table = TABLE_MAP.get(name)
        if not table:
            return StorageService._load_json(name)
        rows = query_db(f"SELECT * FROM {table} ORDER BY created_at DESC")
        return rows

    @staticmethod
    def save(name: str, data: list):
        table = TABLE_MAP.get(name)
        if not table:
            return StorageService._save_json(name, data)
        pass

    @staticmethod
    def load_abe_music():
        path = "/home/ubuntu/sonora-digital-corp/data/abe-music.json"
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return {}

    @staticmethod
    def _load_json(name: str):
        path = os.path.join(DATA_DIR, f"{name}.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return []

    @staticmethod
    def _save_json(name: str, data: list):
        path = os.path.join(DATA_DIR, f"{name}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
