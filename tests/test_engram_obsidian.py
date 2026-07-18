"""Tests para Export Obsidian Live — vault structure, frontmatter, graph, incremental [FR-07]"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.engram_autocapture import ObsidianExporter


class TestObsidianExporter:
    def test_create_vault_structure(self, tmp_path):
        vault = tmp_path / "obsidian-vault"
        exporter = ObsidianExporter(vault_path=str(vault))
        exporter.ensure_vault_structure()
        assert (vault / "Observations").exists()
        assert (vault / "Sessions").exists()
        assert (vault / "Projects").exists()
        assert (vault / "Graph").exists()
        assert (vault / "Canvas").exists()

    def test_export_observation_as_markdown(self, tmp_path):
        vault = tmp_path / "obsidian-vault"
        exporter = ObsidianExporter(vault_path=str(vault))
        exporter.ensure_vault_structure()

        obs = {
            "title": "JWT auth middleware",
            "type": "decision",
            "project": "sonora-digital-corp",
            "topic_key": "architecture/auth-model",
            "version": "v1.2.3",
            "content": "**What**: Switched from sessions to JWT",
            "created_at": "2026-07-18T10:00:00",
        }
        exporter.export_observation(obs)
        md_file = vault / "Observations" / "JWT auth middleware.md"
        assert md_file.exists()
        content = md_file.read_text()
        assert "title: JWT auth middleware" in content
        assert "type: decision" in content
        assert "project: sonora-digital-corp" in content
        assert "topic_key: architecture/auth-model" in content
        assert "version: v1.2.3" in content
        assert "tags:" in content
        assert "---" in content

    def test_frontmatter_is_valid_yaml(self, tmp_path):
        import yaml
        vault = tmp_path / "obsidian-vault"
        exporter = ObsidianExporter(vault_path=str(vault))
        exporter.ensure_vault_structure()
        exporter.export_observation({
            "title": "test",
            "type": "discovery",
            "project": "p",
            "topic_key": "t/k",
            "version": "v1.0.0",
            "content": "test content",
            "created_at": "2026-01-01",
        })
        md = (vault / "Observations" / "test.md").read_text()
        frontmatter = md.split("---")[1]
        parsed = yaml.safe_load(frontmatter)
        assert parsed["title"] == "test"
        assert parsed["type"] == "discovery"
        assert parsed["project"] == "p"

    def test_export_graph_relationships(self, tmp_path):
        vault = tmp_path / "obsidian-vault"
        exporter = ObsidianExporter(vault_path=str(vault))
        exporter.ensure_vault_structure()
        relations = [
            ("A", "supersedes", "B"),
            ("A", "related", "C"),
        ]
        exporter.export_graph(relations)
        graph_file = vault / "Graph" / "relationships.md"
        assert graph_file.exists()
        content = graph_file.read_text()
        assert "A -> supersedes -> B" in content
        assert "A -> related -> C" in content

    def test_incremental_only_new(self, tmp_path):
        vault = tmp_path / "obsidian-vault"
        exporter = ObsidianExporter(vault_path=str(vault))
        exporter.ensure_vault_structure()
        exporter.mark_exported("obs_001")
        assert exporter.is_already_exported("obs_001") is True
        assert exporter.is_already_exported("obs_002") is False
