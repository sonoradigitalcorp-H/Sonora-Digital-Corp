#!/usr/bin/env python3
"""Evolution Engine — HAS-008
8-module pipeline: Observe → Score → Detect → Propose → Generate → Update → Reflect
"""
import argparse
import json
import sys
from pathlib import Path

from evolution.observer import collect
from evolution.scorecard import calculate, save, load
from evolution.error_detector import detect
from evolution.proposer import propose as run_propose
from evolution.adr_generator import generate as gen_adr
from evolution.prompt_updater import update as update_prompts
from evolution.auto_doc import generate as gen_docs
from evolution.reflector import reflect


REPO = Path(__file__).resolve().parent.parent


def run_observe():
    print("[observe] Collecting metrics...")
    metrics = collect()
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    return metrics


def run_score(metrics):
    print("[score] Calculating score...")
    s = calculate(metrics)
    card = save(s, metrics)
    print(f"  Overall: {s}/100")
    return card


def run_detect(metrics):
    print("[detect] Checking for issues...")
    issues = detect(metrics)
    if issues:
        for issue in issues:
            print(f"  [{issue['severity']}] {issue['subsystem']}: {issue['message']}")
    else:
        print("  No issues detected")
    return issues


def run_propose_phase(metrics, issues):
    print("[propose] Generating improvement proposals...")
    proposals = run_propose(metrics, issues)
    if proposals:
        for p in proposals:
            print(f"  {p['id']}: {p['title']} (impact={p['impact']}, effort={p['effort']})")
    else:
        print("  No proposals generated")
    return proposals


def run_generate(proposals):
    print("[generate] Generating ADRs...")
    for p in proposals:
        p["status"] = "accepted"
        path = gen_adr(p)
        if path:
            print(f"  ADR generated: {path}")


def run_update(proposals):
    print("[update] Updating prompts...")
    for p in proposals:
        updated = update_prompts(p)
        for u in updated:
            print(f"  Updated: {u}")


def run_docs(spec_id, title, tier, summary):
    print("[auto-doc] Generating documentation...")
    path = gen_docs(spec_id, title, tier, summary)
    print(f"  Generated: {path}")
    return path


def run_reflect(metrics, issues, proposals):
    print("[reflect] Meta-cognition...")
    result = reflect(metrics, issues, proposals)
    print(f"  Health: {result['system_health']}")
    for rec in result.get("recommendations", []):
        print(f"  → {rec}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Evolution Engine (HAS-008)")
    parser.add_argument("--mode", choices=["check", "observe", "score", "detect", "propose",
                                            "generate", "update", "auto-doc", "reflect", "full"],
                        default="check", help="Evolution mode")
    parser.add_argument("--spec-id", default="SPEC-auto", help="Spec ID for auto-doc")
    parser.add_argument("--title", default="Evolution Engine", help="Title for auto-doc")
    parser.add_argument("--tier", type=int, default=2, help="Tier for auto-doc")
    parser.add_argument("--summary", default="", help="Summary for auto-doc")
    args = parser.parse_args()

    if args.mode == "full":
        metrics = run_observe()
        card = run_score(metrics)
        issues = run_detect(metrics)
        proposals = run_propose_phase(metrics, issues)
        run_generate(proposals)
        run_update(proposals)
        run_reflect(metrics, issues, proposals)
    elif args.mode == "check":
        card = load()
        print(f"[check] Current score: {card.get('overall', 'N/A')}/100")
    elif args.mode == "observe":
        run_observe()
    elif args.mode == "score":
        metrics = run_observe()
        run_score(metrics)
    elif args.mode == "detect":
        metrics = run_observe()
        run_detect(metrics)
    elif args.mode == "propose":
        metrics = run_observe()
        issues = run_detect(metrics)
        run_propose_phase(metrics, issues)
    elif args.mode == "generate":
        proposals_dir = REPO / "evolution" / "proposals"
        if proposals_dir.exists():
            for f in sorted(proposals_dir.glob("*.json")):
                p = json.loads(f.read_text())
                p["status"] = "accepted"
                path = gen_adr(p)
                if path:
                    print(f"  ADR: {path}")
    elif args.mode == "update":
        run_update([])
    elif args.mode == "auto-doc":
        run_docs(args.spec_id, args.title, args.tier, args.summary)
    elif args.mode == "reflect":
        metrics = run_observe()
        issues = run_detect(metrics)
        run_reflect(metrics, issues, [])

    print(f"[done] Evolution mode={args.mode}")


if __name__ == "__main__":
    main()
