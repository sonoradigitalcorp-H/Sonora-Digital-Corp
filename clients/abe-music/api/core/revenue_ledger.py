import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .contract_engine import ContractEngine

log = logging.getLogger("abe.revenue")

LEDGER_FILE = Path(__file__).resolve().parent.parent.parent.parent / "data" / "abe-ledger.json"


class RevenueLedger:
    def __init__(self, contract_engine: ContractEngine):
        self.contracts = contract_engine
        self._entries: list[dict] = []
        self._load()

    def _load(self):
        if LEDGER_FILE.exists():
            try:
                with open(LEDGER_FILE) as f:
                    self._entries = json.load(f).get("entries", [])
            except Exception as e:
                log.warning(f"Failed to load ledger: {e}")

    def _save(self):
        LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LEDGER_FILE, "w") as f:
            json.dump({"entries": self._entries}, f, indent=2, ensure_ascii=False)

    def record(
        self,
        contract_id: str,
        artist_id: str,
        release_id: str,
        amount: float,
        source: str = "streaming",
    ) -> dict:
        split = self.contracts.get_split(contract_id, source)

        entry = {
            "id": str(uuid.uuid4())[:8],
            "contract_id": contract_id,
            "artist_id": artist_id,
            "release_id": release_id,
            "amount": round(amount, 2),
            "source": source,
            "split": split,
            "artist_share": round(amount * split.get("artist", 0.7), 2),
            "label_share": round(amount * split.get("label", 0.2), 2),
            "distributor_share": round(amount * split.get("distributor", 0.1), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._entries.append(entry)
        self._save()
        return entry

    def get_by_artist(self, artist_id: str) -> list[dict]:
        return [e for e in self._entries if e["artist_id"] == artist_id]

    def get_by_contract(self, contract_id: str) -> list[dict]:
        return [e for e in self._entries if e["contract_id"] == contract_id]

    def get_by_release(self, release_id: str) -> list[dict]:
        return [e for e in self._entries if e["release_id"] == release_id]

    def summary(self, artist_id: str = None) -> dict:
        entries = self._entries
        if artist_id:
            entries = self.get_by_artist(artist_id)

        total = sum(e["amount"] for e in entries)
        by_source: dict[str, float] = {}
        for e in entries:
            by_source[e["source"]] = by_source.get(e["source"], 0) + e["amount"]

        return {
            "total_entries": len(entries),
            "total_revenue": round(total, 2),
            "artist_total": round(sum(e["artist_share"] for e in entries), 2),
            "label_total": round(sum(e["label_share"] for e in entries), 2),
            "distributor_total": round(sum(e["distributor_share"] for e in entries), 2),
            "by_source": {k: round(v, 2) for k, v in sorted(by_source.items(), key=lambda x: -x[1])},
        }
