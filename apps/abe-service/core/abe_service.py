import json
import logging
from pathlib import Path
from typing import Any

from ..config import config
from ..models import CEODashboard
from .chat_engine import ChatEngine
from .contract_engine import ContractEngine
from .crm import CRM
from .distribution import DistributionEngine
from .rag_engine import RAGEngine
from .revenue_ledger import RevenueLedger
from .sync_engine import SyncEngine
from .voice_pipeline import VoicePipeline

log = logging.getLogger("abe.service")

DATA_FILE = Path(config._raw.get("data_path", Path(__file__).resolve().parent.parent.parent.parent / "data" / "abe-music.json"))


class ABEService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._data: dict[str, Any] = self._load_data()
        self.rag = RAGEngine()
        self.chat = ChatEngine(self.rag)
        self.contracts = ContractEngine()
        self.revenue = RevenueLedger(self.contracts)
        self.distribution = DistributionEngine()
        self.crm = CRM()
        self.voice = VoicePipeline(chat_engine=self.chat)
        self.sync = SyncEngine(self)
        log.info("ABE Service initialized")

    def _load_data(self) -> dict:
        if DATA_FILE.exists():
            with open(DATA_FILE) as f:
                return json.load(f)
        return {"artists": {}, "releases": {}}

    def reload_data(self):
        self._data = self._load_data()
        log.info("Data reloaded from disk")

    def _save_data(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get_artists(self, status: str = None) -> list[dict]:
        artists = list(self._data.get("artists", {}).values())
        if status:
            return [a for a in artists if a.get("status") == status]
        return sorted(artists, key=lambda a: a.get("revenue", 0), reverse=True)

    def get_artist(self, artist_id: str) -> dict | None:
        return self._data.get("artists", {}).get(artist_id)

    def get_releases(self, artist_id: str = None) -> list[dict]:
        releases = list(self._data.get("releases", {}).values())
        if artist_id:
            return [r for r in releases if r.get("artist_id") == artist_id]
        return releases

    def get_ceo_dashboard(self) -> CEODashboard:
        artists = self.get_artists()
        releases = self.get_releases()
        contracts = self.contracts.list_contracts()

        total_streams = sum(a.get("streams", 0) for a in artists)
        total_revenue = sum(a.get("revenue", 0) for a in artists)
        active = len([a for a in artists if a.get("status") == "active"])
        top = sorted(artists, key=lambda a: a.get("revenue", 0), reverse=True)[:5]

        return CEODashboard(
            total_artists=len(artists),
            active_artists=active,
            total_streams=total_streams,
            total_revenue=total_revenue,
            total_releases=len(releases),
            total_contracts=len(contracts),
            top_artists=[{"name": a.get("nombre", ""), "streams": a.get("streams", 0), "revenue": a.get("revenue", 0)} for a in top],
            pending_contracts=len([c for c in contracts if c.get("status") == "draft"]),
            generated_at=__import__("datetime").datetime.now().isoformat(),
        )

    def record_stream(self, release_id: str, amount: int = 1) -> dict:
        for a in self._data.get("artists", {}).values():
            for r in a.get("releases", []):
                if r.get("id") == release_id or r.get("titulo") == release_id:
                    r["streams"] = (r.get("streams", 0) + amount)
                    a["streams"] = (a.get("streams", 0) + amount)
                    self._save_data()
                    return {"status": "recorded", "release_id": release_id, "amount": amount}
        return {"error": "Release not found"}


abe_service = ABEService()
