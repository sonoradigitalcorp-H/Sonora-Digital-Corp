"""Pricing Engine — Dynamic pricing calculator for multi-tenant brain platform.

Calculates setup fee, monthly maintenance, and revenue share per client
based on industry, size, estimated volume, and partner discounts.
"""

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def load_rates() -> dict:
    import yaml
    rates_path = REPO / "config" / "pricing-tiers.yaml"
    if rates_path.exists():
        with open(rates_path) as f:
            return yaml.safe_load(f)
    return {"industries": {}, "partner_discounts": {}}


def calculate_price(
    industry: str,
    size: str = "small",
    volume_multiplier: float = 1.0,
    partner: str = "",
    revenue_estimated_monthly: float = 0,
) -> dict:
    tiers = load_rates()
    ind = tiers.get("industries", {}).get(industry)
    if not ind:
        return {"error": f"Unknown industry: {industry}", "available": list(tiers.get("industries", {}).keys())}

    if size not in ind["setup_fee"]:
        size = "small"

    setup_fee = ind["setup_fee"][size]
    monthly_base = ind["monthly_base"][size]
    markup = ind["markup_multiplier"]
    rev_share = ind["revenue_share_pct"]

    # Apply volume multiplier
    monthly = monthly_base * volume_multiplier

    # Partner discount
    discounts = tiers.get("partner_discounts", {})
    partner_discount = discounts.get(partner, discounts.get("default", 0))
    partner_monthly = monthly * (1 - partner_discount)
    partner_setup = setup_fee * (1 - partner_discount)

    # Revenue share floor
    rev_share_floor = max(revenue_estimated_monthly * (rev_share / 100), 100)

    return {
        "industry": industry,
        "size": size,
        "setup_fee": round(setup_fee, 2),
        "monthly_base": round(monthly, 2),
        "markup_multiplier": markup,
        "revenue_share_pct": rev_share,
        "revenue_share_estimated_monthly": round(rev_share_floor, 2),
        "partner_monthly": round(partner_monthly, 2) if partner else None,
        "partner_setup": round(partner_setup, 2) if partner else None,
        "partner_discount_pct": round(partner_discount * 100),
        "total_estimated_monthly": round(
            partner_monthly + rev_share_floor if partner else monthly + rev_share_floor, 2
        ),
        "notes": ind.get("notes", ""),
    }


def calculate_from_cost(
    estimated_monthly_cost: float,
    industry: str = "tecnologia",
    partner: str = "",
    target_margin: float = 0.80,
) -> dict:
    tiers = load_rates()
    ind = tiers.get("industries", {}).get(industry, {"markup_multiplier": 4.0, "revenue_share_pct": 5})

    # Calculate price based on cost + target margin
    required_revenue = estimated_monthly_cost / (1 - target_margin)
    markup = ind.get("markup_multiplier", 4.0)
    monthly = round(required_revenue / markup, 2)
    rev_share = ind.get("revenue_share_pct", 5)

    discounts = tiers.get("partner_discounts", {})
    partner_discount = discounts.get(partner, discounts.get("default", 0))
    partner_monthly = round(monthly * (1 - partner_discount), 2)

    return {
        "estimated_monthly_cost": round(estimated_monthly_cost, 2),
        "target_margin_pct": round(target_margin * 100),
        "required_revenue": round(required_revenue, 2),
        "suggested_monthly": monthly,
        "partner_monthly": partner_monthly if partner else None,
        "revenue_share_pct": rev_share,
        "margin_pct": round((1 - estimated_monthly_cost / max(required_revenue, 1)) * 100, 1),
    }


def list_industries() -> str:
    tiers = load_rates()
    inds = tiers.get("industries", {})
    result = []
    for k, v in inds.items():
        result.append({
            "id": k,
            "label": v["label"],
            "setup_range": f"${v['setup_fee']['small']} - ${v['setup_fee']['enterprise']}",
            "monthly_range": f"${v['monthly_base']['small']} - ${v['monthly_base']['enterprise']}",
            "rev_share": f"{v['revenue_share_pct']}%",
        })
    return json.dumps({"industries": result}, indent=2)


def main():
    parser = argparse.ArgumentParser(description="SDC Pricing Engine")
    parser.add_argument("--industry", default="tecnologia", help="Industry segment")
    parser.add_argument("--size", default="small", choices=["small", "medium", "enterprise"])
    parser.add_argument("--volume", type=float, default=1.0, help="Volume multiplier")
    parser.add_argument("--partner", default="", help="Partner ID for discount")
    parser.add_argument("--cost", type=float, default=0, help="Estimated monthly cost (alternative calculation)")
    parser.add_argument("--margin", type=float, default=0.80, help="Target margin (0-1)")
    parser.add_argument("--list-industries", action="store_true", help="List available industries")

    args = parser.parse_args()

    if args.list_industries:
        print(list_industries())
        return

    if args.cost > 0:
        result = calculate_from_cost(args.cost, args.industry, args.partner, args.margin)
    else:
        result = calculate_price(args.industry, args.size, args.volume, args.partner)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
