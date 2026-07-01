"""Tests for planner registry loader."""
import json
from pathlib import Path

import pytest

from planner.registry import (
    count_capabilities,
    count_providers,
    get_capability,
    list_capabilities,
    list_providers,
    load_registry,
    reload_registry,
)

SAMPLE_REGISTRY = {
    "version": "2.0.0",
    "capabilities": {
        "acquire-metadata": {
            "id": "acquire-metadata",
            "name": "Acquire Artist Metadata",
            "description": "Fetch artist profile from DSPs",
            "providers": [
                {"id": "deezer-api", "contract_type": "http", "weight": 1, "enabled": True},
                {"id": "apple-music-api", "contract_type": "http", "weight": 2, "enabled": True},
            ],
            "tags": ["artist", "metadata"],
        },
        "search-artist": {
            "id": "search-artist",
            "name": "Search Artist",
            "description": "Search for an artist across platforms",
            "providers": [
                {"id": "deezer-search", "contract_type": "http", "weight": 1, "enabled": True},
                {"id": "wikipedia-api", "contract_type": "http", "weight": 2, "enabled": True},
            ],
            "tags": ["artist", "search"],
        },
        "browse-artist": {
            "id": "browse-artist",
            "name": "Browse Artist Page",
            "description": "Render artist profile via browser",
            "providers": [
                {"id": "instagram-browser", "contract_type": "browser", "weight": 1, "enabled": True},
                {"id": "tiktok-browser", "contract_type": "browser", "weight": 2, "enabled": True},
                {"id": "facebook-browser", "contract_type": "browser", "weight": 3, "enabled": False},
            ],
            "tags": ["artist", "browser"],
        },
    },
}


@pytest.fixture
def registry_file(tmp_path: Path) -> Path:
    """Create a temporary registry JSON file."""
    f = tmp_path / "registry.json"
    f.write_text(json.dumps(SAMPLE_REGISTRY))
    return f


class TestLoadRegistry:
    def test_load_success(self, registry_file: Path):
        caps = load_registry(registry_file)
        assert len(caps) == 3
        assert "acquire-metadata" in caps

    def test_load_file_not_found(self):
        caps = load_registry("/nonexistent/registry.json")
        assert caps == {}

    def test_load_invalid_json(self, tmp_path: Path):
        f = tmp_path / "bad.json"
        f.write_text("not json")
        caps = load_registry(f)
        assert caps == {}

    def test_load_empty_registry(self, tmp_path: Path):
        f = tmp_path / "empty.json"
        f.write_text(json.dumps({"version": "2.0.0", "capabilities": {}}))
        caps = load_registry(f)
        assert caps == {}

    def test_load_with_skills_backward_compat(self, tmp_path: Path):
        data = dict(SAMPLE_REGISTRY)
        data["skills"] = {"research": {"command": "/research"}}
        f = tmp_path / "with_skills.json"
        f.write_text(json.dumps(data))
        caps = load_registry(f)
        assert len(caps) == 3


class TestGetCapability:
    def test_get_existing(self, registry_file: Path):
        load_registry(registry_file)
        cap = get_capability("acquire-metadata")
        assert cap is not None
        assert cap.id == "acquire-metadata"

    def test_get_missing(self, registry_file: Path):
        load_registry(registry_file)
        cap = get_capability("nonexistent")
        assert cap is None

    def test_get_empty_registry(self):
        load_registry("/dev/null/empty.json")
        assert get_capability("anything") is None


class TestListCapabilities:
    def test_list_all(self, registry_file: Path):
        load_registry(registry_file)
        caps = list_capabilities()
        assert len(caps) == 3

    def test_list_by_tag(self, registry_file: Path):
        load_registry(registry_file)
        caps = list_capabilities(tag="search")
        assert len(caps) == 1
        assert caps[0].id == "search-artist"

    def test_list_by_tag_no_match(self, registry_file: Path):
        load_registry(registry_file)
        caps = list_capabilities(tag="nonexistent")
        assert caps == []

    def test_list_empty_registry(self):
        load_registry("/dev/null/empty.json")
        assert list_capabilities() == []


class TestListProviders:
    def test_all_enabled(self, registry_file: Path):
        load_registry(registry_file)
        providers = list_providers("browse-artist")
        assert len(providers) == 2  # facebook disabled
        assert providers[0].id == "instagram-browser"
        assert providers[1].id == "tiktok-browser"

    def test_ordered_by_weight(self, registry_file: Path):
        load_registry(registry_file)
        providers = list_providers("acquire-metadata")
        assert providers[0].weight == 1
        assert providers[1].weight == 2

    def test_nonexistent_capability(self, registry_file: Path):
        load_registry(registry_file)
        providers = list_providers("nonexistent")
        assert providers == []


class TestCount:
    def test_count_capabilities(self, registry_file: Path):
        load_registry(registry_file)
        assert count_capabilities() == 3

    def test_count_providers(self, registry_file: Path):
        load_registry(registry_file)
        assert count_providers() == 7  # 2+2+3 = 7 total across all capabilities

    def test_count_empty(self):
        load_registry("/dev/null/empty.json")
        assert count_capabilities() == 0
        assert count_providers() == 0


class TestReload:
    def test_reload_updates(self, registry_file: Path, tmp_path: Path):
        load_registry(registry_file)
        assert count_capabilities() == 3

        # Modify file
        data = dict(SAMPLE_REGISTRY)
        data["capabilities"] = {
            "single": SAMPLE_REGISTRY["capabilities"]["acquire-metadata"]
        }
        registry_file.write_text(json.dumps(data))
        reload_registry()
        assert count_capabilities() == 1
