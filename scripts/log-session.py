#!/usr/bin/env python3
"""CLI for quick session logging.

Usage:
  python3 scripts/log-session.py --type comando --command "/generar-nicho" --success true --duration 4200
  python3 scripts/log-session.py --type error --command "deploy" --success false --error "Connection refused"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evolution.session_store import SessionStore


def main():
    parser = argparse.ArgumentParser(description="Log a session interaction to the Session Store")
    parser.add_argument("--type", choices=["comando", "respuesta", "evento", "error"], required=True)
    parser.add_argument("--command", default="")
    parser.add_argument("--success", type=str, choices=["true", "false"], default="true")
    parser.add_argument("--duration", type=int, default=0, help="Duration in milliseconds")
    parser.add_argument("--tokens", type=int, default=0, help="Tokens used")
    parser.add_argument("--user", default="system")
    parser.add_argument("--outcome", default="")
    parser.add_argument("--improvement", default="")
    parser.add_argument("--client-impact", type=str, choices=["true", "false"], default="false")
    parser.add_argument("--skills", default="", help="Comma-separated skill names")
    parser.add_argument("--files", default="", help="Comma-separated file paths")
    parser.add_argument("--error", default="", help="Error message (sets outcome and success=false)")
    args = parser.parse_args()

    session = {
        "type": args.type,
        "command": args.command,
        "success": args.success == "true",
        "duration_ms": args.duration,
        "tokens_used": args.tokens,
        "user": args.user,
        "outcome": args.outcome,
        "improvement": args.improvement,
        "client_impact": args.client_impact == "true",
        "skills_used": [s.strip() for s in args.skills.split(",") if s.strip()],
        "files_changed": [f.strip() for f in args.files.split(",") if f.strip()],
    }

    if args.error:
        session["success"] = False
        session["outcome"] = args.error
        session["type"] = "error"

    store = SessionStore()
    session_id = store.save(session)
    print(session_id)


if __name__ == "__main__":
    main()
