"""Tests para URL Validator — FR-06: SSRF protection"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from common.security.url_validator import filter_valid_urls, validate_url, validate_urls


class TestURLValidator:
    def test_allows_https_public_url(self):
        result = validate_url("https://example.com/photo.jpg")
        assert result.valid

    def test_allows_https_subdomain(self):
        result = validate_url("https://storage.supabase.co/object/public/test.jpg")
        assert result.valid

    def test_blocks_http(self):
        result = validate_url("http://example.com/photo.jpg")
        assert not result.valid
        assert "HTTPS" in result.reason

    def test_blocks_localhost(self):
        result = validate_url("http://localhost:6333/secret")
        assert not result.valid
        assert result.reason  # Should have a reason, any reason

    def test_blocks_127_0_0_1(self):
        result = validate_url("https://127.0.0.1:7687/db/data")
        assert not result.valid

    def test_blocks_private_ip_10_x(self):
        result = validate_url("https://10.0.0.1/admin")
        assert not result.valid

    def test_blocks_private_ip_192_168(self):
        result = validate_url("https://192.168.1.1/config")
        assert not result.valid

    def test_blocks_empty_url(self):
        result = validate_url("")
        assert not result.valid

    def test_blocks_excessively_long_url(self):
        result = validate_url("https://example.com/" + "a" * 3000)
        assert not result.valid

    def test_blocks_metadata_service(self):
        result = validate_url("https://169.254.169.254/latest/meta-data/")
        assert not result.valid

    def test_validates_url_list(self):
        urls = [
            "https://safe.com/img.jpg",
            "http://localhost:6333/evil",
            "https://192.168.1.1/admin",
            "https://another-safe.com/img.png",
        ]
        results = validate_urls(urls)
        valid_count = sum(1 for r in results if r.valid)
        assert valid_count == 2

    def test_filter_valid_urls(self):
        urls = ["https://safe.com/img.jpg", "http://localhost:6333/evil"]
        valid = filter_valid_urls(urls)
        assert len(valid) == 1
        assert valid[0] == "https://safe.com/img.jpg"
