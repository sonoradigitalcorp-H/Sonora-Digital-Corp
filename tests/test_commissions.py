"""Tests para Commissions Tracker — Enterprise deals, partner markups, powered-by discounts"""

import json
import os
import sqlite3
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

import sys
sys.path.insert(0, str(REPO))

_TEST_DB = Path(tempfile.mkdtemp()) / "test_commissions.db"


def _setup():
    os.environ["COMMISSIONS_DB_PATH"] = str(_TEST_DB)
    conn = sqlite3.connect(str(_TEST_DB))
    conn.execute("DROP TABLE IF EXISTS payments")
    conn.execute("DROP TABLE IF EXISTS deals")
    conn.execute("DROP TABLE IF EXISTS partners")
    conn.commit()
    conn.close()
    from scripts.commissions import _init_db
    _init_db()


class TestPartners:
    def test_adds_partner(self):
        _setup()
        from scripts.commissions import add_partner
        result = json.loads(add_partner("aztrotech", "César Holguín"))
        assert result["partner_id"] == "aztrotech"
        assert result["status"] == "active"

    def test_rejects_empty_partner(self):
        _setup()
        from scripts.commissions import add_partner
        result = json.loads(add_partner("", ""))
        assert "error" in result

    def test_adds_multiple_partners(self):
        _setup()
        from scripts.commissions import add_partner
        add_partner("aztrotech", "César")
        add_partner("abe_music", "Abraham")
        result = json.loads(add_partner("partner3", "Otro"))
        assert result["partner_id"] == "partner3"


class TestDeals:
    def test_adds_deal(self):
        _setup()
        from scripts.commissions import add_partner, add_deal
        add_partner("aztrotech", "César")
        result = json.loads(add_deal("aztrotech", "Corp ABC", "business", 15000, 7500, 28000, 14000))
        assert result["deal_id"] >= 1
        assert result["plan"] == "business"
        assert result["wholesale"]["setup"] == 15000
        assert result["partner_markup"]["setup"] == 13000  # 28000-15000
        assert result["partner_markup"]["monthly"] == 6500  # 14000-7500

    def test_deal_year_projection(self):
        _setup()
        from scripts.commissions import add_partner, add_deal
        add_partner("aztrotech", "César")
        result = json.loads(add_deal("aztrotech", "Corp ABC", "business", 15000, 7500, 28000, 14000))
        proj = result["year_1_projection"]
        assert proj["sdc_wholesale"] == 15000 + 7500 * 12  # $105,000
        assert proj["partner_markup"] == 13000 + 6500 * 12  # $91,000

    def test_rejects_deal_without_partner(self):
        _setup()
        from scripts.commissions import add_deal
        result = json.loads(add_deal("nonexistent", "Corp", "business", 1000, 500, 2000, 1000))
        assert "error" in result

    def test_rejects_invalid_plan(self):
        _setup()
        from scripts.commissions import add_partner, add_deal
        add_partner("aztrotech", "César")
        result = json.loads(add_deal("aztrotech", "Corp", "platinum", 1000, 500, 2000, 1000))
        assert "error" in result


class TestPoweredByDiscount:
    def test_footer_discount_applied(self):
        _setup()
        from scripts.commissions import add_partner, add_deal
        add_partner("aztrotech", "César")
        result = json.loads(add_deal("aztrotech", "Corp", "business", 15000, 7500, 28000, 14000, "footer_only"))
        assert result["powered_by"]["discount_pct"] == 5
        monthly = result["wholesale"]["monthly"]
        assert monthly == 7125  # 7500 - 5%

    def test_full_branding_discount(self):
        _setup()
        from scripts.commissions import add_partner, add_deal
        add_partner("aztrotech", "César")
        result = json.loads(add_deal("aztrotech", "Corp", "business", 15000, 7500, 28000, 14000, "full_branding"))
        assert result["powered_by"]["discount_pct"] == 10
        assert result["wholesale"]["monthly"] == 6750  # 7500 - 10%

    def test_hidden_no_discount(self):
        _setup()
        from scripts.commissions import add_partner, add_deal
        add_partner("aztrotech", "César")
        result = json.loads(add_deal("aztrotech", "Corp", "business", 15000, 7500, 28000, 14000, "hidden"))
        assert result["powered_by"]["discount_pct"] == 0
        assert result["wholesale"]["monthly"] == 7500


class TestSummary:
    def test_partner_summary(self):
        _setup()
        from scripts.commissions import add_partner, add_deal, get_partner_summary
        add_partner("aztrotech", "César")
        add_deal("aztrotech", "Client A", "business", 15000, 7500, 28000, 14000)
        add_deal("aztrotech", "Client B", "starter", 5000, 2500, 10000, 5000)
        result = json.loads(get_partner_summary("aztrotech"))
        assert result["active_deals"] == 2
        assert result["monthly_recurring"]["sdc_wholesale"] == 10000  # 7500+2500
        assert result["monthly_recurring"]["partner_markup"] == 9000  # (28000-15000)+(10000-5000)=13000+5000=18000... wait

    def test_all_partners(self):
        _setup()
        from scripts.commissions import add_partner, get_all_partners
        add_partner("aztrotech", "César")
        add_partner("abe_music", "Abraham")
        result = json.loads(get_all_partners())
        assert len(result["partners"]) == 2


class TestProjection:
    def test_projection_12_months(self):
        _setup()
        from scripts.commissions import add_partner, add_deal, get_projection
        add_partner("aztrotech", "César")
        add_deal("aztrotech", "Corp", "business", 15000, 7500, 28000, 14000)
        result = json.loads(get_projection("aztrotech", 12))
        assert len(result["monthly"]) == 12
        assert result["totals"]["sdc_wholesale"] > 0
        assert result["totals"]["partner_markup"] > 0
