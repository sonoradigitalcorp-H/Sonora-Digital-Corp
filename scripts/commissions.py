"""Commissions Tracker — Enterprise deal tracking and partner commissions.

Tracks wholesale deals, partner markups, and projects revenue.
CLI for partners like AztroTech (César) to see their earnings.

Usage:
  python3 scripts/commissions.py --add-partner aztrotech "César Holguín"
  python3 scripts/commissions.py --add-deal aztrotech "Corp ABC" business 15000 7500 28000 14000
  python3 scripts/commissions.py --partners
  python3 scripts/commissions.py --summary aztrotech
  python3 scripts/commissions.py --projection aztrotech
"""

import argparse
import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _get_db() -> sqlite3.Connection:
    db_path = Path(os.environ.get("COMMISSIONS_DB_PATH", str(REPO / "data" / "commissions.db")))
    os.makedirs(db_path.parent, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS partners (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            contact TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id TEXT NOT NULL,
            client_name TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            wholesale_setup REAL NOT NULL,
            wholesale_monthly REAL NOT NULL,
            resell_setup REAL NOT NULL,
            resell_monthly REAL NOT NULL,
            powered_by_level TEXT DEFAULT 'hidden',
            status TEXT DEFAULT 'active',
            signed_at TEXT DEFAULT (datetime('now')),
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (partner_id) REFERENCES partners(id)
        );
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            paid_at TEXT DEFAULT (datetime('now')),
            notes TEXT DEFAULT '',
            FOREIGN KEY (deal_id) REFERENCES deals(id)
        );
    """)
    conn.commit()
    conn.close()


def load_packages() -> dict:
    import yaml
    path = REPO / "config" / "packages.yaml"
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f) or {}
    return {}


def get_plan(plan_id: str) -> dict:
    pkgs = load_packages()
    plans = pkgs.get("enterprise_wholesale", {})
    plan = plans.get(plan_id)
    if not plan:
        return {"error": f"Plan '{plan_id}' not found", "available": list(plans.keys())}
    return plan


def calc_powered_discount(level: str, amount: float) -> tuple:
    pkgs = load_packages()
    levels = pkgs.get("powered_by_sdc", {})
    cfg = levels.get(level, levels.get("hidden", {"discount_pct": 0}))
    discount_pct = cfg["discount_pct"]
    discount = round(amount * discount_pct / 100, 2)
    return discount_pct, discount


def add_partner(partner_id: str, name: str, contact: str = "") -> str:
    if not partner_id or not name:
        return json.dumps({"error": "partner_id and name are required"})
    _init_db()
    conn = _get_db()
    conn.execute("INSERT OR REPLACE INTO partners (id, name, contact) VALUES (?, ?, ?)",
                 (partner_id, name, contact))
    conn.commit()
    conn.close()
    return json.dumps({"partner_id": partner_id, "name": name, "status": "active"})


def add_deal(partner_id: str, client_name: str, plan_id: str,
             wholesale_setup: float, wholesale_monthly: float,
             resell_setup: float, resell_monthly: float,
             powered_by: str = "hidden") -> str:
    if not partner_id or not client_name:
        return json.dumps({"error": "partner_id and client_name are required"})

    plan = get_plan(plan_id)
    if "error" in plan:
        return json.dumps(plan)

    partner_markup_setup = round(resell_setup - wholesale_setup, 2)
    partner_markup_monthly = round(resell_monthly - wholesale_monthly, 2)

    _init_db()
    conn = _get_db()

    # Check partner exists
    cur = conn.execute("SELECT id FROM partners WHERE id = ?", (partner_id,))
    if not cur.fetchone():
        conn.close()
        return json.dumps({"error": f"Partner '{partner_id}' not found. Add with --add-partner first."})

    # Apply powered-by discount
    discount_pct, discount_amount = calc_powered_discount(powered_by, wholesale_monthly)
    discounted_monthly = round(wholesale_monthly - discount_amount, 2)

    conn.execute(
        """INSERT INTO deals
           (partner_id, client_name, plan_id, wholesale_setup, wholesale_monthly,
            resell_setup, resell_monthly, powered_by_level, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')""",
        (partner_id, client_name, plan_id, wholesale_setup, discounted_monthly,
         resell_setup, resell_monthly, powered_by),
    )
    deal_id = conn.execute("SELECT last_insert_rowid() as rid").fetchone()["rid"]
    conn.commit()
    conn.close()

    # Projections
    y1_wholesale = wholesale_setup + discounted_monthly * 12
    y1_partner = partner_markup_setup + partner_markup_monthly * 12

    return json.dumps({
        "deal_id": deal_id,
        "partner_id": partner_id,
        "client_name": client_name,
        "plan": plan_id,
        "wholesale": {"setup": wholesale_setup, "monthly": discounted_monthly},
        "partner_markup": {"setup": partner_markup_setup, "monthly": partner_markup_monthly},
        "powered_by": {"level": powered_by, "discount_pct": discount_pct, "discount_amount": discount_amount},
        "year_1_projection": {
            "sdc_wholesale": round(y1_wholesale, 2),
            "partner_markup": round(y1_partner, 2),
            "client_total": round(resell_setup + resell_monthly * 12, 2),
        },
        "status": "active",
    })


