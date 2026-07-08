"""sync-artist-data capability — actual logic (HAS-005)
Syncs artist data from all configured providers.
Delegates to scrapers/sync.py for the heavy lifting.
"""
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent.parent.parent


async def run(artist_id: str | None = None, full_sync: bool = False) -> dict:
    sync_path = REPO / "scrapers" / "sync.py"
    if not sync_path.exists():
        return {"status": "error", "error": "scrapers/sync.py not found"}

    # Ensure scrapers.sync is importable
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))

    from scrapers.sync import sync_artist, run_sync_cycle

    if full_sync and not artist_id:
        result = run_sync_cycle()
        return {"status": "success", "artists_synced": len(result) if result else 0, "full_sync": True}

    if artist_id:
        result = sync_artist(artist_id)
        return {"status": "success" if result.get("updated") else "no_changes", "artist_id": artist_id, "delta": result.get("delta", {})}

    return {"status": "error", "error": "provide artist_id or full_sync=true"}
