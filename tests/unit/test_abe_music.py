"""Tests for ABE MUSIC (spec 011) — CRM, dashboard, royalties."""

import pytest
from src.core.abe_music import ArtistCRM, KPIDashboard, ROYALTY_SPLIT


class TestArtistCRM:
    def test_create_artist(self):
        crm = ArtistCRM()
        artist = crm.create_artist({
            "nombre": "Artista Test",
            "genero": "Reggaeton",
            "pais": "PR",
            "status": "development",
        })
        assert artist["nombre"] == "Artista Test"
        assert artist["status"] == "development"
        assert artist["streams"] == 0
        assert artist["revenue"] == 0.0

    def test_get_artist(self):
        crm = ArtistCRM()
        created = crm.create_artist({"nombre": "Test"})
        assert crm.get_artist(created["id"]) is not None

    def test_get_nonexistent(self):
        crm = ArtistCRM()
        assert crm.get_artist("nonexistent") is None

    def test_list_artists(self):
        crm = ArtistCRM()
        crm.create_artist({"nombre": "A1", "genero": "Pop"})
        crm.create_artist({"nombre": "A2", "genero": "Rock"})
        assert len(crm.list_artists()) == 2

    def test_list_by_status(self):
        crm = ArtistCRM()
        crm.create_artist({"nombre": "A1", "status": "active"})
        crm.create_artist({"nombre": "A2", "status": "development"})
        active = crm.list_artists("active")
        assert len(active) == 1
        assert active[0]["nombre"] == "A1"

    def test_create_release(self):
        crm = ArtistCRM()
        artist = crm.create_artist({"nombre": "Test"})
        release = crm.create_release(artist["id"], {
            "titulo": "Mi Tema",
            "tipo": "single",
            "genero": "Reggaeton",
        })
        assert release is not None
        assert release["titulo"] == "Mi Tema"
        assert release["status"] == "draft"

    def test_create_release_nonexistent_artist(self):
        crm = ArtistCRM()
        assert crm.create_release("nonexistent", {"titulo": "Test"}) is None

    def test_record_stream(self):
        crm = ArtistCRM()
        artist = crm.create_artist({"nombre": "Test"})
        release = crm.create_release(artist["id"], {"titulo": "Tema"})
        crm.record_stream(release["id"], 100)
        assert release["streams"] == 100
        assert artist["streams"] == 100

    def test_record_stream_increments(self):
        crm = ArtistCRM()
        artist = crm.create_artist({"nombre": "Test"})
        release = crm.create_release(artist["id"], {"titulo": "Tema"})
        for _ in range(5):
            crm.record_stream(release["id"], 1000)
        assert release["streams"] == 5000

    def test_record_revenue(self):
        crm = ArtistCRM()
        artist = crm.create_artist({"nombre": "Test"})
        release = crm.create_release(artist["id"], {"titulo": "Tema"})
        rev = crm.record_revenue(release["id"], 1000, "streaming")
        assert rev["amount"] == 1000
        assert rev["artist_share"] == 700.0
        assert rev["label_share"] == 200.0

    def test_revenue_adds_to_artist(self):
        crm = ArtistCRM()
        artist = crm.create_artist({"nombre": "Test"})
        release = crm.create_release(artist["id"], {"titulo": "Tema"})
        crm.record_revenue(release["id"], 1000, "streaming")
        assert artist["revenue"] == 700.0

    def test_different_revenue_splits(self):
        crm = ArtistCRM()
        artist = crm.create_artist({"nombre": "Test"})
        release = crm.create_release(artist["id"], {"titulo": "Tema"})
        crm.record_revenue(release["id"], 1000, "merch")
        crm.record_revenue(release["id"], 1000, "sync_license")
        assert artist["revenue"] == 1100.0  # 600 + 500

    def test_list_sorted_by_revenue(self):
        crm = ArtistCRM()
        a1 = crm.create_artist({"nombre": "Top"})
        a2 = crm.create_artist({"nombre": "Low"})
        r1 = crm.create_release(a1["id"], {"titulo": "T1"})
        r2 = crm.create_release(a2["id"], {"titulo": "T2"})
        crm.record_revenue(r1["id"], 5000)
        crm.record_revenue(r2["id"], 100)
        artists = crm.list_artists()
        assert artists[0]["nombre"] == "Top"


class TestKPIDashboard:
    def test_ceo_dashboard(self):
        crm = ArtistCRM()
        kpi = KPIDashboard(crm)
        dash = kpi.get_ceo_dashboard()
        assert dash["total_artists"] == 0
        assert dash["total_revenue"] == 0.0

    def test_ceo_dashboard_with_data(self):
        crm = ArtistCRM()
        a1 = crm.create_artist({"nombre": "Artista 1", "status": "active"})
        a2 = crm.create_artist({"nombre": "Artista 2", "status": "signed"})
        r1 = crm.create_release(a1["id"], {"titulo": "T1"})
        r2 = crm.create_release(a2["id"], {"titulo": "T2"})
        crm.record_revenue(r1["id"], 1000)
        crm.record_stream(r1["id"], 500)
        crm.record_stream(r1["id"], 300)

        kpi = KPIDashboard(crm)
        dash = kpi.get_ceo_dashboard()
        assert dash["total_artists"] == 2
        assert dash["active_artists"] == 1
        assert dash["signed_artists"] == 1
        assert dash["total_streams"] == 800
        assert dash["total_revenue"] == 700.0  # solo la parte del artista
        assert len(dash["top_artists"]) == 2

    def test_artist_kpi(self):
        crm = ArtistCRM()
        a = crm.create_artist({"nombre": "Test", "genero": "Pop"})
        r = crm.create_release(a["id"], {"titulo": "Tema"})
        crm.record_stream(r["id"], 1000)
        crm.record_revenue(r["id"], 500)

        kpi = KPIDashboard(crm)
        result = kpi.get_artist_kpi(a["id"])
        assert result["artist"] == "Test"
        assert result["total_streams"] == 1000
        assert result["total_revenue"] == 350.0

    def test_artist_kpi_not_found(self):
        kpi = KPIDashboard(ArtistCRM())
        assert kpi.get_artist_kpi("nonexistent") is None

    def test_top_artists_limit(self):
        crm = ArtistCRM()
        for i in range(10):
            a = crm.create_artist({"nombre": f"Artista {i}"})
            r = crm.create_release(a["id"], {"titulo": f"T{i}"})
            crm.record_revenue(r["id"], (10 - i) * 100)
        kpi = KPIDashboard(crm)
        dash = kpi.get_ceo_dashboard()
        assert len(dash["top_artists"]) == 5
        assert dash["top_artists"][0]["nombre"] == "Artista 0"
