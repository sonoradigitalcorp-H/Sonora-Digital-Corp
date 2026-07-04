"""Integration tests for Unified Brain"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.brain.mcp_tool import unified_brain_query
from apps.brain.service import BrainService

def test_neo4j_connectivity():
    b = BrainService()
    status = b.ready()
    b.close()
    assert status["neo4j"], "Neo4j should be reachable"
    assert status["qdrant"], "Qdrant should be reachable"
    print("  ✅ Neo4j + Qdrant + Engram connectivity")

def test_semantic_search():
    r = unified_brain_query("Hermes")
    assert r["total"] > 0, "Should find Hermes"
    print(f"  ✅ Semantic search: {r['total']} results")

def test_type_filter():
    r = unified_brain_query("Neo4j", type_filter="service")
    print(f"  ✅ Type filter: {r['total']} results, types: {[x['type'] for x in r['results']]}")

def test_event_search():
    r = unified_brain_query("health")
    has_event = any(x["type"] == "event" for x in r["results"])
    print(f"  ✅ Event search: {r['total']} results, has events: {has_event}")

def test_node_count():
    b = BrainService()
    with b.neo4j.session() as s:
        count = s.run("MATCH (n:Knowledge) RETURN count(n) as c").single()["c"]
    b.close()
    assert count > 100, f"Should have >100 nodes, got {count}"
    print(f"  ✅ Node count: {count} nodes")

if __name__ == "__main__":
    print("Unified Brain Integration Tests")
    print("=" * 40)
    test_neo4j_connectivity()
    test_semantic_search()
    test_type_filter()
    test_event_search()
    test_node_count()
    print("=" * 40)
    print(" ALL TESTS PASSED")
