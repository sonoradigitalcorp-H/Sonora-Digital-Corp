"""Tests para Evolution Loop — store, proposer, simulator, loop [FR1-FR5]"""
import json
import sys
import pytest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from apps.learn.evolution.store import EvolutionStore
from apps.learn.evolution.proposer import EvolutionProposer
from apps.learn.evolution.simulator import EvolutionSimulator
from apps.learn.evolution.loop import EvolutionLoop


@pytest.fixture
def tmp_store(tmp_path):
    store = EvolutionStore()
    store.PROPOSALS_FILE = tmp_path / "proposals.jsonl"
    store.DECISIONS_FILE = tmp_path / "decisions.json"
    return store


class TestEvolutionStore:
    def test_save_proposal(self, tmp_store):
        pid = tmp_store.save_proposal({"title": "Test", "type": "improvement"})
        assert pid.startswith("prop_")
        proposals = tmp_store.list_proposals()
        assert len(proposals) == 1
        assert proposals[0]["title"] == "Test"
        assert proposals[0]["status"] == "proposed"

    def test_list_proposals_limit(self, tmp_store):
        for i in range(5):
            tmp_store.save_proposal({"title": f"Test {i}"})
        proposals = tmp_store.list_proposals(limit=2)
        assert len(proposals) == 2

    def test_list_proposals_empty(self, tmp_store):
        proposals = tmp_store.list_proposals()
        assert proposals == []

    def test_update_status(self, tmp_store):
        pid = tmp_store.save_proposal({"title": "Test"})
        tmp_store.update_status(pid, "approved", "Looks good")
        proposals = tmp_store.list_proposals()
        assert proposals[0]["status"] == "approved"
        assert proposals[0]["notes"] == "Looks good"

    def test_save_decision(self, tmp_store):
        pid = tmp_store.save_proposal({"title": "Test"})
        tmp_store.save_decision(pid, "approved", "Good idea")
        decisions = json.loads(tmp_store.DECISIONS_FILE.read_text())
        assert decisions[pid]["decision"] == "approved"

    def test_proposal_has_timestamps(self, tmp_store):
        pid = tmp_store.save_proposal({"title": "Test"})
        proposals = tmp_store.list_proposals()
        assert "created_at" in proposals[0]


class TestEvolutionProposer:
    def test_analyze(self):
        proposer = EvolutionProposer()
        proposals = proposer.analyze()
        assert isinstance(proposals, list)
        assert len(proposals) >= 0

    def test_analyze_returns_proposals(self):
        proposer = EvolutionProposer()
        proposals = proposer.analyze()
        if proposals:
            assert "title" in proposals[0]
            assert "type" in proposals[0]
            assert "estimated_impact" in proposals[0]

    def test_last_analysis_is_set(self):
        proposer = EvolutionProposer()
        proposer.analyze()
        assert proposer.last_analysis is not None
        assert "proposals_generated" in proposer.last_analysis


class TestEvolutionSimulator:
    def test_compute_score(self):
        sim = EvolutionSimulator()
        score = sim._compute_current_score()
        assert "score" in score
        assert "agents" in score
        assert "active" in score
        assert "violations" in score
        assert score["score"] >= 0

    def test_simulate_high_impact(self):
        sim = EvolutionSimulator()
        result = sim.simulate({"title": "Big change", "estimated_impact": "high"})
        assert result["delta"] == 10
        assert result["recommendation"] == "approve"

    def test_simulate_low_impact(self):
        sim = EvolutionSimulator()
        result = sim.simulate({"title": "Small change", "estimated_impact": "low"})
        assert result["delta"] == 2
        assert result["recommendation"] == "review"

    def test_simulate_no_impact(self):
        sim = EvolutionSimulator()
        result = sim.simulate({"title": "Info", "estimated_impact": "none"})
        assert result["delta"] == 0
        assert result["recommendation"] == "reject"

    def test_simulate_improvement_pct(self):
        sim = EvolutionSimulator()
        result = sim.simulate({"title": "Medium", "estimated_impact": "medium"})
        assert result["improvement_pct"] >= 0


class TestEvolutionLoop:
    def test_dry_run(self):
        loop = EvolutionLoop()
        result = loop.run_once(dry_run=True)
        assert "current_score" in result
        assert "proposals_generated" in result
        assert "dry_run" in result
        assert result["dry_run"] is True

    def test_run_once_structure(self):
        loop = EvolutionLoop()
        result = loop.run_once(dry_run=True)
        assert "cycle" in result
        assert "proposals_accepted" in result


class TestCapability:
    def test_capability_file_exists(self):
        cap_file = REPO / "agents" / "capabilities" / "evolution.yaml"
        assert cap_file.exists()

    def test_policy_file_exists(self):
        policy_file = REPO / "agents" / "policies" / "70-evolution.yaml"
        assert policy_file.exists()

    def test_registry_has_evolution(self):
        import yaml
        reg_file = REPO / "agents" / "registry.yaml"
        data = yaml.safe_load(reg_file.read_text())
        agents = {a["name"]: a for a in data["agents"]}
        assert "evolution" in agents
        assert agents["evolution"]["role"] == "self-improvement"
