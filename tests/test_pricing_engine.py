"""Tests para Pricing Engine — FR-04/FR-05: Cálculo de precio dinámico"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO))

from scripts.pricing_engine import calculate_from_cost, calculate_price


class TestCalculatePrice:
    def test_basic_tech_small(self):
        result = calculate_price("tecnologia", "small", 1.0)
        assert result["industry"] == "tecnologia"
        assert result["setup_fee"] == 499
        assert result["monthly_base"] == 149
        assert result["revenue_share_pct"] == 5

    def test_music_enterprise(self):
        result = calculate_price("musica", "enterprise", 1.0)
        assert result["setup_fee"] == 2499
        assert result["monthly_base"] == 999
        assert result["revenue_share_pct"] == 10

    def test_marketing_premium(self):
        result = calculate_price("marketing", "medium", 1.0)
        assert result["setup_fee"] == 1499
        assert result["monthly_base"] == 599
        assert result["revenue_share_pct"] == 7

    def test_legal_has_highest_setup(self):
        result = calculate_price("legal", "enterprise")
        assert result["setup_fee"] == 4999
        assert result["monthly_base"] == 2499

    def test_partner_discount_applied(self):
        result = calculate_price("tecnologia", "medium", 1.0, partner="aztrotech")
        assert result["partner_monthly"] is not None
        assert result["partner_monthly"] < result["monthly_base"]
        assert result["partner_discount_pct"] == 30

    def test_abe_music_discount(self):
        result = calculate_price("musica", "small", 1.0, partner="abe_music")
        assert result["partner_discount_pct"] == 25
        assert result["partner_monthly"] < result["monthly_base"]

    def test_volume_multiplier(self):
        base = calculate_price("tecnologia", "small", 1.0)
        scaled = calculate_price("tecnologia", "small", 2.0)
        assert scaled["monthly_base"] == base["monthly_base"] * 2

    def test_revenue_share_floor(self):
        result = calculate_price("tecnologia", "small", 1.0, "", 5000)
        assert result["revenue_share_estimated_monthly"] >= 100

    def test_unknown_industry_returns_error(self):
        result = calculate_price("nonexistent", "small")
        assert "error" in result

    def test_unknown_size_defaults_to_small(self):
        result = calculate_price("tecnologia", "giant")
        assert result["size"] == "small"


class TestCalculateFromCost:
    def test_calculates_from_monthly_cost(self):
        result = calculate_from_cost(10.0, "tecnologia")
        assert result["estimated_monthly_cost"] == 10.0
        assert result["suggested_monthly"] > 0
        assert result["margin_pct"] >= 70

    def test_higher_margin_requires_more_revenue(self):
        low_margin = calculate_from_cost(10.0, "tecnologia", target_margin=0.70)
        high_margin = calculate_from_cost(10.0, "tecnologia", target_margin=0.90)
        assert high_margin["required_revenue"] > low_margin["required_revenue"]

    def test_partner_discount_included(self):
        result = calculate_from_cost(10.0, "tecnologia", partner="aztrotech")
        assert result["partner_monthly"] is not None

    def test_zero_cost_does_not_crash(self):
        result = calculate_from_cost(0, "tecnologia")
        assert "estimated_monthly_cost" in result
