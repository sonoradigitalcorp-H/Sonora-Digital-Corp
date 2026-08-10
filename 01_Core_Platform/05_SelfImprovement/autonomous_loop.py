"""Autonomous Loop — scheduled self-improvement.

Runs on a cron-like schedule (weekly by default). Each cycle:
  1. Mine failures from experience store
  2. Generate insights
  3. Audit all skills (tests + evals)
  4. Evolve prompts for underperforming skills
  5. Write report to reports/

CLI:
  python3 autonomous_loop.py run              # single cycle
  python3 autonomous_loop.py schedule         # cron mode (weekly)
  python3 autonomous_loop.py status           # show last run + stats
"""

import json
import time
import hashlib
import argparse
import schedule
from pathlib import Path
from datetime import datetime, timezone

from sdc_sdk import DB_PATH, SKILLS_DIR, call_llm, log_action, get_db
from experience_store import ExperienceStore
from failure_miner import FailureMiner
from skill_evolver import SkillEvolver

REPORTS_DIR = Path(__file__).resolve().parent / "reports"


def generate_report(
    store: ExperienceStore,
    miner: FailureMiner,
    evolver: SkillEvolver,
    cycle_id: str,
) -> dict:
    """Run one full improvement cycle and return the report."""
    started = time.time()
    log_action("auto_cycle_start", metadata={"cycle_id": cycle_id})

    # 1. Mine failures
    patterns = miner.mine_deterministic(limit=500)

    # 2. Generate insights
    insights = miner.generate_insights()

    # 3. Audit skills
    #   We use a stub executor that logs input/output
    def stub_executor(skill_name: str, prompt: str) -> str:
        return f"[eval] {skill_name}: output for '{prompt[:100]}'"

    audit_results = evolver.audit_and_evolve_all()

    # 4. Stats
    stats = store.get_stats()

    # 5. Recommendations from LLM
    report_prompt = f"""Genera un reporte de auto-mejora ejecutivo para Sonora Digital Corp.

ESTADÍSTICAS:
{json.dumps(stats, indent=2)}

PATRONES ENCONTRADOS: {len(patterns)}
INSIGHTS GENERADOS: {len(insights)}

AUDITORÍA DE SKILLS:
{json.dumps(audit_results, indent=2, default=str)}

Genera:
1. Resumen ejecutivo (3 líneas)
2. Top 3 insights priorizados
3. Skills que requieren atención humana
4. Recomendación de próximos pasos

Formato: JSON con keys: summary, top_insights, needs_human_review, next_steps"""

    try:
        recommendations = call_llm(
            prompt=report_prompt,
            system="Eres un analista de operaciones. Genera JSON válido.",
            max_tokens=1500,
            temperature=0.2,
        )
        rec_parsed = json.loads(recommendations.strip().strip("```"))
    except Exception:
        rec_parsed = {
            "summary": "Auto-mejora completada. Ver estadísticas para detalles.",
            "top_insights": [],
            "needs_human_review": [],
            "next_steps": ["Revisar logs de estabilidad"],
        }

    report = {
        "cycle_id": cycle_id,
        "started_at": datetime.fromtimestamp(started, tz=timezone.utc).isoformat(),
        "completed_at": datetime.fromtimestamp(time.time(), tz=timezone.utc).isoformat(),
        "duration_seconds": round(time.time() - started, 2),
        "stats": stats,
        "patterns_found": len(patterns),
        "insights_generated": len(insights),
        "skill_audit": audit_results,
        "summary": rec_parsed.get("summary", ""),
        "top_insights": rec_parsed.get("top_insights", []),
        "needs_human_review": rec_parsed.get("needs_human_review", []),
        "next_steps": rec_parsed.get("next_steps", []),
    }

    # Save report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"report_{cycle_id}.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    # Also save as latest
    (REPORTS_DIR / "latest.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )

    log_action("auto_cycle_complete", metadata={"cycle_id": cycle_id, "duration": report["duration_seconds"]})
    return report


def run_cycle() -> dict:
    """Run a single improvement cycle."""
    cycle_id = hashlib.sha1(f"{time.time()}".encode()).hexdigest()[:8]
    store = ExperienceStore()
    miner = FailureMiner(store=store)
    evolver = SkillEvolver(store=store)
    return generate_report(store, miner, evolver, cycle_id)


def run_schedule(at_time: str = "03:00"):
    """Run cycles on a daily schedule at specific time (default 3 AM)."""
    log_action("scheduler_started", metadata={"at_time": at_time})

    def job():
        try:
            report = run_cycle()
            print(f"[{datetime.now().isoformat()}] Cycle {report['cycle_id']} complete: "
                  f"{report['stats']['total_tasks']} tasks, "
                  f"{report['patterns_found']} patterns, "
                  f"{report['insights_generated']} insights")
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Cycle error: {e}")
            log_action("scheduler_error", metadata={"error": str(e)})

    # Run immediately on start if flag set
    import os
    if os.getenv("AUTO_RUN_IMMEDIATE", "false").lower() == "true":
        job()

    # Schedule daily at specified time
    schedule.every().day.at(at_time).do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)


def status() -> dict:
    """Show current system status."""
    store = ExperienceStore()
    stats = store.get_stats()

    # Latest report
    latest = REPORTS_DIR / "latest.json"
    last_report = json.loads(latest.read_text(encoding="utf-8")) if latest.exists() else {}

    # Pending insights
    pending = []
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, description, recommendation, impact_score FROM insights WHERE applied = 0 ORDER BY impact_score DESC LIMIT 10"
        ).fetchall()
        pending = [dict(r) for r in rows]

    # Registered skills
    skills = []
    if SKILLS_DIR.exists():
        skills = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir()]

    return {
        "stats": stats,
        "last_report": last_report.get("cycle_id"),
        "last_report_at": last_report.get("completed_at"),
        "pending_insights": pending,
        "registered_skills": skills,
        "db_path": str(DB_PATH),
    }


def main():
    parser = argparse.ArgumentParser(description="SDC Self-Improvement Engine")
    parser.add_argument("command", choices=["run", "schedule", "status"],
                        help="run: single cycle | schedule: daily at 3 AM | status: show stats")
    parser.add_argument("--at-time", type=str, default="03:00",
                        help="Schedule time HH:MM (default: 03:00)")
    parser.add_argument("--immediate", action="store_true",
                        help="Run once immediately on start")
    args = parser.parse_args()

    if args.command == "run":
        report = run_cycle()
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))

    elif args.command == "schedule":
        import os
        if args.immediate:
            os.environ["AUTO_RUN_IMMEDIATE"] = "true"
        print(f"Starting autonomous improvement loop (daily at {args.at_time})")
        print("Press Ctrl+C to stop.")
        try:
            run_schedule(at_time=args.at_time)
        except KeyboardInterrupt:
            print("\nScheduler stopped.")

    elif args.command == "status":
        st = status()
        print(json.dumps(st, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
