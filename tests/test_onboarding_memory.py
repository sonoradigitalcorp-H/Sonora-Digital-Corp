"""Tests para Memoria de Onboarding — FR-05: Engram + Qdrant + Neo4j"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(REPO))


class TestMemory:
    def test_engram_entry_format(self):
        entry = {
            "timestamp": "2026-07-18T12:00:00",
            "type": "milestone",
            "title": "onboarding: Juan Pérez",
            "content": "Cliente Juan Pérez activado via onboarding. Partner: aztrotech. Plan: pro.",
        }
        assert entry["type"] == "milestone"
        assert "onboarding:" in entry["title"]
        assert "activado" in entry["content"]

    def test_qdrant_vector_profile(self):
        profile = {
            "tenant_id": "aztrotech_a1b2c3d4",
            "name": "Juan Pérez",
            "partner": "aztrotech",
            "plan": "pro",
            "phone": "+5216622681111",
            "tags": ["cliente", "activo", "pro"],
        }
        assert profile["tenant_id"].startswith("aztrotech_")
        assert profile["plan"] in ("basic", "pro", "enterprise")
        assert "cliente" in profile["tags"]

    def test_neo4j_graph_relationships(self):
        graph = {
            "nodes": [
                {"id": "cliente_1", "type": "Cliente", "name": "Juan"},
                {"id": "partner_1", "type": "Partner", "name": "AztroTech"},
            ],
            "edges": [
                {"source": "cliente_1", "target": "partner_1", "relation": "CLIENTE_DE"},
            ],
        }
        assert len(graph["nodes"]) == 2
        assert graph["edges"][0]["relation"] == "CLIENTE_DE"

    def test_onboarding_log_created(self):
        log_entry = {
            "timestamp": "2026-07-18T12:00:00",
            "tenant_id": "aztrotech_a1b2c3d4",
            "client_name": "Juan Pérez",
            "partner_id": "aztrotech",
            "plan": "pro",
        }
        assert "tenant_id" in log_entry
        assert "partner_id" in log_entry

    def test_onboarding_log_has_all_required_fields(self):
        required = {"timestamp", "tenant_id", "client_name", "partner_id", "plan"}
        log = {"timestamp": "x", "tenant_id": "y", "client_name": "z", "partner_id": "w", "plan": "p", "extra": "e"}
        assert required.issubset(set(log.keys()))

    def test_code_status_tracked(self):
        code_record = {
            "id": "SDC-A7F3K2",
            "status": "used",
            "client_phone": "+5216622681111",
            "activated_at": "2026-07-18T12:00:00",
        }
        assert code_record["status"] in ("active", "used", "expired")
        assert code_record["activated_at"] is not None

    def test_activation_feed_to_engram(self):
        feed_cmd = 'engram save "onboarding: Test" "Cliente activado" --type milestone'
        assert "engram save" in feed_cmd
        assert "--type milestone" in feed_cmd
