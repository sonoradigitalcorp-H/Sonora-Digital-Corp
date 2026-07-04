"""Evolution Store — propuestas persistentes"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent.parent


class EvolutionStore:
    PROPOSALS_FILE = REPO / "state" / "evolution" / "proposals.jsonl"
    DECISIONS_FILE = REPO / "state" / "evolution" / "decisions.json"

    def __init__(self):
        self.PROPOSALS_FILE.parent.mkdir(parents=True, exist_ok=True)

    def save_proposal(self, proposal: dict) -> str:
        import uuid
        pid = f"prop_{uuid.uuid4().hex[:8]}"
        proposal["id"] = pid
        proposal["created_at"] = datetime.now(timezone.utc).isoformat()
        proposal["status"] = "proposed"
        with open(self.PROPOSALS_FILE, "a") as f:
            f.write(json.dumps(proposal) + "\n")
        return pid

    def list_proposals(self, limit: int = 20, status: str = None) -> list[dict]:
        if not self.PROPOSALS_FILE.exists():
            return []
        proposals = []
        with open(self.PROPOSALS_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    p = json.loads(line)
                    if status and p.get("status") != status:
                        continue
                    proposals.append(p)
        return proposals[-limit:]

    def update_status(self, proposal_id: str, status: str, notes: str = None):
        proposals = self.list_proposals(limit=10000)
        updated = []
        found = False
        for p in proposals:
            if p["id"] == proposal_id:
                p["status"] = status
                p["updated_at"] = datetime.now(timezone.utc).isoformat()
                if notes:
                    p["notes"] = notes
                found = True
            updated.append(p)
        if found:
            with open(self.PROPOSALS_FILE, "w") as f:
                for p in updated:
                    f.write(json.dumps(p) + "\n")

    def save_decision(self, proposal_id: str, decision: str, reason: str = None):
        decisions = {}
        if self.DECISIONS_FILE.exists():
            decisions = json.loads(self.DECISIONS_FILE.read_text())
        decisions[proposal_id] = {
            "decision": decision,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.DECISIONS_FILE.write_text(json.dumps(decisions, indent=2))
