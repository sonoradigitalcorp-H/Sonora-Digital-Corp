"""SDC Enterprise Packages CLI — Planes wholesale, markup para partners, powered-by discounts.

Usage:
  python3 scripts/packages.py --enterprise             # Planes enterprise wholesale
  python3 scripts/packages.py --show business          # Detalle de un plan
  python3 scripts/packages.py --calculate-deal business 28000 14000  # Tú ganas X, partner gana Y
  python3 scripts/packages.py --powered-levels          # Niveles de powered-by SDC
"""

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def load_packages() -> dict:
    import yaml
    path = REPO / "config" / "packages.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def show_enterprise():
    pkgs = load_packages()
    plans = pkgs.get("enterprise_wholesale", {})
    print(f"\n{'═'*80}")
    print("  🏢  ENTERPRISE WHOLESALE — Lo que pagas a SDC por cliente")
    print(f"{'═'*80}\n")
    print(f"  {'Plan':12s} {'Setup':>10s} {'Monthly':>10s} {'Asientos':>10s} {'Interacciones':>15s} {'Soporte'}")
    print(f"  {'─'*80}")
    for pid, plan in plans.items():
        seats = "∞" if plan["seats"] == -1 else str(plan["seats"])
        interactions = "∞" if plan["interactions_per_month"] == -1 else f"{plan['interactions_per_month']:,}/mes"
        print(f"  {pid:12s} ${plan['setup_fee']:>7,}  ${plan['monthly']:>7,}  {seats:>8s}  {interactions:>15s}  {plan['support'][:20]}")
    print()

    print(f"  {'─'*80}")
    print("  📊  SUGERENCIA DE REVENTA (lo que el partner cobra al cliente)")
    print(f"  {'─'*80}")
    print(f"  {'Plan':12s} {'Setup sugerido':>20s} {'Monthly sugerido':>20s} {'Markup partner':>20s}")
    print(f"  {'─'*80}")
    for pid, plan in plans.items():
        resell_setup = plan["suggested_resell_setup"]
        resell_monthly = plan["suggested_resell_monthly"]
        markup_setup = resell_setup[0] - plan["setup_fee"]
        markup_monthly = resell_monthly[0] - plan["monthly"]
        print(f"  {pid:12s} ${resell_setup[0]:>7,}-${resell_setup[1]:>7,}  "
              f"${resell_monthly[0]:>7,}-${resell_monthly[1]:>7,}  "
              f"${markup_setup:>7,}+${markup_monthly:>6,}/mes")
    print()

    print(f"  {'─'*80}")
    print("  🔍  EJEMPLO: Si vendes a cliente a precio medio de reventa...")
    print(f"  {'─'*80}")
    for pid, plan in plans.items():
        w_setup = plan["setup_fee"]
        w_monthly = plan["monthly"]
        r_setup = sum(plan["suggested_resell_setup"]) // 2
        r_monthly = sum(plan["suggested_resell_monthly"]) // 2
        p_setup = r_setup - w_setup
        p_monthly = r_monthly - w_monthly
        y1_sdc = w_setup + w_monthly * 12
        y1_partner = p_setup + p_monthly * 12
        print(f"  {pid:12s} Tú: ${w_setup:,}+${w_monthly:,}/mo  Partner: ${p_setup:,}+${p_monthly:,}/mo  → Año 1: SDC ${y1_sdc:,} | Partner ${y1_partner:,}")
    print()


def show_plan(plan_id: str) -> str:
    pkgs = load_packages()
    plans = pkgs.get("enterprise_wholesale", {})
    plan = plans.get(plan_id)
    if not plan:
        available = list(plans.keys())
        return json.dumps({"error": f"Plan '{plan_id}' not found", "available": available}, indent=2)
    return json.dumps(plan, indent=2, ensure_ascii=False)


def calculate_deal(plan_id: str, resell_setup: float, resell_monthly: float, powered_by: str = "hidden") -> str:
    pkgs = load_packages()
    plans = pkgs.get("enterprise_wholesale", {})
    plan = plans.get(plan_id)
    if not plan:
        return json.dumps({"error": f"Plan '{plan_id}' not found"})

    wholesale_setup = plan["setup_fee"]
    wholesale_monthly = plan["monthly"]

    # Powered by discount
    pb_levels = pkgs.get("powered_by_sdc", {})
    pb_cfg = pb_levels.get(powered_by, {"discount_pct": 0, "label": "Hidden"})
    discount_pct = pb_cfg["discount_pct"]
    monthly_discount = round(wholesale_monthly * discount_pct / 100, 2)
    wholesale_monthly_discounted = wholesale_monthly - monthly_discount

    partner_markup_setup = round(resell_setup - wholesale_setup, 2)
    partner_markup_monthly = round(resell_monthly - wholesale_monthly_discounted, 2)

    y1_sdc = wholesale_setup + wholesale_monthly_discounted * 12
    y1_partner = partner_markup_setup + partner_markup_monthly * 12

    return json.dumps({
        "plan": plan_id,
        "plan_name": plan["name"],
        "powered_by": {"level": powered_by, "label": pb_cfg["label"], "discount_pct": discount_pct, "monthly_discount": monthly_discount},
        "wholesale": {"setup": wholesale_setup, "monthly": wholesale_monthly_discounted},
        "partner_suggested_resell": {"setup": plan["suggested_resell_setup"], "monthly": plan["suggested_resell_monthly"]},
        "this_deal": {
            "partner_charges_client": {"setup": resell_setup, "monthly": resell_monthly},
            "partner_markup": {"setup": partner_markup_setup, "monthly": partner_markup_monthly},
        },
        "year_1_projection": {
            "sdc_wholesale": round(y1_sdc, 2),
            "partner_markup": round(y1_partner, 2),
            "client_total": round(resell_setup + resell_monthly * 12, 2),
        },
    }, indent=2, ensure_ascii=False)


def show_powered_levels():
    pkgs = load_packages()
    levels = pkgs.get("powered_by_sdc", {})
    print(f"\n{'═'*70}")
    print("  ⚡  POWERED BY SDC — Descuentos por visibilidad de marca")
    print(f"{'═'*70}\n")
    print(f"  {'Nivel':20s} {'Desc':>8s} {'Requisito'}")
    print(f"  {'─'*70}")
    for lid, lvl in levels.items():
        print(f"  {lid:20s} -{lvl['discount_pct']:>2d}%  {lvl['requirement'][:50]}")
    print()


def main():
    parser = argparse.ArgumentParser(description="SDC Enterprise Packages")
    parser.add_argument("--enterprise", action="store_true", help="Show enterprise wholesale plans")
    parser.add_argument("--show", metavar="PLAN", help="Show plan details (starter, business, premium)")
    parser.add_argument("--calculate-deal", nargs=3, metavar=("PLAN", "R_SETUP", "R_MONTHLY"), help="Calculate deal: what you earn vs partner markup")
    parser.add_argument("--powered-by", default="hidden", choices=["hidden", "footer_only", "public_mentions", "full_branding"])
    parser.add_argument("--powered-levels", action="store_true", help="Show powered-by SDC levels")

    args = parser.parse_args()

    if args.enterprise:
        show_enterprise()
    elif args.show:
        print(show_plan(args.show))
    elif args.calculate_deal:
        plan, r_setup, r_monthly = args.calculate_deal
        print(calculate_deal(plan, float(r_setup), float(r_monthly), args.powered_by))
    elif args.powered_levels:
        show_powered_levels()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
