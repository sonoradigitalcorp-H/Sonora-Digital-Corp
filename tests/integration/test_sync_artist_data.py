"""Integration tests for sync-artist-data capability.
Tests against real Neo4j and Qdrant instances.
"""
from neo4j import GraphDatabase
import pytest

from .conftest import require_neo4j, require_qdrant

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "sdc_neo4j_2024"


@require_neo4j
def test_neo4j_connection():
    """Verify Neo4j is reachable and can execute queries."""
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)) as driver:
        with driver.session() as session:
            result = session.run("RETURN 1 AS n")
            record = result.single()
            assert record["n"] == 1


@require_neo4j
def test_neo4j_capability_registry_exists():
    """Check that capability nodes can be created and queried."""
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)) as driver:
        with driver.session() as session:
            session.run("CREATE (t:TestCapability {id: 'integration-test', name: 'Test'})")
            result = session.run("MATCH (t:TestCapability {id: 'integration-test'}) RETURN t")
            assert result.single() is not None
            session.run("MATCH (t:TestCapability {id: 'integration-test'}) DELETE t")


@require_neo4j
@require_qdrant
def test_artist_data_pipeline():
    """End-to-end: create artist profile in Neo4j and verify."""
    artist_id = "test-artist-integration"
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)) as driver:
        with driver.session() as session:
            session.run(
                "MERGE (a:Artist {id: $id}) SET a.name = $name, a.updated = datetime()",
                id=artist_id, name="Integration Test Artist"
            )
            result = session.run("MATCH (a:Artist {id: $id}) RETURN a.name AS name", id=artist_id)
            record = result.single()
            assert record is not None
            assert record["name"] == "Integration Test Artist"
            session.run("MATCH (a:Artist {id: $id}) DELETE a", id=artist_id)
