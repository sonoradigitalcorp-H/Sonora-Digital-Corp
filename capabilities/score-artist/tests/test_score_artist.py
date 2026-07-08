"""Tests for score-artist capability"""
import pytest


class TestScoreArtist:
    def test_manifest_exists(self):
        import yaml, os
        path = os.path.join(os.path.dirname(__file__), "..", "capability.yaml")
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data["id"] == "score-artist"
        assert data["version"] == "1.0.0"
