"""Sync engine — triggers open-source collectors and merges data into ABE Service."""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from ..bridges.collectors import collect_all_artists

log = logging.getLogger("abe.sync")

SYNC_LOG = Path(__file__).resolve().parent.parent.parent.parent / "state" / "logs" / "sync-history.jsonl"


class SyncEngine:
    def __init__(self, abe_service):
        self.abe = abe_service
        self._last_sync = None
        self._last_result = {}

    async def sync_now(self) -> dict:
        """Run sync cycle: collect metadata for all artists, merge into ABE data."""
        log.info("Sync cycle started")
        artists = self.abe.get_artists()

        if not artists:
            result = {"status": "skipped", "reason": "no_artists", "artists_synced": 0}
            self._record_result(result)
            return result

        collected = await collect_all_artists(artists)

        merged = 0
        errors = 0
        for data in collected:
            artist_id = data.get("artist_id", "")
            if not artist_id or data.get("error"):
                errors += 1
                continue
            artist = self.abe.get_artist(artist_id)
            if artist:
                for k, v in data.items():
                    if v is not None and k not in ("artist_id", "nombre", "source", "fetched_at", "error"):
                        artist[k] = v
                artist["last_sync"] = data.get("fetched_at", datetime.now(timezone.utc).isoformat())
                merged += 1

        self.abe._save_data()

        result = {
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_artists": len(artists),
            "artists_synced": len(collected),
            "merged": merged,
            "errors": errors,
        }
        self._record_result(result)
        log.info(f"Sync completed: {merged} merged, {errors} errors")
        return result

    def _record_result(self, result: dict):
        self._last_sync = datetime.now(timezone.utc).isoformat()
        self._last_result = result
        SYNC_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(SYNC_LOG, "a") as f:
            f.write(json.dumps(result) + "\n")

    def status(self) -> dict:
        return {
            "last_sync": self._last_sync,
            "last_result": self._last_result,
            "sync_log": str(SYNC_LOG),
        }
