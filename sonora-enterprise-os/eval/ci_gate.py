#!/usr/bin/env python3
"""CI Gate — Ejecuta evals por tenant y falla si score < 80%.

Uso:
    python sonora-enterprise-os/eval/ci_gate.py
    python sonora-enterprise-os/eval/ci_gate.py --tenant sdc-core
    python sonora-enterprise-os/eval/ci_gate.py --threshold 0.9
"""

import argparse
import subprocess
import sys
from pathlib import Path


EVAL_DIR = Path(__file__).parent / "tenants"
TENANTS = ["sdc-core", "abe-fenix", "default"]


def run_evals(tenant: str = None, threshold: float = 0.8) -> dict:
    """Ejecuta evals y retorna resultados por tenant."""
    tenants = [tenant] if tenant else TENANTS
    results = {}

    for t in tenants:
        tenant_dir = EVAL_DIR / t
        if not tenant_dir.exists():
            print(f"⚠️  Tenant {t} no tiene evals, saltando...")
            continue

        print(f"\n{'='*60}")
        print(f"📋 Evaluando tenant: {t}")
        print(f"{'='*60}")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(tenant_dir), "-v", "--tb=short"],
                capture_output=True, text=True, timeout=120
            )
            output = result.stdout + result.stderr
            print(output)

            # Parse results
            passed = output.count("PASSED")
            failed = output.count("FAILED")
            errors = output.count("ERROR")
            total = passed + failed + errors
            score = passed / total if total > 0 else 0

            results[t] = {
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "total": total,
                "score": round(score, 2),
                "gate": "✅ PASS" if score >= threshold else "❌ FAIL",
            }
        except subprocess.TimeoutExpired:
            results[t] = {"error": "timeout", "gate": "❌ FAIL"}
        except Exception as e:
            results[t] = {"error": str(e), "gate": "❌ FAIL"}

    return results


def main():
    parser = argparse.ArgumentParser(description="SDC Eval CI Gate")
    parser.add_argument("--tenant", help="Evaluar solo un tenant")
    parser.add_argument("--threshold", type=float, default=0.8, help="Score mínimo (0-1)")
    args = parser.parse_args()

    results = run_evals(tenant=args.tenant, threshold=args.threshold)

    # Summary
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE EVALUACIONES")
    print(f"{'='*60}")
    for tenant, r in results.items():
        if "error" in r and "passed" not in r:
            print(f"  {tenant}: {r['gate']} ({r['error']})")
        else:
            print(f"  {tenant}: {r['gate']} ({r['passed']}/{r['total']} = {r['score']})")

    # Exit code
    all_pass = all(r.get("gate", "").startswith("✅") for r in results.values())
    if not all_pass:
        print(f"\n❌ CI GATE FAILED — Score mínimo: {args.threshold}")
        sys.exit(1)
    else:
        print(f"\n✅ CI GATE PASSED — Todos los tenants superan {args.threshold}")
        sys.exit(0)


if __name__ == "__main__":
    main()
