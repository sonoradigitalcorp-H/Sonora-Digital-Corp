"""SDC Packages CLI — Muestra todos los paquetes, calcula precios, y compara planes.

Usage:
  python3 scripts/packages.py --list                  # Todos los paquetes
  python3 scripts/packages.py --show artist           # Un paquete específico
  python3 scripts/packages.py --compare pro premium   # Compara dos paquetes
  python3 scripts/packages.py --calculate partner 50  # Calcula costo para partner con 50 clientes
"""

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def load_packages() -> dict:
    import yaml
    path = REPO / "config" / "packages.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def list_all():
    pkgs = load_packages()
    result = []

    for category, label in [("consumers", "CONSUMIDORES"), ("partners", "PARTNERS"),
                            ("ambassadors", "EMBAJADORES"), ("enterprise", "EMPRESA")]:
        items = pkgs.get(category, {})
        if isinstance(items, dict) and "name" in items:
            items = {"plan": items}

        if isinstance(items, dict):
            for plan_id, plan in items.items():
                price = plan.get("price_usd", plan.get("commission_pct", "?"))
                setup = plan.get("setup_fee", plan.get("commission_on", "?"))
                result.append({
                    "category": label,
                    "plan_id": plan_id,
                    "name": plan.get("name", plan_id),
                    "price": f"${price}" if isinstance(price, (int, float)) else str(price),
                    "setup": f"${setup}" if isinstance(setup, (int, float)) else str(setup),
                    "audience": plan.get("audience", ""),
                    "tagline": plan.get("tagline", ""),
                })

    return result


def show_plan(category: str, plan_id: str) -> dict:
    pkgs = load_packages()
    cat = pkgs.get(category, {})
    if isinstance(cat, dict) and "name" in cat:
        if category == "enterprise":
            return cat
        return {"error": f"Category '{category}' has no sub-plans. Use --list"}

    plan = cat.get(plan_id)
    if not plan:
        available = list(cat.keys())
        return {"error": f"Plan '{plan_id}' not found in {category}", "available": available}
    return plan


def calculate_partner_cost(partner_plan: str, client_count: int, client_plan: str = "pro") -> dict:
    pkgs = load_packages()
    partners = pkgs.get("partners", {})
    plan = partners.get(partner_plan)
    if not plan:
        return {"error": f"Partner plan '{partner_plan}' not found"}

    client_slots = plan["includes"]["client_slots"]
    if client_slots != -1 and client_count > client_slots:
        return {"error": f"Plan '{partner_plan}' allows max {client_slots} clients, requested {client_count}"}

    consumers = pkgs.get("consumers", {})
    client_plan_data = consumers.get(client_plan)
    if not client_plan_data:
        return {"error": f"Client plan '{client_plan}' not found"}

    list_price = client_plan_data["price_usd"]
    wholesale_discount = plan["includes"]["margin_pct"]  # % descuento sobre lista
    wholesale_price = list_price * (1 - wholesale_discount / 100)

    partner_flat_fee = plan["price_usd"]
    setup_fee = plan["setup_fee"]

    suggested_resell = round(list_price * 1.0)  # Pueden vender al precio de lista o más
    total_revenue = client_count * suggested_resell
    total_cost = partner_flat_fee + (client_count * wholesale_price)
    profit = total_revenue - total_cost
    profit_per_client = suggested_resell - wholesale_price
    break_even = round(partner_flat_fee / profit_per_client) if profit_per_client > 0 else 0
    effective_cost_per_client = wholesale_price + (partner_flat_fee / max(client_count, 1))

    return {
        "partner_plan": plan["name"],
        "partner_flat_fee": partner_flat_fee,
        "setup_fee": setup_fee,
        "client_count": client_count,
        "client_plan": client_plan_data["name"],
        "list_price": list_price,
        "wholesale_price": round(wholesale_price, 2),
        "wholesale_discount_pct": wholesale_discount,
        "suggested_resell_price": suggested_resell,
        "profit_per_client": round(profit_per_client, 2),
        "effective_cost_per_client_with_fee": round(effective_cost_per_client, 2),
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "monthly_profit": round(profit, 2),
        "profit_margin_pct": round((profit / total_revenue) * 100, 1) if total_revenue > 0 else 0,
        "break_even_clients": break_even,
        "max_clients": "Unlimited" if client_slots == -1 else client_slots,
        "scaling": [
            {"clients": c, "profit": round(c * profit_per_client - partner_flat_fee, 2)}
            for c in [client_count, break_even, client_slots if client_slots != -1 else client_count * 2]
            if c > 0 and c != client_count
        ],
        "revenue_example": plan.get("revenue_example", ""),
    }


