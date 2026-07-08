"""Tests for analyze-artist capability"""
import pytest


class TestAnalyzeArtist:
    def test_manifest_exists(self):
        import yaml, os
        path = os.path.join(os.path.dirname(__file__), "..", "capability.yaml")
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data["id"] == "analyze-artist"
        assert data["version"] == "1.0.0"
