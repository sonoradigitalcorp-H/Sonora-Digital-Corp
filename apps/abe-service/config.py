import json
import os
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent.parent.parent
DEFAULT_CONFIG_PATH = BASE / "config" / "abe-system.json"
DEFAULT_DATA_PATH = BASE / "data" / "abe-music.json"
EVENTS_PATH = BASE / "state" / "logs" / "events.jsonl"


class ABEConfig:
    def __init__(self, config_path: str | Path = DEFAULT_CONFIG_PATH):
        self._raw: dict[str, Any] = {}
        if Path(config_path).exists():
            with open(config_path) as f:
                self._raw = json.load(f).get("abe_music", {})

    @property
    def name(self) -> str:
        return self._raw.get("name", "ABE Music Inc")

    @property
    def tenant_id(self) -> str:
        return self._raw.get("tenant_id", "abe-fenix")

    @property
    def jwt_secret(self) -> str:
        return os.environ.get(
            "ABE_JWT_SECRET",
            "abe_music_jwt_secret_dev_change_in_prod_2026",
        )

    @property
    def mcp_gateway_url(self) -> str:
        return os.environ.get("MCP_GATEWAY_URL", "http://127.0.0.1:18989")

    @property
    def mcp_client_id(self) -> str:
        return os.environ.get("MCP_CLIENT_ID", "sdc-core")

    @property
    def mcp_client_secret(self) -> str:
        return os.environ.get(
            "MCP_CLIENT_SECRET",
            "sdc_secret_ent3rpr1s3_k3y_2026",
        )

    @property
    def qdrant_url(self) -> str:
        return os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")

    @property
    def ws_port(self) -> int:
        return int(os.environ.get("ABE_WS_PORT", "5180"))

    @property
    def ws_host(self) -> str:
        return os.environ.get("ABE_WS_HOST", "127.0.0.1")

    @property
    def brand_colors(self) -> dict:
        return self._raw.get("brand", {}).get("colors", {})

    @property
    def agents(self) -> dict:
        return self._raw.get("agents", {})

    @property
    def workflows(self) -> dict:
        return self._raw.get("workflows", {})

    @property
    def spotify(self) -> dict:
        return self._raw.get("integrations", {}).get("spotify", {})

    @property
    def metrics(self) -> dict:
        return self._raw.get("metrics", {})

    @property
    def openclaw_url(self) -> str:
        return os.environ.get("OPENCLAW_URL", "http://127.0.0.1:18789")

    @property
    def royalty_split(self) -> dict:
        return self._raw.get("royalty_split", {
            "streaming": {"artist": 0.70, "label": 0.20, "distributor": 0.10},
            "merch": {"artist": 0.60, "label": 0.30, "distributor": 0.10},
            "sync_license": {"artist": 0.50, "label": 0.40, "distributor": 0.10},
        })


config = ABEConfig()
