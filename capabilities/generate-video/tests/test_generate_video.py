"""Tests for generate-video capability"""
import pytest


class TestGenerateVideo:
    def test_manifest_exists(self):
        import yaml, os
        path = os.path.join(os.path.dirname(__file__), "..", "capability.yaml")
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data["id"] == "generate-video"
        assert data["status"] == "experimental"
