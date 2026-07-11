import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("abe.distribution")

DISTRO_FILE = Path(__file__).resolve().parent.parent.parent.parent / "data" / "abe-distribution.json"

PLATFORMS = [
    "spotify", "apple_music", "deezer", "amazon_music",
    "youtube_music", "tidal", "pandora", "claro_musica",
]


class DistributionEngine:
    def __init__(self):
        self._releases: dict[str, dict] = {}
        self._load()

    def _load(self):
        if DISTRO_FILE.exists():
            try:
                with open(DISTRO_FILE) as f:
                    self._releases = json.load(f).get("releases", {})
            except Exception as e:
                log.warning(f"Failed to load distribution data: {e}")

    def _save(self):
        DISTRO_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DISTRO_FILE, "w") as f:
            json.dump({"releases": self._releases}, f, indent=2, ensure_ascii=False)

    def create_release(
        self,
        artist_id: str,
        title: str,
        album_type: str = "single",
        genre: str = "",
        upc: str = None,
        isrc: str = None,
        platforms: list[str] = None,
    ) -> dict:
        rid = str(uuid.uuid4())[:8]
        release = {
            "id": rid,
            "artist_id": artist_id,
            "title": title,
            "type": album_type,
            "genre": genre,
            "upc": upc or f"ABE{rid.upper()}",
            "isrc": isrc or f"MX{rid.upper()}00001",
            "platforms": platforms or PLATFORMS,
            "status": "draft",
            "streams": 0,
            "revenue": 0.0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "released_at": None,
        }
        self._releases[rid] = release
        self._save()
        return release

    def get_release(self, release_id: str) -> dict | None:
        return self._releases.get(release_id)

    def list_releases(self, artist_id: str = None, status: str = None) -> list[dict]:
        releases = list(self._releases.values())
        if artist_id:
            releases = [r for r in releases if r["artist_id"] == artist_id]
        if status:
            releases = [r for r in releases if r["status"] == status]
        return sorted(releases, key=lambda r: r.get("created_at", ""), reverse=True)

    def publish_release(self, release_id: str) -> dict | None:
        r = self._releases.get(release_id)
        if not r:
            return None
        r["status"] = "published"
        r["released_at"] = datetime.now(timezone.utc).isoformat()
        self._save()
        return r

    def update_platforms(self, release_id: str, platforms: list[str]) -> dict | None:
        r = self._releases.get(release_id)
        if not r:
            return None
        r["platforms"] = platforms
        self._save()
        return r

    def get_distribution_status(self, release_id: str) -> dict:
        r = self._releases.get(release_id)
        if not r:
            return {"error": "Release not found"}
        return {
            "release": r["title"],
            "upc": r["upc"],
            "isrc": r["isrc"],
            "platforms": r["platforms"],
            "status": r["status"],
        }
