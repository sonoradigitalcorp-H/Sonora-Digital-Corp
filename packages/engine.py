#!/usr/bin/env python3
"""SDC Package Engine — 5 Layers
Layer 1: Package Builder — combina productos en paquetes
Layer 2: Dependency Mapper — skills + tools → packages
Layer 3: Subscription Engine — clientes → packages → billing
Layer 4: Validator — verifica skills/tools existen
Layer 5: Generator — genera configs (nginx, systemd, env)
"""
import json
import os
import sys
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent.parent
PRODUCTS_FILE = BASE / "products" / "registry.yaml"
PACKAGES_FILE = BASE / "packages" / "registry.yaml"
SKILLS_DIR = BASE / "skills"
TOOLS_FILE = BASE / "tools" / "registry.json"


def _ok(data=None, message=""):
    return {"status": "ok", "data": data or {}, "message": message}

def _err(error, code=400):
    return {"status": "error", "error": error, "code": code}


class PackageEngine:
    def __init__(self):
        self.packages = {}
        self.products = {}
        self.skills = set()
        self.tools = set()
        self._load()

    def _load(self):
        if PACKAGES_FILE.exists():
            data = yaml.safe_load(PACKAGES_FILE.read_text())
            for p in data.get("packages", []):
                self.packages[p["id"]] = p
        if PRODUCTS_FILE.exists():
            data = yaml.safe_load(PRODUCTS_FILE.read_text())
            for p in data.get("products", []):
                self.products[p["id"]] = p
        def _add_skill(name):
            """Normalize skill name: remove extension."""
            n = name.replace(".skill.md", "").replace(".SKILL.md", "").replace(".py", "").replace(".sh", "")
            self.skills.add(n)

        for d in [SKILLS_DIR, BASE / "scripts", BASE / "ops"] + [x for x in BASE.glob("products/*/") if x.is_dir()]:
            if not d.exists():
                continue
            for f in d.iterdir():
                if f.is_file() and (f.name.endswith((".skill.md", ".py", ".sh"))):
                    _add_skill(f.name)
                if f.is_dir() and (f / "SKILL.md").exists():
                    _add_skill(f.name)
                if f.is_dir() and (f / "cli.py").exists():
                    _add_skill(f.name)
        for svc in ["wacli", "hermes-gateway", "hermes", "openclaw", "lora_mcp", "omnivoice_mcp"]:
            _add_skill(svc)
        # Scan tools from registry
        if TOOLS_FILE.exists():
            data = json.loads(TOOLS_FILE.read_text())
            for t in data.get("tools", []):
                self.tools.add(t["name"])

    # ─── Layer 1: Package Builder ───

    def list(self, tier=None):
        results = []
        for p in self.packages.values():
            if tier and p.get("tier") != tier:
                continue
            products_included = []
            total_individual = 0
            for pid in p.get("products", []):
                prod = self.products.get(pid, {})
                prices = prod.get("price_mxn", {})
                price = prices.get(p["tier"], 0) or prices.get("pro", 0) or prices.get("enterprise", 0) or 0
                total_individual += price
                products_included.append({"id": pid, "name": prod.get("name", pid), "individual_price": price})
            results.append({
                "id": p["id"],
                "name": p["name"],
                "tier": p.get("tier"),
                "price": p.get("price_mxn", 0),
                "discount": p.get("discount", 0),
                "total_individual": total_individual,
                "you_save": total_individual - p.get("price_mxn", 0),
                "products": products_included,
                "features": p.get("features", []),
                "limits": p.get("limits", {}),
            })
        return _ok(results)

    def show(self, pid):
        p = self.packages.get(pid)
        if not p:
            return _err(f"Package '{pid}' not found", 404)
        return _ok(p)

    # ─── Layer 2: Dependency Mapper ───

    def deps(self, pid):
        """Muestra skills + tools requeridas por el paquete y su estado."""
        p = self.packages.get(pid)
        if not p:
            return _err(f"Package '{pid}' not found", 404)

        skills_status = []
        for s in p.get("skills_required", []):
            s_clean = s.replace(".skill.md", "").replace(".py", "").replace(".sh", "").replace("ops/", "")
            exists = s in self.skills or s_clean in self.skills
            skills_status.append({"name": s, "exists": exists, "source": "file" if exists else "missing"})

        tools_status = []
        for t in p.get("tools_required", []):
            exists = t in self.tools
            tools_status.append({"name": t, "exists": exists, "source": "mcp" if exists else "missing"})

        return _ok({
            "package": pid,
            "skills": {"required": len(p.get("skills_required", [])), "available": sum(1 for s in skills_status if s["exists"]), "items": skills_status},
            "tools": {"required": len(p.get("tools_required", [])), "available": sum(1 for t in tools_status if t["exists"]), "items": tools_status},
        })

    # ─── Layer 3: Validator ───

    def validate(self, pid=None):
        """Valida consistencia del paquete: productos existen, skills existen, precios OK."""
        to_check = [pid] if pid else self.packages.keys()
        errors = []
        warnings = []

        for pid in to_check:
            p = self.packages.get(pid)
            if not p:
                errors.append(f"Package '{pid}' not found in registry")
                continue

            # Check products exist
            for prod_id in p.get("products", []):
                if prod_id not in self.products:
                    errors.append(f"[{pid}] Product '{prod_id}' not in product registry")

            for s in p.get("skills_required", []):
                s_clean = s.replace(".skill.md", "").replace(".py", "").replace(".sh", "").replace("ops/", "")
                found = s in self.skills or s_clean in self.skills
                if not found:
                    warnings.append(f"[{pid}] Skill '{s}' not found")

            # Check tools exist
            for t in p.get("tools_required", []):
                if t not in self.tools:
                    warnings.append(f"[{pid}] Tool '{t}' not in MCP registry")

            # Check price consistency
            total_individual = 0
            for prod_id in p.get("products", []):
                prod = self.products.get(prod_id, {})
                prices = prod.get("price_mxn", {})
                price = prices.get(p.get("tier", "pro"), 0)
                total_individual += price
            if p.get("price_mxn", 0) > total_individual and total_individual > 0:
                warnings.append(f"[{pid}] Package price (${p['price_mxn']}) > sum of products (${total_individual})")

        return _ok({
            "checked": len(to_check),
            "errors": errors,
            "warnings": warnings,
            "passed": len(errors) == 0,
        })

    # ─── Layer 4: Subscription Engine ───

    def subscribe(self, client_email, package_id, tier=None):
        """Simula suscripción de un cliente a un paquete."""
        p = self.packages.get(package_id)
        if not p:
            return _err(f"Package '{package_id}' not found", 404)
        return _ok({
            "client": client_email,
            "package": package_id,
            "plan": p["name"],
            "price": p.get("price_mxn", 0),
            "billing": "monthly",
            "status": "active",
            "features": p.get("features", []),
            "limits": p.get("limits", {}),
        }, f"Cliente {client_email} suscrito a {p['name']}")

    def estimate(self, package_ids):
        """Estima costo de combinar múltiples paquetes."""
        total = 0
        products_set = set()
        items = []
        for pid in package_ids:
            p = self.packages.get(pid)
            if not p:
                continue
            total += p.get("price_mxn", 0)
            products_set.update(p.get("products", []))
            items.append({"id": pid, "name": p["name"], "price": p.get("price_mxn", 0)})
        return _ok({
            "packages": items,
            "total": total,
            "unique_products": len(products_set),
        })

    # ─── Layer 5: Generator ───

    def generate(self, pid, output_dir=None):
        """Genera configs para el paquete (env, systemd, nginx)."""
        p = self.packages.get(pid)
        if not p:
            return _err(f"Package '{pid}' not found", 404)

        out = Path(output_dir or "/tmp/sdc-gen")
        out.mkdir(parents=True, exist_ok=True)

        generated = []

        # Generate .env
        env_lines = [f"# SDC Package: {p['name']}", f"PACKAGE_ID={pid}", f"PACKAGE_TIER={p.get('tier','')}"]
        env_file = out / f"{pid}.env"
        env_file.write_text("\n".join(env_lines) + "\n")
        generated.append(f".env: {env_file}")

        # Generate systemd override
        if p.get("systemd_services"):
            for svc in p["systemd_services"]:
                override_dir = out / "systemd-overrides"
                override_dir.mkdir(parents=True, exist_ok=True)
                override = override_dir / f"{svc}.conf"
                override.write_text(f"[Service]\nEnvironment=PACKAGE_ID={pid}\n")
                generated.append(f"systemd: {override}")

        # Generate nginx snippet
        if p.get("nginx_configs"):
            nginx_dir = out / "nginx"
            nginx_dir.mkdir(parents=True, exist_ok=True)
            nginx_conf = nginx_dir / f"package-{pid}.conf"
            nginx_conf.write_text(f"# Package: {p['name']}\n# Incluir en server block\n")
            generated.append(f"nginx: {nginx_conf}")

        # Generate limits config
        if p.get("limits"):
            limits_file = out / f"{pid}-limits.json"
            limits_file.write_text(json.dumps(p["limits"], indent=2))
            generated.append(f"limits: {limits_file}")

        return _ok({"package": pid, "files": generated}, f"Generated {len(generated)} files in {out}")


