"""Tests for publish-track capability"""
import pytest


class TestPublishTrack:
    def test_manifest_exists(self):
        import yaml, os
        path = os.path.join(os.path.dirname(__file__), "..", "capability.yaml")
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data["id"] == "publish-track"
        assert data["status"] == "experimental"
