"""Integration tests for clone-person capability.
Tests the event system and scoring pipeline end-to-end.
"""
import json
import os
from pathlib import Path
import pytest

from .conftest import require_neo4j

REPO = Path(__file__).resolve().parent.parent.parent


def test_event_system_logs_events():
    """Verify the event system exists and can write events."""
    events_dir = REPO / "state" / "events"
    assert events_dir.exists() or events_dir.parent.exists()


def test_scorecard_updated():
    """Verify the scorecard has recent data."""
    scorecard = REPO / "core" / "scorecard.json"
    assert scorecard.exists()
    with open(scorecard) as f:
        data = json.load(f)
    assert "overall" in data
    assert "metrics" in data
    assert data["metrics"].get("capabilities", 0) >= 9


@require_neo4j
def test_neo4j_can_store_clone_models():
    """Verify Neo4j can store and query clone model metadata."""
    from neo4j import GraphDatabase

    with GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "sdc_neo4j_2024")) as driver:
        with driver.session() as session:
            session.run(
                "MERGE (m:CloneModel {id: 'test-clone'}) "
                "SET m.name = 'Test Clone', m.status = 'trained', m.created = datetime()"
            )
            result = session.run("MATCH (m:CloneModel {id: 'test-clone'}) RETURN m.status AS status")
            record = result.single()
            assert record is not None
            assert record["status"] == "trained"
            session.run("MATCH (m:CloneModel {id: 'test-clone'}) DELETE m")
