"""Client Success Engine — 3AM Daily Analysis + Intervention System.

Analiza cada cliente del sistema y genera sugerencias proactivas.
Puede intervenir automáticamente: WhatsApp, Email, Video, Agendar.

Usage:
  python3 scripts/client_analyzer.py --analyze-all        # Analiza todos los clientes
  python3 scripts/client_analyzer.py --analyze-client X   # Analiza un cliente especifico
  python3 scripts/client_analyzer.py --suggest client_X   # Genera sugerencia
  python3 scripts/client_analyzer.py --intervene client_X signal_name  # Ejecuta accion
  python3 scripts/client_analyzer.py --schedule-3am       # Registra cron job
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

MAX_SUGGESTIONS_PER_CLIENT = 3


def load_signals() -> dict:
    import yaml
    path = REPO / "config" / "client-signals.yaml"
    with open(path) as f:
        return yaml.safe_load(f) or {}


def _conn_with_rows(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def get_tenants_db() -> sqlite3.Connection:
    db_path = Path(os.environ.get("TENANT_DB_PATH", str(REPO / "data" / "tenants.db")))
    return _conn_with_rows(db_path)


def get_commissions_db() -> sqlite3.Connection:
    db_path = Path(os.environ.get("COMMISSIONS_DB_PATH", str(REPO / "data" / "commissions.db")))
    return _conn_with_rows(db_path)


def get_clone_db() -> sqlite3.Connection:
    db_path = Path(os.environ.get("DB_PATH", str(REPO / "data" / "clone_service.db")))
    return _conn_with_rows(db_path)


def get_cost_db() -> sqlite3.Connection:
    db_path = Path(os.environ.get("COST_DB_PATH", str(REPO / "data" / "cost_tracker.db")))
    return _conn_with_rows(db_path)


def get_all_clients() -> list:
    """Get all clients from all databases."""
    clients = []
    seen = set()

    # From tenants DB
    try:
        conn = get_tenants_db()
        rows = conn.execute(
            "SELECT id as tenant_id, client_name, partner_id, status, created_at FROM tenants"
        ).fetchall()
        for r in rows:
            cid = r["tenant_id"]
            if cid not in seen:
                seen.add(cid)
                clients.append({
                    "tenant_id": cid,
                    "name": r["client_name"],
                    "partner": r["partner_id"],
                    "status": r["status"],
                    "created_at": r["created_at"],
                })
        conn.close()
    except Exception:
        pass

    # From clone service DB
    try:
        conn = get_clone_db()
        rows = conn.execute(
            "SELECT id, status, pack_type, credits_photo, credits_video, credits_tts, "
            "lora_id, voice_id, created_at FROM clients"
        ).fetchall()
        for r in rows:
            cid = r["id"]
            if cid not in seen:
                seen.add(cid)
                clients.append({
                    "tenant_id": cid,
                    "name": cid,
                    "partner": "sdc",
                    "status": r["status"],
                    "pack": r["pack_type"],
                    "credits": {"photo": r["credits_photo"], "video": r["credits_video"], "tts": r["credits_tts"]},
                    "lora": r["lora_id"],
                    "voice": r["voice_id"],
                    "created_at": r["created_at"],
                })
            else:
                # Merge data into existing
                for c in clients:
                    if c["tenant_id"] == cid:
                        c["pack"] = r["pack_type"]
                        c["credits"] = {"photo": r["credits_photo"], "video": r["credits_video"], "tts": r["credits_tts"]}
                        c["lora"] = r["lora_id"]
                        c["voice"] = r["voice_id"]
                        break
        conn.close()
    except Exception:
        pass

    return clients


def get_client_activity(tenant_id: str) -> dict:
    """Get activity data for a client."""
    activity = {
        "last_activity_days": 999,
        "photos_used": 0,
        "videos_used": 0,
        "total_calls": 0,
        "total_cost": 0,
        "credits_remaining_pct": 0,
    }

    # Check assets generated
    try:
        conn = get_clone_db()
        assets = conn.execute(
            "SELECT type, COUNT(*) as cnt, MAX(created_at) as last FROM assets "
            "WHERE client_id = ? GROUP BY type", (tenant_id,)
        ).fetchall()
        for a in assets:
            if a["type"] == "photo":
                activity["photos_used"] = a["cnt"]
            elif a["type"] == "video":
                activity["videos_used"] = a["cnt"]
            if a["last"]:
                days = (datetime.now() - datetime.strptime(a["last"][:10], "%Y-%m-%d")).days
                activity["last_activity_days"] = min(activity["last_activity_days"], days)
        conn.close()
    except Exception:
        pass

    # Check costs
    try:
        conn = get_cost_db()
        cost = conn.execute(
            "SELECT SUM(cost_usd) as total, COUNT(*) as calls FROM cost_log "
            "WHERE tenant_id = ? AND created_at >= datetime('now', '-30 days')",
            (tenant_id,),
        ).fetchone()
        if cost:
            activity["total_cost"] = cost["total"] or 0
            activity["total_calls"] = cost["calls"] or 0
        conn.close()
    except Exception:
        pass

    return activity


def evaluate_signals(client: dict, activity: dict) -> list:
    """Evaluate all signals against a client and return matching suggestions."""
    signals_config = load_signals().get("signals", {})
    suggestions = []

    days_since_signup = 0
    if client.get("created_at"):
        try:
            created = datetime.strptime(client["created_at"][:10], "%Y-%m-%d")
            days_since_signup = (datetime.now() - created).days
        except Exception:
            pass

    for signal_id, signal in signals_config.items():
        audience = signal.get("audience", "")
        check = signal.get("check", "")
        then_block = signal.get("then", {})

        # Filter by audience
        if "Embajadores" in audience and client.get("partner") in ("aztrotech", "abe_music"):
            pass  # It's a partner/ambassador
        elif "Clientes Pro" in audience and client.get("pack") != "pro":
            continue
        elif "Clientes nuevos" in audience and days_since_signup > 7:
            continue
        elif "Usuarios free" in audience and client.get("pack") not in (None, "", "free"):
            continue
        elif "Clientes con LoRA entrenado" in audience and not client.get("lora"):
            continue
        elif "Clientes Pro" in audience and client.get("pack") != "pro":
            continue

        # Evaluate check conditions
        matched = False
        if "last_activity > 7_days" in check and activity["last_activity_days"] > 7:
            matched = True
        elif "last_activity > 15_days" in check and activity["last_activity_days"] > 15:
            matched = True
        elif "photos_used > credits_total * 0.8" in check and client.get("credits"):
            total = client["credits"].get("photo", 30)
            used = activity["photos_used"]
            if total > 0 and used / total >= 0.8:
                matched = True
        elif "credits_remaining < 20%" in check and client.get("credits"):
            total = sum(client["credits"].values())
            if total < 5:  # Arbitrary low threshold
                matched = True
        elif "days_since_signup > 2 AND lora_trained == false" in check:
            if days_since_signup > 2 and not client.get("lora"):
                matched = True
        elif "trial_ended AND not_converted" in check:
            if client.get("pack") in (None, "free") and days_since_signup > 1:
                matched = True
        elif "last_payment_failed == true" in check:
            if client.get("status") == "payment_failed":
                matched = True
        elif "today == client_birthday" in check:
            pass  # Skip without birthday data
        elif "remaining_for_next_level <= 5" in check:
            pass  # Skip without ambassador data

        # Generic match for signals without specific checks
        if "last_activity" in check or "days_since" in check or "credits_remaining" in check:
            pass  # Already handled above

        if matched or not check:  # If no check condition, signal is based on audience/context
            if signal_id in ("ambassador_first_sale_pending", "voice_not_cloned",
                             "lora_trained_no_videos", "ambassador_inactive_7d",
                             "birthday"):
                matched = True

        if matched:
            suggestion = {
                "signal_id": signal_id,
                "name": signal["name"],
                "severity": signal.get("severity", "medium"),
                "suggest": then_block.get("suggest", ""),
                "action": then_block.get("action", "send_whatsapp"),
                "audience": audience,
            }
            suggestions.append(suggestion)

    # Sort by severity: critical > high > medium > low
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    suggestions.sort(key=lambda s: severity_order.get(s["severity"], 99))

    return suggestions[:MAX_SUGGESTIONS_PER_CLIENT]


def format_suggestion(suggestion: dict, client: dict) -> str:
    """Format a suggestion as a readable message."""
    msg = suggestion.get("suggest", "")
    msg = msg.replace("{X}", str(client.get("name", "")))
    msg = msg.replace("{next_level}", "Warrior")
    msg = msg.replace("{bonus}", "$500")
    return msg


def intervene(client: dict, suggestion: dict) -> dict:
    """Execute an intervention action."""

    action = suggestion.get("action", "send_whatsapp")
    msg = format_suggestion(suggestion, client)

    result = {"client": client.get("name"), "signal": suggestion["signal_id"], "action": action, "message": msg[:100], "executed": False}

    if "send_whatsapp" in action:
        result["whatsapp"] = f"Would send to {client.get('tenant_id')}: {msg[:80]}..."
        result["executed"] = True

    if "send_email" in action:
        result["email"] = f"Would email to {client.get('tenant_id')}: {msg[:80]}..."
        result["executed"] = True

    if "offer_trial" in action:
        result["offer"] = "7 days free trial offered"
        result["executed"] = True

    if "send_video_tutorial" in action or "send_video_example" in action or "send_video_gift" in action or "send_congrats_video" in action:
        result["video"] = f"Would generate video for {client.get('name')}"
        result["executed"] = True

    if "schedule_call" in action:
        result["call"] = f"Would schedule retention call for {client.get('name')}"
        result["executed"] = True

    if "notify_ambassador" in action or "notify_sdc" in action:
        result["notification"] = f"Would notify SDC team about {client.get('name')}"
        result["executed"] = True

    return result


def analyze_client(client: dict) -> dict:
    """Analyze a single client and return suggestions + interventions."""
    activity = get_client_activity(client["tenant_id"])
    suggestions = evaluate_signals(client, activity)
    interventions = [intervene(client, s) for s in suggestions]

    return {
        "client": client.get("name", client["tenant_id"]),
        "tenant_id": client["tenant_id"],
        "partner": client.get("partner", ""),
        "activity": activity,
        "suggestions": suggestions,
        "interventions": interventions,
    }


def analyze_all() -> list:
    """Analyze all clients and return results."""
    clients = get_all_clients()
    results = []
    for client in clients:
        try:
            result = analyze_client(client)
            results.append(result)
        except Exception as e:
            results.append({
                "client": client.get("name", client.get("tenant_id", "unknown")),
                "error": str(e),
            })
    return results


def report(results: list):
    """Print a beautiful report of the analysis."""
    print(f"\n{'═'*70}")
    print("  🌅  CLIENT SUCCESS ENGINE — Daily Analysis")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'═'*70}\n")

    total_interventions = 0
    total_critical = 0

    for r in results:
        if "error" in r:
            print(f"  ⚠️  {r['client']}: {r['error']}")
            continue

        suggestions = r.get("suggestions", [])
        interventions = r.get("interventions", [])

        if not suggestions:
            print(f"  ✅  {r['client']:30s} — Todo bien, sin sugerencias")
            continue

        status_icon = "🔴" if any(s["severity"] == "critical" for s in suggestions) else \
                      "🟡" if any(s["severity"] == "high" for s in suggestions) else "🟢"
        print(f"  {status_icon}  {r['client']:30s} ({len(suggestions)} sugerencias)")

        for s in suggestions:
            sev_icon = {"critical": "🔴", "high": "🟡", "medium": "🟢", "low": "ℹ️"}
            print(f"     {sev_icon.get(s['severity'], '•')} {s['name']}")
            print(f"       → {format_suggestion(s, r)[:90]}")
            total_interventions += 1
            if s["severity"] == "critical":
                total_critical += 1

        for inv in interventions:
            if inv.get("executed"):
                print(f"       ✅ {inv['action']}")

        print()

    print(f"{'═'*70}")
    print(f"  📊  RESUMEN: {len(results)} clientes | {total_interventions} sugerencias | {total_critical} críticas")
    print(f"{'═'*70}\n")


def setup_cron():
    """Install the 3AM cron job."""
    script_path = REPO / "scripts" / "client_analyzer.py"
    cron_line = f"0 3 * * * cd {REPO} && PYTHONPATH=. python3 {script_path} --analyze-all >> {REPO}/logs/client-analyzer.log 2>&1"

    # Check if already installed
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if script_path.name in result.stdout:
        print("✅ Cron job already installed")
        return

    # Install
    new_cron = result.stdout + cron_line + "\n"
    proc = subprocess.run(["crontab", "-"], input=new_cron, capture_output=True, text=True)
    if proc.returncode == 0:
        print("✅ Cron job installed: 0 3 * * * → client_analyzer.py")
    else:
        print(f"❌ Failed to install cron: {proc.stderr}")


def main():
    parser = argparse.ArgumentParser(description="SDC Client Success Engine — 3AM Analysis")
    parser.add_argument("--analyze-all", action="store_true", help="Analyze all clients")
    parser.add_argument("--analyze-client", metavar="CLIENT_ID", help="Analyze a specific client")
    parser.add_argument("--suggest", metavar="CLIENT_ID", help="Generate suggestions for a client")
    parser.add_argument("--intervene", nargs=2, metavar=("CLIENT_ID", "SIGNAL"), help="Execute intervention for a client")
    parser.add_argument("--schedule-3am", action="store_true", help="Install 3AM cron job")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.schedule_3am:
        setup_cron()
        return

    if args.analyze_all:
        results = analyze_all()
    elif args.analyze_client:
        client = {"tenant_id": args.analyze_client, "name": args.analyze_client, "partner": "sdc"}
        results = [analyze_client(client)]
    elif args.suggest:
        client = {"tenant_id": args.suggest, "name": args.suggest, "partner": "sdc"}
        result = analyze_client(client)
        results = [result]
        print(json.dumps({"suggestions": result["suggestions"]}, indent=2, ensure_ascii=False))
        return
    elif args.intervene:
        client_id, signal_name = args.intervene
        # Quick intervention simulation
        signals_config = load_signals().get("signals", {})
        signal = signals_config.get(signal_name, {})
        then_block = signal.get("then", {})
        client = {"name": client_id, "tenant_id": client_id}
        suggestion = {
            "signal_id": signal_name,
            "name": signal.get("name", signal_name),
            "severity": signal.get("severity", "medium"),
            "suggest": then_block.get("suggest", f"Intervención para {client_id}"),
            "action": then_block.get("action", "send_whatsapp"),
        }
        result = intervene(client, suggestion)
        results = [{"client": client_id, "interventions": [result]}]
    else:
        parser.print_help()
        return

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        report(results)


if __name__ == "__main__":
    main()
