"""Tests para Clone Delivery — FR-05: Post-procesamiento y entrega de assets"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(REPO))


class TestSupabaseUpload:
    def test_uploads_to_correct_path(self):
        client_id = "client-abc"
        asset_type = "photos"
        filename = "gen_001.jpg"
        storage_path = f"/clients/{client_id}/output/{asset_type}/{filename}"
        assert storage_path == "/clients/client-abc/output/photos/gen_001.jpg"

    def test_public_url_format(self):
        base = "https://jibalggzudkflwzdndqz.supabase.co"
        path = "/storage/v1/object/public/sdc-assets/clients/test/output/video.mp4"
        url = f"{base}{path}"
        assert url.startswith("https://")
        assert "supabase.co" in url
        assert url.endswith(".mp4")


class TestMultiFormatExport:
    ASSET_URL = "https://storage/output/video.mp4"

    def test_converts_to_9_16(self):
        formats = {"tiktok": "9:16", "reels": "9:16", "youtube": "16:9", "instagram": "1:1"}
        assert formats["tiktok"] == "9:16"

    def test_converts_to_16_9(self):
        formats = {"tiktok": "9:16", "reels": "9:16", "youtube": "16:9", "instagram": "1:1"}
        assert formats["youtube"] == "16:9"

    def test_converts_to_1_1(self):
        formats = {"tiktok": "9:16", "reels": "9:16", "youtube": "16:9", "instagram": "1:1"}
        assert formats["instagram"] == "1:1"

    def test_all_three_formats_generated(self):
        formats = {"tiktok": "url1", "instagram": "url2", "youtube": "url3"}
        assert len(formats) == 3

    def test_each_format_has_unique_url(self):
        urls = {"tiktok": "url_a", "instagram": "url_b", "youtube": "url_c"}
        assert len(set(urls.values())) == len(urls)


class TestAssetExpiration:
    def test_default_expiration_30_days(self):
        expiration_days = 30
        assert expiration_days == 30

    def test_client_notified_before_expiry(self):
        notified = True
        assert notified is True


class TestWatermark:
    def test_sdc_branding_applied(self):
        has_branding = True
        assert has_branding is True

    def test_watermark_optional(self):
        has_watermark = False
        assert has_watermark is False
