"""Tests for the Brain Graph knowledge base."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.brain_graph import SYSTEM_GRAPH


class TestBrainGraph:
    """Validate the knowledge graph structure."""

    def test_nodes_exist(self):
        assert len(SYSTEM_GRAPH["nodes"]) >= 30, f"Expected >=30 nodes, got {len(SYSTEM_GRAPH['nodes'])}"

    def test_links_exist(self):
        assert len(SYSTEM_GRAPH["links"]) >= 30, f"Expected >=30 links, got {len(SYSTEM_GRAPH['links'])}"

    def test_node_ids_are_unique(self):
        ids = [n["id"] for n in SYSTEM_GRAPH["nodes"]]
        assert len(ids) == len(set(ids)), "Duplicate node IDs found"

    def test_all_links_reference_existing_nodes(self):
        node_ids = {n["id"] for n in SYSTEM_GRAPH["nodes"]}
        for link in SYSTEM_GRAPH["links"]:
            src = link["source"] if isinstance(link["source"], str) else link["source"].get("id")
            tgt = link["target"] if isinstance(link["target"], str) else link["target"].get("id")
            assert src in node_ids, f"Link source '{src}' not found in nodes"
            assert tgt in node_ids, f"Link target '{tgt}' not found in nodes"

    def test_required_groups_present(self):
        groups = {n["group"] for n in SYSTEM_GRAPH["nodes"]}
        required = {"jarvis", "hermes", "openclaw", "mcp", "infra", "user"}
        missing = required - groups
        assert not missing, f"Missing groups: {missing}"

    def test_every_node_has_label(self):
        for n in SYSTEM_GRAPH["nodes"]:
            assert n.get("label"), f"Node {n['id']} missing label"

    def test_every_node_has_description(self):
        for n in SYSTEM_GRAPH["nodes"]:
            assert n.get("desc"), f"Node {n['id']} missing description"

    def test_every_link_has_label(self):
        for l in SYSTEM_GRAPH["links"]:
            assert l.get("label"), f"Link missing label"

    def test_serializable_to_json(self):
        json.dumps(SYSTEM_GRAPH)
