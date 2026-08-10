#!/usr/bin/env python3
"""onboarding_tools.py — Tools de onboarding para invocar desde OpenClaw agent cesar.

Uso desde el agente:
  python3 /path/to/onboarding_tools.py score <tenant> <json_data>
  python3 /path/to/onboarding_tools.py intelligence <tenant> <json_data>
  python3 /path/to/onboarding_tools.py assets <tenant> <servicio>
  python3 /path/to/onboarding_tools.py feedback <tenant> <event_type> <json_data>
"""

import json
import sys
from pathlib import Path
from dataclasses import asdict

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))

from lead_scoring import calculate_lead_score
from lead_intelligence import generate_lead_intelligence
from asset_generation import list_prompts, generate_asset_prompt
from feedback_loop import FeedbackLoop, FeedbackEvent


def cmd_score(tenant: str, data_json: str):
    data = json.loads(data_json)
    scoring = calculate_lead_score(data)
    return {
        "score": scoring.score,
        "classification": scoring.classification,
        "factores": scoring.factores,
        "next_action": scoring.next_action
    }


def cmd_intelligence(tenant: str, data_json: str):
    data = json.loads(data_json)
    lead = data.get("lead", {})
    scoring_result = data.get("scoring_result")
    intel = generate_lead_intelligence(tenant, lead, scoring_result)
    return intel.model_dump()


def cmd_assets(tenant: str, asset_type: str):
    prompts = list_prompts(asset_type)
    return {"prompts": [asdict(p) for p in prompts]}


def cmd_feedback(tenant: str, event_type: str, data_json: str):
    data = json.loads(data_json)
    db_path = str(Path.home() / ".openclaw" / "workspace" / f"leads_{tenant}.db")
    loop = FeedbackLoop(db_path)
    event = FeedbackEvent(
        lead_id=data["lead_id"],
        tenant=tenant,
        tipo=event_type,
        valor=data["valor"],
        metadata=data.get("metadata", {})
    )
    return loop.process_event(event)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: onboarding_tools.py <cmd> <tenant> [args...]")
        print("Cmds: score, intelligence, assets, feedback")
        sys.exit(1)

    cmd = sys.argv[1]
    tenant = sys.argv[2]

    try:
        if cmd == "score":
            result = cmd_score(tenant, sys.argv[3])
        elif cmd == "intelligence":
            result = cmd_intelligence(tenant, sys.argv[3])
        elif cmd == "assets":
            result = cmd_assets(tenant, sys.argv[3])
        elif cmd == "feedback":
            result = cmd_feedback(tenant, sys.argv[3], sys.argv[4])
        else:
            print(f"Unknown cmd: {cmd}")
            sys.exit(1)

        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
