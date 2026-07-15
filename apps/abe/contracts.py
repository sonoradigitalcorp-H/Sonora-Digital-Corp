import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from ..models import ContractType, RevenueSplit

log = logging.getLogger("abe.contracts")

CONTRACTS_FILE = Path(__file__).resolve().parent.parent.parent.parent / "data" / "abe-contracts.json"

DEFAULT_SPLITS: dict[str, RevenueSplit] = {
    "streaming": RevenueSplit(artist=0.70, label=0.20, distributor=0.10, manager=0.0, producer=0.0),
    "merch": RevenueSplit(artist=0.60, label=0.30, distributor=0.10, manager=0.0, producer=0.0),
    "sync_license": RevenueSplit(artist=0.50, label=0.40, distributor=0.10, manager=0.0, producer=0.0),
}


class ContractEngine:
    def __init__(self):
        self._contracts: dict[str, dict] = {}
        self._load()

    def _load(self):
        if CONTRACTS_FILE.exists():
            try:
                with open(CONTRACTS_FILE) as f:
                    self._contracts = json.load(f).get("contracts", {})
            except Exception as e:
                log.warning(f"Failed to load contracts: {e}")

    def _save(self):
        CONTRACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONTRACTS_FILE, "w") as f:
            json.dump({"contracts": self._contracts}, f, indent=2, ensure_ascii=False)

    def create_contract(
        self,
        artist_id: str,
        contract_type: ContractType,
        revenue_splits: dict[str, dict] = None,
        start_date: str = None,
        end_date: str = None,
        territories: list[str] = None,
        platforms: list[str] = None,
    ) -> dict:
        cid = str(uuid.uuid4())[:8]
        splits = {}
        if revenue_splits:
            for source, s in revenue_splits.items():
                splits[source] = RevenueSplit(**s).model_dump()
        else:
            splits = {k: v.model_dump() for k, v in DEFAULT_SPLITS.items()}

        contract = {
            "id": cid,
            "artist_id": artist_id,
            "type": contract_type.value if isinstance(contract_type, ContractType) else contract_type,
            "start_date": start_date or datetime.now(timezone.utc).isoformat(),
            "end_date": end_date,
            "revenue_splits": splits,
            "territories": territories or ["worldwide"],
            "platforms": platforms or ["all"],
            "status": "draft",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._contracts[cid] = contract
        self._save()
        return contract

    def get_contract(self, contract_id: str) -> dict | None:
        return self._contracts.get(contract_id)

    def list_contracts(self, artist_id: str = None, status: str = None) -> list[dict]:
        contracts = list(self._contracts.values())
        if artist_id:
            contracts = [c for c in contracts if c["artist_id"] == artist_id]
        if status:
            contracts = [c for c in contracts if c["status"] == status]
        return sorted(contracts, key=lambda c: c.get("created_at", ""), reverse=True)

    def update_status(self, contract_id: str, status: str) -> dict | None:
        c = self._contracts.get(contract_id)
        if not c:
            return None
        c["status"] = status
        self._save()
        return c

    def update_splits(self, contract_id: str, revenue_type: str, splits: dict) -> dict | None:
        c = self._contracts.get(contract_id)
        if not c:
            return None
        c["revenue_splits"][revenue_type] = RevenueSplit(**splits).model_dump()
        self._save()
        return c

    def get_split(self, contract_id: str, revenue_type: str) -> dict | None:
        c = self._contracts.get(contract_id)
        if not c:
            return DEFAULT_SPLITS.get(revenue_type, DEFAULT_SPLITS["streaming"]).model_dump()
        return c["revenue_splits"].get(
            revenue_type,
            DEFAULT_SPLITS.get(revenue_type, DEFAULT_SPLITS["streaming"]).model_dump(),
        )
