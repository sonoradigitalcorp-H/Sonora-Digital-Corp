"""Test básico de ABE Service — verifica imports y estructura."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
for p in [BASE, BASE / "mcp", BASE / "apps" / "jarvis" / "src"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def test_imports():
    from apps.abe_service.config import config
    assert config.name == "ABE Music Inc"
    assert config.tenant_id == "abe-fenix"
    assert config.ws_port == 5180


def test_models():
    from apps.abe_service.models import (
        CEODashboard,
        ChatRequest,
        ContractType,
        RevenueSplit,
        Role,
    )
    assert Role.CEO.value == "ceo"
    assert ContractType.EXCLUSIVE.value == "exclusive"
    split = RevenueSplit(artist=0.7, label=0.2, distributor=0.1)
    assert split.artist == 0.7

    req = ChatRequest(text="hola")
    assert req.text == "hola"

    dash = CEODashboard(total_artists=3, active_artists=2, total_streams=100, total_revenue=5000, total_releases=10, total_contracts=2, generated_at="now")
    assert dash.total_artists == 3


def test_contract_engine():
    from apps.abe_service.core.contract_engine import ContractEngine
    from apps.abe_service.models import ContractType

    engine = ContractEngine()
    c = engine.create_contract("artist-1", ContractType.DISTRIBUTION_ONLY)
    assert c["artist_id"] == "artist-1"
    assert c["type"] == "distribution_only"
    assert c["status"] == "draft"
    assert "revenue_splits" in c

    got = engine.get_contract(c["id"])
    assert got is not None
    assert got["id"] == c["id"]

    signed = engine.update_status(c["id"], "active")
    assert signed["status"] == "active"


def test_distribution_engine():
    from apps.abe_service.core.distribution import DistributionEngine

    engine = DistributionEngine()
    r = engine.create_release("artist-1", "Test Song", "single", "Pop")
    assert r["title"] == "Test Song"
    assert r["type"] == "single"
    assert r["status"] == "draft"
    assert r["upc"].startswith("ABE")

    published = engine.publish_release(r["id"])
    assert published["status"] == "published"
    assert published["released_at"] is not None


def test_revenue_ledger():

    from apps.abe_service.core.contract_engine import ContractEngine
    from apps.abe_service.core.revenue_ledger import RevenueLedger
    from apps.abe_service.models import ContractType

    # Clean persistent state for reproducible test
    data_dir = BASE / "data"
    data_dir.mkdir(exist_ok=True)
    for f in [data_dir / "abe-ledger.json", data_dir / "abe-contracts.json"]:
        f.write_text("{}")

    ce = ContractEngine()
    c = ce.create_contract("artist-1", ContractType.DISTRIBUTION_ONLY)
    rl = RevenueLedger(ce)

    entry = rl.record(c["id"], "artist-1", "release-1", 1000, "streaming")
    assert entry["amount"] == 1000
    assert entry["artist_share"] == 700.0
    assert entry["label_share"] == 200.0
    assert entry["distributor_share"] == 100.0

    summary = rl.summary("artist-1")
    assert summary["total_revenue"] == 1000
    assert summary["artist_total"] == 700


def test_abe_service():
    from apps.abe_service.core.abe_service import abe_service

    artists = abe_service.get_artists()
    assert isinstance(artists, list)

    dash = abe_service.get_ceo_dashboard()
    assert dash.total_artists >= 0
    assert dash.generated_at != ""


def test_rest_api_routes():
    from apps.abe_service.main import app

    paths = []
    for r in app.routes:
        if hasattr(r, "path"):
            paths.append(r.path)
        if hasattr(r, "original_router"):
            for sr in r.original_router.routes:
                if hasattr(sr, "path"):
                    paths.append(sr.path)
    assert "/api/health" in paths
    assert "/api/ceo/dashboard" in paths
    assert "/api/artists" in paths
    assert "/api/contracts" in paths
    assert "/api/revenue" in paths
    assert "/api/chat" in paths
    assert "/api/voice/process" in paths
    assert "/api/crm/fans" in paths
    assert "/api/auth/token" in paths
    assert "/ws" in paths


def test_mcp_connect_tools():
    tools_js = Path(BASE) / "mcp" / "tools" / "abe-connect.js"
    assert tools_js.exists(), "Missing mcp/tools/abe-connect.js"
    content = tools_js.read_text()
    assert "abe_connect_fan_list" in content
    assert "abe_connect_fan_create" in content
    assert "abe_connect_notify" in content
    assert "abe_connect_stats" in content


def test_mcp_hub_tools():
    tools_js = Path(BASE) / "mcp" / "tools" / "abe-hub.js"
    assert tools_js.exists(), "Missing mcp/tools/abe-hub.js"
    content = tools_js.read_text()
    assert "abe_hub_products" in content
    assert "abe_hub_onboarding" in content
    assert "abe_hub_services" in content
    assert "abe_hub_pricing" in content