def calculate_ambassador_commission(plan_id: str, client_count: int, client_plan: str = "pro") -> dict:
    pkgs = load_packages()
    ambassadors = pkgs.get("ambassadors", {})
    amb = ambassadors.get(plan_id)
    if not amb:
        return {"error": f"Ambassador plan '{plan_id}' not found"}

    consumers = pkgs.get("consumers", {})
    client = consumers.get(client_plan)
    if not client:
        return {"error": f"Client plan '{client_plan}' not found"}

    setup_fee = client["setup_fee"]
    monthly = client["price_usd"]
    commission_pct = amb["commission_pct"]
    months = 3 if plan_id == "basic" else 6

    commission_per_client = (setup_fee + monthly * months) * (commission_pct / 100)
    total = commission_per_client * client_count

    return {
        "ambassador_plan": amb["name"],
        "commission_pct": commission_pct,
        "commission_months": months,
        "clients_referred": client_count,
        "commission_per_client": round(commission_per_client, 2),
        "total_commission": round(total, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="SDC Packages — Planes y precios")
    parser.add_argument("--list", action="store_true", help="Listar todos los paquetes")
    parser.add_argument("--show", nargs=2, metavar=("CATEGORY", "PLAN"), help="Mostrar detalle de un plan (ej: --show consumers artist)")
    parser.add_argument("--compare", nargs=2, metavar=("PLAN_A", "PLAN_B"), help="Comparar dos planes (ej: --compare pro premium)")
    parser.add_argument("--calculate-partner", nargs=3, metavar=("PLAN", "CLIENTS", "CLIENT_PLAN"), help="Calcular costo partner (ej: --calculate-partner business 50 pro)")
    parser.add_argument("--calculate-ambassador", nargs=3, metavar=("PLAN", "CLIENTS", "CLIENT_PLAN"), help="Calcular comisión embajador (ej: --calculate-ambassador pro 10 artist)")

    args = parser.parse_args()

    if args.list:
        plans = list_all()
        print(f"\n{'═'*80}")
        print(f"  📦  SDC PACKAGES — Todos los planes")
        print(f"{'═'*80}\n")
        current_cat = ""
        for p in plans:
            if p["category"] != current_cat:
                current_cat = p["category"]
                print(f"  ┌─ {current_cat} ───────────────────────────────────────")
            price_str = f"${p['price']}" if not p['price'].startswith('$') else p['price']
            print(f"  │ {p['plan_id']:15s} │ {p['name']:20s} │ {price_str:>8s} │ {p['tagline']}")
        print(f"  └──────────────────────────────────────────────────────")
        print()

    elif args.show:
        cat, plan_id = args.show
        result = show_plan(cat, plan_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.compare:
        a_id, b_id = args.compare
        all_plans = list_all()
        a = next((p for p in all_plans if p["plan_id"] == a_id), None)
        b = next((p for p in all_plans if p["plan_id"] == b_id), None)
        if not a or not b:
            print(json.dumps({"error": "Plan not found"}))
            return
        print(f"\n{'═'*60}")
        print(f"  COMPARACIÓN: {a['name']:20s} vs {b['name']}")
        print(f"{'═'*60}")
        print(f"  {'Concepto':25s} {a['name']:20s} {b['name']}")
        print(f"  {'─'*60}")
        print(f"  {'Precio':25s} {a['price']:>10s}          {b['price']:>10s}")
        print(f"  {'Setup':25s} {a['setup']:>10s}          {b['setup']:>10s}")
        print(f"  {'Audiencia':25s} {a['audience'][:20]:20s} {b['audience'][:20]:20s}")
        print()

    elif args.calculate_partner:
        plan, clients, client_plan = args.calculate_partner
        result = calculate_partner_cost(plan, int(clients), client_plan)
        if "error" in result:
            print(json.dumps(result, indent=2))
            return
        print(f"\n{'═'*60}")
        print(f"  🤝  PARTNER {result['partner_plan']} — {clients} clientes {result['client_plan']}")
        print(f"{'═'*60}")
        print(f"  Tu flat fee mensual:  ${result['partner_flat_fee']:>8.2f}")
        print(f"  Setup fee único:      ${result['setup_fee']:>8.2f}")
        print(f"  Descuento mayorista:   {result['wholesale_discount_pct']}% OFF")
        print(f"  Precio lista:          ${result['list_price']:>8.2f}/cliente")
        print(f"  Tu costo mayoreo:      ${result['wholesale_price']:>8.2f}/cliente")
        print(f"  Precio sugerido venta: ${result['suggested_resell_price']:>8.2f}/cliente")
        print(f"  Ganancia por cliente:  ${result['profit_per_client']:>8.2f}")
        print(f"  {'─'*60}")
        print(f"  Ingreso total:        ${result['total_revenue']:>8.2f}")
        print(f"  Tu costo total:       ${result['total_cost']:>8.2f}")
        print(f"  🟢  GANANCIA MENSUAL: ${result['monthly_profit']:>8.2f} ({result['profit_margin_pct']}%)")
        print(f"  Break-even:           {result['break_even_clients']} clientes")
        if result.get("scaling"):
            print(f"  Proyecciones:")
            for s in result["scaling"]:
                print(f"    → {s['clients']:>5d} clientes: ${s['profit']:>8.2f}/mes")
        print(f"\n  {result['revenue_example']}")
        print()

    elif args.calculate_ambassador:
        plan, clients, client_plan = args.calculate_ambassador
        result = calculate_ambassador_commission(plan, int(clients), client_plan)
        if "error" in result:
            print(json.dumps(result, indent=2))
            return
        print(f"\n{'═'*50}")
        print(f"  🎯  EMBAJADOR {result['ambassador_plan']}")
        print(f"{'═'*50}")
        print(f"  Comisión:              {result['commission_pct']}%")
        print(f"  Clientes referidos:    {clients}")
        print(f"  Por cliente:           ${result['commission_per_client']}")
        print(f"  🟢  Total comisión:    ${result['total_commission']}")
        print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