def get_partner_summary(partner_id: str) -> str:
    _init_db()
    conn = _get_db()
    deals = conn.execute(
        "SELECT * FROM deals WHERE partner_id = ? AND status = 'active' ORDER BY created_at DESC",
        (partner_id,),
    ).fetchall()

    total_wholesale_monthly = sum(d["wholesale_monthly"] for d in deals)
    total_markup_monthly = sum(d["resell_monthly"] - d["wholesale_monthly"] for d in deals)
    total_wholesale_setup = sum(d["wholesale_setup"] for d in deals)
    total_markup_setup = sum(d["resell_setup"] - d["wholesale_setup"] for d in deals)

    conn.close()
    return json.dumps({
        "partner_id": partner_id,
        "active_deals": len(deals),
        "monthly_recurring": {
            "sdc_wholesale": round(total_wholesale_monthly, 2),
            "partner_markup": round(total_markup_monthly, 2),
        },
        "setup_total": {
            "sdc_wholesale": round(total_wholesale_setup, 2),
            "partner_markup": round(total_markup_setup, 2),
        },
        "deals": [dict(d) for d in deals],
    })


def get_all_partners() -> str:
    _init_db()
    conn = _get_db()
    partners = conn.execute("SELECT * FROM partners WHERE active = 1 ORDER BY created_at DESC").fetchall()
    result = []
    for p in partners:
        deals = conn.execute(
            "SELECT COUNT(*) as cnt FROM deals WHERE partner_id = ? AND status = 'active'",
            (p["id"],),
        ).fetchone()["cnt"]
        result.append({**dict(p), "active_deals": deals})
    conn.close()
    return json.dumps({"partners": result})


def get_projection(partner_id: str, months: int = 12) -> str:
    _init_db()
    conn = _get_db()
    deals = conn.execute(
        "SELECT * FROM deals WHERE partner_id = ? AND status = 'active'",
        (partner_id,),
    ).fetchall()
    conn.close()

    monthly_wholesale = sum(d["wholesale_monthly"] for d in deals)
    monthly_markup = sum(d["resell_monthly"] - d["wholesale_monthly"] for d in deals)
    total_setup_wholesale = sum(d["wholesale_setup"] for d in deals)
    total_setup_markup = sum(d["resell_setup"] - d["wholesale_setup"] for d in deals)

    projection = []
    for m in range(1, months + 1):
        month_name = (datetime.now() + timedelta(days=30 * m)).strftime("%Y-%m")
        if m == 1:
            sdc = total_setup_wholesale + monthly_wholesale
            mark = total_setup_markup + monthly_markup
        else:
            sdc = monthly_wholesale
            mark = monthly_markup
        projection.append({"month": month_name, "sdc_wholesale": round(sdc, 2), "partner_markup": round(mark, 2)})

    total_sdc = sum(p["sdc_wholesale"] for p in projection)
    total_markup = sum(p["partner_markup"] for p in projection)

    return json.dumps({
        "partner_id": partner_id,
        "current_deals": len(deals),
        "projection_months": months,
        "monthly": projection,
        "totals": {"sdc_wholesale": round(total_sdc, 2), "partner_markup": round(total_markup, 2)},
    })


def main():
    parser = argparse.ArgumentParser(description="SDC Enterprise Commissions Tracker")
    parser.add_argument("--add-partner", nargs=2, metavar=("ID", "NAME"), help="Add a new partner (ej: --add-partner aztrotech 'César Holguín')")
    parser.add_argument("--add-deal", nargs=6,
        metavar=("PARTNER", "CLIENT", "PLAN", "W_SETUP", "W_MONTHLY", "R_MONTHLY"),
        help="Add deal: partner/client/plan/w_setup/w_monthly/r_monthly")
    parser.add_argument("--resell-setup", type=float, default=0, help="Resell setup fee (for --add-deal)")
    parser.add_argument("--powered-by", default="hidden", choices=["hidden", "footer_only", "public_mentions", "full_branding"], help="Powered by SDC level")
    parser.add_argument("--summary", metavar="PARTNER", help="Get partner summary")
    parser.add_argument("--partners", action="store_true", help="List all partners")
    parser.add_argument("--projection", nargs="?", const="aztrotech", metavar="PARTNER", help="Revenue projection for partner")

    args = parser.parse_args()
    _init_db()

    if args.add_partner:
        pid, name = args.add_partner
        print(add_partner(pid, name))
    elif args.add_deal:
        pid, client, plan = args.add_deal[:3]
        try:
            w_setup = float(args.add_deal[3])
            w_monthly = float(args.add_deal[4])
            r_monthly = float(args.add_deal[5])
        except (ValueError, IndexError):
            print(json.dumps({"error": "Invalid numbers for prices. Use: partner client plan w_setup w_monthly r_monthly [--resell-setup RSETUP]"}))
            return
        r_setup = args.resell_setup or w_setup * 1.5  # Default 50% markup on setup
        print(add_deal(pid, client, plan, w_setup, w_monthly, r_setup, r_monthly, args.powered_by))
    elif args.summary:
        print(get_partner_summary(args.summary))
    elif args.partners:
        print(get_all_partners())
    elif args.projection:
        print(get_projection(args.projection))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
