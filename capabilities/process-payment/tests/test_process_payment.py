"""Tests for process-payment capability"""
import pytest


class TestProcessPayment:
    def test_manifest_exists(self):
        import yaml, os
        path = os.path.join(os.path.dirname(__file__), "..", "capability.yaml")
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data["id"] == "process-payment"
        assert data["domain"] == "finance"
