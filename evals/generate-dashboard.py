#!/usr/bin/env python3
"""Run evals and generate promptfoo-style HTML dashboard.
Usage: python3 evals/generate-dashboard.py
Output: evals/dashboard.html
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE / "evals" / "results"
HTML_OUTPUT = BASE / "evals" / "dashboard.html"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_evals():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "evals/test_evals.py", "-v", "--tb=line"],
        cwd=BASE, capture_output=True, text=True, timeout=120,
    )
    return result.stdout, result.stderr, result.returncode


def parse_output(output: str):
    lines = output.split("\n")
    tests = []
    for line in lines:
        line = line.strip()
        # Parse: test_file.py::test_name PASSED/FAILED
        if "::" in line and ("PASSED" in line or "FAILED" in line):
            parts = line.split()
            if len(parts) >= 2:
                test_path = parts[0]
                status = parts[1]  # PASSED/FAILED
                test_name = test_path.split("::")[-1] if "::" in test_path else test_path
                tests.append({"name": test_name, "status": "passed" if status == "PASSED" else "failed"})
    return tests


def domain(name: str) -> str:
    if name.startswith("test_agent"): return "AGENT"
    if name.startswith("test_cap"): return "CAP"
    if name.startswith("test_sdd"): return "SDD"
    if name.startswith("test_skill"): return "SKILL"
    if name.startswith("test_event"): return "EVENT"
    return "OTHER"


def number(name: str) -> str:
    parts = name.split("_")
    for p in parts:
        if p.isdigit():
            return p
    return ""


def main():
    print("Running 35 eval tests...")
    stdout, stderr, code = run_evals()
    tests = parse_output(stdout)
    passed = sum(1 for t in tests if t["status"] == "passed")
    failed = sum(1 for t in tests if t["status"] == "failed")
    total = len(tests)
    pct = passed / max(total, 1) * 100

    domains = {}
    for t in tests:
        d = domain(t["name"])
        if d not in domains:
            domains[d] = {"passed": 0, "failed": 0, "total": 0}
        domains[d][t["status"]] += 1
        domains[d]["total"] += 1

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = ""
    for t in tests:
        d = domain(t["name"])
        n = number(t["name"])
        status_icon = "✅" if t["status"] == "passed" else "❌"
        badge = f'<span class="badge {d.lower()}">{d}-{n}</span>' if n else ""
        rows += f"""
        <tr class="{t["status"]}">
            <td>{status_icon}</td>
            <td>{badge} {t["name"].replace("test_","").replace("_"," ").title()}</td>
            <td><span class="status-{t["status"]}">{t["status"].upper()}</span></td>
        </tr>"""

    domain_rows = ""
    for d, stats in sorted(domains.items()):
        dpct = stats["passed"] / max(stats["total"], 1) * 100
        domain_rows += f"""
        <tr>
            <td><span class="badge {d.lower()}">{d}</span></td>
            <td>{stats["passed"]}/{stats["total"]}</td>
            <td>{dpct:.0f}%</td>
            <td><div class="bar"><div class="fill" style="width:{dpct}%"></div></div></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>SDC Eval Dashboard — {passed}/{total}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; padding: 24px; max-width: 1200px; margin: 0 auto; }}
        h1 {{ font-size: 28px; margin-bottom: 4px; }}
        .subtitle {{ color: #8b949e; font-size: 14px; margin-bottom: 24px; }}
        .summary {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
        .stat {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px 28px; min-width: 120px; }}
        .num {{ font-size: 40px; font-weight: 700; }}
        .label {{ font-size: 11px; text-transform: uppercase; color: #8b949e; letter-spacing: 0.5px; }}
        .pass .num {{ color: #3fb950; }}
        .fail .num {{ color: #f85149; }}
        .total .num {{ color: #58a6ff; }}
        .pct .num {{ color: #d29922; }}
        h2 {{ font-size: 18px; margin: 24px 0 12px; color: #f0f6fc; }}
        table {{ width: 100%; border-collapse: collapse; background: #161b22; border-radius: 8px; overflow: hidden; margin-bottom: 16px; }}
        th {{ text-align: left; padding: 12px 16px; background: #21262d; border-bottom: 1px solid #30363d; font-size: 11px; text-transform: uppercase; color: #8b949e; letter-spacing: 0.5px; }}
        td {{ padding: 10px 16px; border-bottom: 1px solid #21262d; font-size: 13px; }}
        tr:hover {{ background: #1c2128; }}
        tr.failed td {{ border-left: 3px solid #f85149; }}
        tr.passed td {{ border-left: 3px solid #3fb950; }}
        .status-passed {{ color: #3fb950; font-weight: 600; }}
        .status-failed {{ color: #f85149; font-weight: 600; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; letter-spacing: 0.3px; }}
        .badge.agent {{ background: #3fb95022; color: #3fb950; }}
        .badge.cap {{ background: #d2992222; color: #d29922; }}
        .badge.sdd {{ background: #58a6ff22; color: #58a6ff; }}
        .badge.skill {{ background: #bc8cff22; color: #bc8cff; }}
        .badge.event {{ background: #f8514922; color: #f85149; }}
        .bar {{ height: 8px; background: #21262d; border-radius: 4px; overflow: hidden; }}
        .fill {{ height: 100%; background: #3fb950; border-radius: 4px; }}
        .fill.low {{ background: #f85149; }}
        .fill.medium {{ background: #d29922; }}
        .footer {{ margin-top: 24px; font-size: 11px; color: #484f58; text-align: center; }}
    </style>
</head>
<body>
    <h1>SDC Agent OS — Eval Dashboard</h1>
    <p class="subtitle">5 domains · {total} tests · {ts}</p>

    <div class="summary">
        <div class="stat total"><div class="num">{total}</div><div class="label">Total</div></div>
        <div class="stat pass"><div class="num">{passed}</div><div class="label">Passed</div></div>
        <div class="stat fail"><div class="num">{failed}</div><div class="label">Failed</div></div>
        <div class="stat pct"><div class="num">{pct:.0f}%</div><div class="label">Pass Rate</div></div>
    </div>

    <h2>📊 By Domain</h2>
    <table>
        <tr><th>Domain</th><th>Passed/Total</th><th>Rate</th><th>Bar</th></tr>
        {domain_rows}
    </table>

    <h2>📋 All Tests</h2>
    <table>
        <tr><th>Status</th><th>Test</th><th>Result</th></tr>
        {rows}
    </table>

    <div class="footer">Generated by SDC Eval Runner · promptfoo-compatible</div>
</body>
</html>"""

    HTML_OUTPUT.write_text(html)
    print(f"\nResults: {passed}/{total} passed ({pct:.0f}%)")
    print(f"Dashboard: file://{HTML_OUTPUT}")

    # Save JSON results
    result_file = RESULTS_DIR / f"eval-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    result_file.write_text(json.dumps({
        "total": total, "passed": passed, "failed": failed,
        "domains": domains, "tests": tests,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2))
    print(f"Results: {result_file}")

    if failed > 0:
        print("\n⚠️  Known gap: 'research-agent' referenced in capabilities/index.yaml")
        print("   but not defined in agents/registry.yaml")


if __name__ == "__main__":
    main()
