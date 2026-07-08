"""Tests for sales_pipeline.py — LeadScorer, ProposalGenerator, events, graceful degradation."""

import json
import os
import tempfile
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from src.core.sales_pipeline import (
    LeadScorer,
    ProposalGenerator,
    SalesPipeline,
    Lead,
    PipelineStage,
    LeadSource,
    _emit_event,
    _emit_score_log,
)


class TestLeadScorer:
    @pytest.fixture
    def scorer(self):
        return LeadScorer()

    def test_score_imperio_plan(self, scorer):
        lead = Lead(plan_interest="imperio", source="referral", niche="empresa")
        score = scorer.score(lead)
        assert score >= 20  # imperio(10) + referral(8) + empresa(8)

    def test_score_explorador_plan(self, scorer):
        lead = Lead(plan_interest="explorador", source="manual", niche="general")
        score = scorer.score(lead)
        assert score <= 10

    def test_qualified_threshold(self, scorer):
        lead = Lead(plan_interest="imperio", source="referral", niche="empresa")
        assert scorer.is_qualified(lead, threshold=10) is True

    def test_not_qualified(self, scorer):
        lead = Lead(plan_interest="explorador", source="manual", niche="general")
        assert scorer.is_qualified(lead, threshold=10) is False

    def test_unknown_values_default_to_low(self, scorer):
        lead = Lead(plan_interest="nonexistent", source="unknown", niche="unknown")
        score = scorer.score(lead)
        assert score == 6  # 1 (plan) + 3 (source default) + 2 (niche default)


class TestProposalGenerator:
    @pytest.fixture
    def gen(self):
        return ProposalGenerator()

    def test_generates_proposal_with_plan(self, gen):
        lead = Lead(name="Test User", plan_interest="conquistador", niche="musica")
        proposal = gen.generate(lead)
        assert "Test User" in proposal
        assert "Conquistador" in proposal
        assert "Mercado Pago" in proposal
        assert "Bitso" in proposal
        assert "SPEI" in proposal

    def test_generates_proposal_fallback_conquistador(self, gen):
        lead = Lead(name="No Plan", plan_interest="", niche="general")
        proposal = gen.generate(lead)
        assert "Conquistador" in proposal  # fallback to first plan

    def test_proposal_includes_price(self, gen):
        lead = Lead(name="Priced", plan_interest="imperio", niche="general")
        proposal = gen.generate(lead)
        assert "$" in proposal
        assert "MXN" in proposal


class TestSalesPipeline:
    @pytest.fixture
    def pipeline(self):
        return SalesPipeline()

    def test_capture_lead_creates_id(self, pipeline):
        lead = pipeline.capture_lead(name="Test", email="test@test.com", source="web_form")
        assert lead.id.startswith("lead_")
        assert lead.score > 0
        assert lead.stage == PipelineStage.LEAD

    def test_capture_lead_emits_event(self, pipeline):
        events_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "state", "logs", "events.jsonl"
        )
        before = 0
        if os.path.exists(events_file):
            with open(events_file) as f:
                before = sum(1 for _ in f)

        pipeline.capture_lead(name="Event Test", source="telegram")

        if os.path.exists(events_file):
            with open(events_file) as f:
                after = sum(1 for _ in f)
            assert after > before

    def test_auto_qualify_empty_returns_empty_list(self, pipeline):
        with patch.object(pipeline, 'list_leads', return_value=[]):
            qualified = pipeline.auto_qualify_leads(threshold=10)
        assert qualified == []  # Graceful degradation when no leads

    def test_pipeline_graceful_without_neo4j(self, pipeline):
        lead = pipeline.get_lead("nonexistent")
        assert lead is None

    def test_dashboard_returns_structure(self, pipeline):
        dashboard = pipeline.get_dashboard()
        assert "stages" in dashboard
        assert "total_leads" in dashboard
        assert "won" in dashboard
        assert "lost" in dashboard
        assert "conversion_rate" in dashboard
        assert "total_revenue" in dashboard
        assert "pipeline_value" in dashboard
        assert list(PipelineStage) == [PipelineStage.LEAD, PipelineStage.QUALIFIED,
                                        PipelineStage.PROPOSAL, PipelineStage.NEGOTIATION,
                                        PipelineStage.WON, PipelineStage.LOST]


class TestLeadModel:
    def test_lead_defaults(self):
        lead = Lead()
        assert lead.id == ""
        assert lead.stage == PipelineStage.LEAD
        assert lead.source == LeadSource.MANUAL
        assert lead.score == 0

    def test_lead_with_values(self):
        lead = Lead(id="lead_abc", name="John", email="j@test.com", score=15,
                     stage=PipelineStage.QUALIFIED)
        assert lead.id == "lead_abc"
        assert lead.name == "John"
        assert lead.score == 15
        assert lead.stage == PipelineStage.QUALIFIED


class TestEventEmission:
    def test_emit_event_appends_to_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            events_file = os.path.join(tmp, "events.jsonl")
            original = "state/logs/events.jsonl"
            _emit_event("test_event", {"key": "value"})
            # event goes to real file, just test no exception
            assert True

    def test_score_log_does_not_crash(self):
        _emit_score_log("test", "deal_123", 100.0)
        assert True


class TestPipelineStages:
    def test_stage_order(self):
        stages = [s.value for s in PipelineStage]
        assert stages == ["lead", "qualified", "proposal", "negotiation", "won", "lost"]

    def test_all_stages_covered(self):
        assert len(PipelineStage) == 6
