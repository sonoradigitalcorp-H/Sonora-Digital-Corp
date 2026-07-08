"""Tests for manage-crm capability"""
import pytest


class TestManageCRM:
    def test_manifest_exists(self):
        import yaml, os
        path = os.path.join(os.path.dirname(__file__), "..", "capability.yaml")
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data["id"] == "manage-crm"
        assert data["status"] == "experimental"
