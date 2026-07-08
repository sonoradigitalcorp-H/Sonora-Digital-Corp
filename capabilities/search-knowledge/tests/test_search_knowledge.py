"""Tests for search-knowledge capability"""
import pytest


class TestSearchKnowledge:
    def test_manifest_exists(self):
        import yaml, os
        path = os.path.join(os.path.dirname(__file__), "..", "capability.yaml")
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data["id"] == "search-knowledge"
        assert data["domain"] == "system"
