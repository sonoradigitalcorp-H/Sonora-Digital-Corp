"""
ABE MUSIC — CRM de artistas, dashboard CEO, distribución, regalías.
White label de SDC para sellos discográficos digitales.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone

log = logging.getLogger("jarvis.abe")

SEED_DATA = [
    (
        {"nombre": "Hector Rubio", "genero": "Regional Mexicano", "pais": "México", "status": "active", "email": "hector@example.com"},
        [
            {"titulo": "Corazón de Piedra", "tipo": "single", "_streams": 45000, "_revenue": 3200.0, "_source": "streaming"},
            {"titulo": "Amor Eterno", "tipo": "single", "_streams": 28000, "_revenue": 2100.0, "_source": "streaming"},
            {"titulo": "Noches de Verano", "tipo": "album", "_streams": 120000, "_revenue": 8500.0, "_source": "streaming"},
        ]
    ),
    (
        {"nombre": "Jesus Urquijo", "genero": "Pop Latino", "pais": "México", "status": "active", "email": "jesus@example.com"},
        [
            {"titulo": "Bailando Contigo", "tipo": "single", "_streams": 89000, "_revenue": 6100.0, "_source": "streaming"},
            {"titulo": "Sol y Luna", "tipo": "album", "_streams": 156000, "_revenue": 11200.0, "_source": "streaming"},
        ]
    ),
    (
        {"nombre": "Javier Arvayo", "genero": "Urbano", "pais": "México", "status": "signed", "email": "javier@example.com"},
        [
            {"titulo": "Fuego", "tipo": "single", "_streams": 67000, "_revenue": 4800.0, "_source": "streaming"},
            {"titulo": "Callejero", "tipo": "single", "_streams": 34000, "_revenue": 2500.0, "_source": "streaming"},
        ]
    ),
]

ROYALTY_SPLIT = {
    "streaming": {"artist": 0.70, "label": 0.20, "distribution": 0.10},
    "merch": {"artist": 0.60, "label": 0.30, "printful": 0.10},
    "sync_license": {"artist": 0.50, "label": 0.40, "manager": 0.10},
}


class ArtistCRM:
    DEFAULT_DATA_PATH = "data/abe-music.json"

    def __init__(self, neo4j_store=None, data_path: str = None):
        self.neo4j = neo4j_store
        self.data_path = data_path
        self._artists: dict[str, dict] = {}
        self._releases: dict[str, dict] = {}
        if data_path:
            if os.path.exists(data_path):
                self._load()
            else:
                self._seed_if_empty()

    def _save(self):
        if not self.data_path:
            return
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump({"artists": self._artists, "releases": self._releases}, f, indent=2)

    def _load(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path) as f:
                    data = json.load(f)
                self._artists = data.get("artists", {})
                self._releases = data.get("releases", {})
            except Exception as e:
                log.warning(f"Failed to load data from {self.data_path}: {e}")

    def _seed_if_empty(self):
        if self._artists:
            return
        log.info("Seeding ABE MUSIC with demo data...")
        for artist_data, releases_data in SEED_DATA:
            artist = self.create_artist(artist_data, _save=False)
            for rdata in releases_data:
                release = self.create_release(artist["id"], rdata, _save=False)
                for _ in range(rdata.get("_streams", 0)):
                    self.record_stream(release["id"], _save=False)
                if rdata.get("_revenue", 0):
                    self.record_revenue(release["id"], rdata["_revenue"], rdata.get("_source", "streaming"), _save=False)
        self._save()
        log.info(f"Seeded {len(self._artists)} artists, {len(self._releases)} releases")

    def create_artist(self, data: dict, _save: bool = True) -> dict:
        artist_id = str(uuid.uuid4())[:8]
        artist = {
            "id": artist_id,
            "nombre": data.get("nombre", ""),
            "genero": data.get("genero", ""),
            "pais": data.get("pais", ""),
            "status": data.get("status", "development"),
            "email": data.get("email", ""),
            "telefono": data.get("telefono", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "streams": 0,
            "revenue": 0.0,
            "releases_count": 0,
        }
        self._artists[artist_id] = artist
        if self.neo4j:
            try:
                driver = self.neo4j.get_driver()
                if driver:
                    with driver.session() as session:
                        session.run(
                            "CREATE (a:Artist {id: $id, nombre: $nombre, genero: $genero, "
                            "pais: $pais, status: $status, streams: $streams, revenue: $revenue})",
                            **artist,
                        )
            except Exception as e:
                log.warning(f"Neo4j artist create failed: {e}")
        if _save:
            self._save()
        return artist

    def get_artist(self, artist_id: str) -> dict | None:
        return self._artists.get(artist_id)

    def list_artists(self, status: str = None) -> list[dict]:
        artists = list(self._artists.values())
        if status:
            artists = [a for a in artists if a["status"] == status]
        return sorted(artists, key=lambda a: a["revenue"], reverse=True)

    def create_release(self, artist_id: str, data: dict, _save: bool = True) -> dict | None:
        artist = self._artists.get(artist_id)
        if not artist:
            return None
        release_id = str(uuid.uuid4())[:8]
        release = {
            "id": release_id,
            "artist_id": artist_id,
            "titulo": data.get("titulo", ""),
            "tipo": data.get("tipo", "single"),
            "genero": data.get("genero", artist["genero"]),
            "fecha_lanzamiento": data.get(
                "fecha", datetime.now(timezone.utc).isoformat()
            ),
            "streams": 0,
            "revenue": 0.0,
            "status": "draft",
        }
        self._releases[release_id] = release
        artist["releases_count"] += 1
        if _save:
            self._save()
        return release

    def record_stream(self, release_id: str, amount: int = 1, _save: bool = True) -> dict | None:
        release = self._releases.get(release_id)
        if not release:
            return None
        release["streams"] += amount
        artist = self._artists.get(release["artist_id"])
        if artist:
            artist["streams"] += amount
        if _save:
            self._save()
        return release

    def record_revenue(
        self, release_id: str, amount: float, source: str = "streaming", _save: bool = True
    ) -> dict:
        release = self._releases.get(release_id)
        if not release:
            return {"error": "Release not found"}
        split = ROYALTY_SPLIT.get(source, ROYALTY_SPLIT["streaming"])
        revenue_entry = {
            "release_id": release_id,
            "amount": amount,
            "source": source,
            "split": split,
            "artist_share": round(amount * split["artist"], 2),
            "label_share": round(amount * split["label"], 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        release["revenue"] += amount
        artist = self._artists.get(release["artist_id"])
        if artist:
            artist["revenue"] += amount * split["artist"]
        if _save:
            self._save()
        return revenue_entry


class KPIDashboard:
    def __init__(self, crm: ArtistCRM):
        self.crm = crm

    def get_ceo_dashboard(self) -> dict:
        artists = self.crm.list_artists()
        releases = list(self.crm._releases.values())

        total_streams = sum(a["streams"] for a in artists)
        total_revenue = sum(a["revenue"] for a in artists)
        active_artists = len([a for a in artists if a["status"] == "active"])
        signed_artists = len([a for a in artists if a["status"] == "signed"])

        top_artists = sorted(artists, key=lambda a: a["revenue"], reverse=True)[:5]

        return {
            "total_artists": len(artists),
            "active_artists": active_artists,
            "signed_artists": signed_artists,
            "total_releases": len(releases),
            "total_streams": total_streams,
            "total_revenue": round(total_revenue, 2),
            "top_artists": [
                {
                    "nombre": a["nombre"],
                    "streams": a["streams"],
                    "revenue": a["revenue"],
                }
                for a in top_artists
            ],
            "revenue_breakdown": {
                "artists_share": round(sum(a["revenue"] for a in artists), 2),
                "label_share": round(
                    total_revenue * ROYALTY_SPLIT["streaming"]["label"], 2
                ),
            },
        }

    def get_artist_kpi(self, artist_id: str) -> dict | None:
        artist = self.crm.get_artist(artist_id)
        if not artist:
            return None
        releases = [
            r for r in self.crm._releases.values() if r["artist_id"] == artist_id
        ]
        return {
            "artist": artist["nombre"],
            "status": artist["status"],
            "total_streams": artist["streams"],
            "total_revenue": artist["revenue"],
            "releases": len(releases),
            "genero": artist["genero"],
            "revenue_per_stream": (
                round(artist["revenue"] / artist["streams"], 4)
                if artist["streams"] > 0
                else 0
            ),
        }
