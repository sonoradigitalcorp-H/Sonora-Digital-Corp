import json
import logging
from datetime import datetime
from typing import Optional
from redis import Redis
from core.config import settings

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    # === Orders ===

    def save_order(self, order_dict: dict):
        key = f"order:{order_dict['id']}"
        self.redis.hset(key, mapping=order_dict)
        self.redis.expire(key, 604800)

    def get_order(self, order_id: str) -> Optional[dict]:
        data = self.redis.hgetall(f"order:{order_id}")
        if not data:
            return None
        data["total_cost"] = float(data.get("total_cost", 0))
        data["duration"] = int(data.get("duration", 30))
        if "timeline" in data and isinstance(data["timeline"], str):
            data["timeline"] = json.loads(data["timeline"])
        return data

    def update_order_status(self, order_id: str, status: str, extra: dict = None):
        key = f"order:{order_id}"
        self.redis.hset(key, "status", status)
        timeline_entry = {"event": status, "at": datetime.utcnow().isoformat()}
        timeline_json = self.redis.hget(key, "timeline")
        if timeline_json:
            timeline = json.loads(timeline_json)
        else:
            timeline = []
        timeline.append(timeline_entry)
        self.redis.hset(key, "timeline", json.dumps(timeline))
        if extra:
            for k, v in extra.items():
                if isinstance(v, (dict, list)):
                    v = json.dumps(v)
                self.redis.hset(key, k, str(v) if not isinstance(v, str) else v)

    def list_orders(self, status: str = None, limit: int = 50) -> list:
        pattern = "order:*"
        keys = self.redis.keys(pattern)
        orders = []
        for key in keys:
            data = self.redis.hgetall(key)
            if data:
                data["total_cost"] = float(data.get("total_cost", 0))
                if "timeline" in data and isinstance(data["timeline"], str):
                    data["timeline"] = json.loads(data["timeline"])
                if status is None or data.get("status") == status:
                    orders.append(data)
        orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return orders[:limit]

    # === Clients ===

    def save_client(self, client_dict: dict):
        key = f"client:{client_dict['phone']}"
        self.redis.hset(key, mapping=client_dict)

    def get_client(self, phone: str) -> Optional[dict]:
        data = self.redis.hgetall(f"client:{phone}")
        if not data:
            return None
        data["total_orders"] = int(data.get("total_orders", 0))
        return data

    # === Metrics ===

    def increment_counter(self, name: str, amount: float = 1.0):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        self.redis.hincrbyfloat(f"metrics:{today}", name, amount)

    def get_todays_metrics(self) -> dict:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        data = self.redis.hgetall(f"metrics:{today}")
        return {k: float(v) if v.replace(".", "").isdigit() else v for k, v in data.items()}


db = Database()