engine = PackageEngine()


def main():
    if len(sys.argv) < 2:
        print("Usage: packages/engine.py <command> [args]")
        print("\nCommands:")
        print("  list [tier]              List packages (free/pro/enterprise)")
        print("  show <id>                Show package details")
        print("  deps <id>                Show dependencies (skills+tools)")
        print("  validate [id]            Validate package(s)")
        print("  subscribe <email> <id>   Simulate subscription")
        print("  estimate <id1,id2,...>   Estimate multi-package cost")
        print("  generate <id> [outdir]   Generate config files")
        return

    cmd = sys.argv[1]

    if cmd == "list":
        tier = sys.argv[2] if len(sys.argv) > 2 else None
        r = engine.list(tier)
        if r["status"] == "ok":
            print(f"\n{'='*70}")
            print(f"  SDC Packages — {len(r['data'])} available")
            print(f"{'='*70}")
            for p in r["data"]:
                tag = "🆓" if p["tier"] == "free" else "⭐" if p["tier"] == "pro" else "🏢"
                print(f"\n  {tag} {p['name']} ({p['id']})")
                print(f"     ${p['price']}/mo — ahorras ${p['you_save']} vs individual")
                print(f"     Productos: {', '.join(x['name'][:25] for x in p['products'])}")
                for f in p["features"][:3]:
                    print(f"       ✅ {f}")
            print()

    elif cmd == "show":
        r = engine.show(sys.argv[2])
        if r["status"] == "ok":
            p = r["data"]
            print(f"\n  {p['name']} ({p['id']})")
            print(f"  Tier: {p.get('tier')} | ${p.get('price_mxn',0)}/mo")
            print(f"  Products: {', '.join(p.get('products',[]))}")
            print(f"  Features:")
            for f in p.get("features", []):
                print(f"    ✅ {f}")
            print(f"  Limits: {json.dumps(p.get('limits',{}), indent=4)}")

    elif cmd == "deps":
        r = engine.deps(sys.argv[2])
        if r["status"] == "ok":
            d = r["data"]
            print(f"\n  Dependencies for: {d['package']}")
            print(f"  Skills: {d['skills']['available']}/{d['skills']['required']} available")
            for s in d["skills"]["items"]:
                icon = "✅" if s["exists"] else "❌"
                print(f"    {icon} {s['name']}")
            print(f"  Tools: {d['tools']['available']}/{d['tools']['required']} available")
            for t in d["tools"]["items"]:
                icon = "✅" if t["exists"] else "❌"
                print(f"    {icon} {t['name']}")

    elif cmd == "validate":
        pid = sys.argv[2] if len(sys.argv) > 2 else None
        r = engine.validate(pid)
        if r["status"] == "ok":
            v = r["data"]
            print(f"\n  Validation: {v['checked']} packages checked")
            if not v["errors"] and not v["warnings"]:
                print("  ✅ All perfect")
            if v["errors"]:
                print(f"\n  ❌ Errors ({len(v['errors'])}):")
                for e in v["errors"]:
                    print(f"    {e}")
            if v["warnings"]:
                print(f"\n  ⚠️  Warnings ({len(v['warnings'])}):")
                for w in v["warnings"]:
                    print(f"    {w}")

    elif cmd == "subscribe":
        email = sys.argv[2]
        pid = sys.argv[3]
        r = engine.subscribe(email, pid)
        print(f"\n  {'✅' if r['status']=='ok' else '❌'} {r.get('message','')}")

    elif cmd == "estimate":
        ids = sys.argv[2].split(",")
        r = engine.estimate(ids)
        if r["status"] == "ok":
            d = r["data"]
            print(f"\n  Estimate for {len(d['packages'])} packages")
            for pkg in d["packages"]:
                print(f"    {pkg['name']}: ${pkg['price']}")
            print(f"  Total: ${d['total']}")
            print(f"  Unique products: {d['unique_products']}")

    elif cmd == "generate":
        pid = sys.argv[2]
        outdir = sys.argv[3] if len(sys.argv) > 3 else None
        r = engine.generate(pid, outdir)
        if r["status"] == "ok":
            print(f"\n  Generated {len(r['data']['files'])} files:")
            for f in r["data"]["files"]:
                print(f"    📄 {f}")

    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()
