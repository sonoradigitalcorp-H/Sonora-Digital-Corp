#!/usr/bin/env python3
"""SDC Product Engine — Catálogo de mini servicios / productos.
Carga products/registry.yaml y expone APIs, CLI, FAQs, cache config.

Usage:
  python3 products/engine.py list                           → Lista todos los productos
  python3 products/engine.py show cyber-diagnosis           → Detalle del producto
  python3 products/engine.py faq cyber-diagnosis            → FAQs del producto
  python3 products/engine.py cache cyber-diagnosis          → Política de cache
  python3 products/engine.py search "ssl"                   → Buscar productos
"""
import json
import sys
import yaml
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
REGISTRY = BASE / "products" / "registry.yaml"


class ProductEngine:
    def __init__(self):
        self._products = {}
        self._load()

    def _load(self):
        if REGISTRY.exists():
            data = yaml.safe_load(REGISTRY.read_text())
            for p in data.get("products", []):
                self._products[p["id"]] = p

    def list(self, category=None, tier=None):
        results = []
        for p in self._products.values():
            if category and p.get("category") != category:
                continue
            if tier and tier not in p.get("tier", []):
                continue
            results.append({
                "id": p["id"],
                "name": p["name"],
                "entity": p.get("entity", ""),
                "tagline": p.get("tagline", ""),
                "category": p.get("category", ""),
                "price": p.get("price_mxn", {}),
                "features": len(p.get("features", [])),
            })
        return results

    def get(self, product_id):
        p = self._products.get(product_id)
        if not p:
            return None
        return p

    def faq(self, product_id):
        p = self._products.get(product_id)
        if not p:
            return None
        return p.get("faqs", [])

    def cache_policy(self, product_id):
        p = self._products.get(product_id)
        if not p:
            return None
        return p.get("cache", "No cache policy defined")

    def auth_policy(self, product_id):
        p = self._products.get(product_id)
        if not p:
            return None
        return p.get("auth", "No auth policy defined")

    def search(self, query):
        q = query.lower()
        results = []
        for p in self._products.values():
            if q in p["id"].lower() or q in p["name"].lower() or q in p.get("tagline", "").lower():
                results.append({
                    "id": p["id"],
                    "name": p["name"],
                    "tagline": p.get("tagline", ""),
                    "price": p.get("price_mxn", {}),
                })
        return results

    def categories(self):
        cats = {}
        for p in self._products.values():
            cat = p.get("category", "other")
            if cat not in cats:
                cats[cat] = []
            cats[cat].append(p["id"])
        return cats

    def by_skill(self, skill_name):
        """Encuentra productos que usan una skill específica."""
        results = []
        for p in self._products.values():
            if skill_name in p.get("skills", []):
                results.append(p["id"])
        return results


engine = ProductEngine()


def main():
    if len(sys.argv) < 2:
        print("Usage: products/engine.py <command> [args]")
        print("Commands: list, show, faq, cache, auth, search, categories")
        return

    cmd = sys.argv[1]

    if cmd == "list":
        cat = sys.argv[2] if len(sys.argv) > 2 else None
        tier = sys.argv[3] if len(sys.argv) > 3 else None
        items = engine.list(cat, tier)
        print(f"\n{'='*60}")
        print(f"  SDC Product Catalog — {len(items)} products")
        print(f"{'='*60}")
        for p in items:
            price_str = " | ".join(f"{t}: ${v}" for t, v in p["price"].items() if v > 0)
            free = "🆓" if p["price"].get("free") == 0 else ""
            print(f"\n  {free} {p['id']}")
            print(f"     {p['name']} — {p['entity']}")
            print(f"     {p['tagline'][:80]}")
            print(f"     [{p['category']}] {price_str}")
        print()

    elif cmd == "show":
        pid = sys.argv[2] if len(sys.argv) > 2 else ""
        p = engine.get(pid)
        if not p:
            print(f"Producto '{pid}' no encontrado")
            return
        print(f"\n{'='*60}")
        print(f"  {p['name']}")
        print(f"  Entity: {p.get('entity', 'N/A')}")
        print(f"  Tagline: {p.get('tagline', '')}")
        print(f"  Category: {p.get('category', '')}")
        print(f"  Tiers: {', '.join(p.get('tier', []))}")
        print(f"  Price: {json.dumps(p.get('price_mxn', {}))}")
        print(f"  Skills: {', '.join(p.get('skills', []))}")
        print(f"{'='*60}")
        for f in p.get("features", []):
            print(f"  ✅ {f}")
        print(f"\n  Events: {', '.join(p.get('events', []))}")
        print(f"  Triggers: {', '.join(p.get('triggers', []))}")

    elif cmd == "faq":
        pid = sys.argv[2] if len(sys.argv) > 2 else ""
        faqs = engine.faq(pid)
        if faqs is None:
            print(f"Producto '{pid}' no encontrado")
            return
        if not faqs:
            print("No FAQs defined")
            return
        print(f"\n  FAQs — {pid}")
        print(f"{'='*60}")
        for faq in faqs:
            print(f"\n  ❓ {faq['p']}")
            print(f"  💬 {faq['r']}")

    elif cmd == "cache":
        pid = sys.argv[2] if len(sys.argv) > 2 else ""
        policy = engine.cache_policy(pid)
        if policy is None:
            print(f"Producto '{pid}' no encontrado")
            return
        print(f"\n  Cache Policy — {pid}")
        print(f"{'='*60}")
        print(policy)

    elif cmd == "auth":
        pid = sys.argv[2] if len(sys.argv) > 2 else ""
        policy = engine.auth_policy(pid)
        if policy is None:
            print(f"Producto '{pid}' no encontrado")
            return
        print(f"\n  Auth Policy — {pid}")
        print(f"{'='*60}")
        print(policy)

    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        results = engine.search(query)
        print(f"\n  Search: '{query}' — {len(results)} results")
        for r in results:
            print(f"  🛒 {r['id']}: {r['name']} — {r['tagline'][:60]}")

    elif cmd == "categories":
        cats = engine.categories()
        print(f"\n  Categories ({len(cats)})")
        for cat, prods in sorted(cats.items()):
            print(f"  [{cat}] {', '.join(prods)}")

    elif cmd == "by-skill":
        skill = sys.argv[2] if len(sys.argv) > 2 else ""
        prods = engine.by_skill(skill)
        print(f"\n  Products using skill '{skill}': {', '.join(prods) if prods else 'None'}")

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
