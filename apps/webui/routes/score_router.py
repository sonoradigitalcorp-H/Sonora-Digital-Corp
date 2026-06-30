from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

BASE_DIR = Path(__file__).parent.parent.parent
SCORE_LOG = BASE_DIR / "state" / "logs" / "enterprise-score.log"
EVENTS_FILE = BASE_DIR / "state" / "logs" / "events.jsonl"


@router.get("/api/enterprise-score")
async def get_enterprise_score():
    score = _calc_score()
    history = _read_score_history()
    return {
        "score": score["total"],
        "metrics": score["metrics"],
        "history": history[-30:],
    }


@router.get("/api/enterprise-score/history")
async def get_score_history():
    return {"history": _read_score_history()[-100:]}


def _calc_score() -> dict:
    import json

    events = []
    if EVENTS_FILE.exists():
        with open(EVENTS_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

    finops_calls = [e for e in events if e.get("event") == "ai_call"]

    def count(etype):
        return len([e for e in events if e.get("event") == etype])

    revenue_score = min(10, count("revenue_recorded")) if count("revenue_recorded") else 1
    scalability_score = min(10, count("deal_won") + 3)
    reusability_score = min(10, count("skill_execution") // 5)
    automation_score = min(10, round(count("skill_execution") / max(1, len(events)) * 10)) if events else 1
    knowledge_score = min(10, count("knowledge_stored"))
    reliability_score = 7
    founder_score = min(10, count("service_recovered"))
    simplicity_score = max(0, 10 - len(set(e.get("event", "") for e in events)) // 10)
    customer_score = min(10, count("customer_onboarded")) if count("customer_onboarded") else 1
    total_cost = sum(c.get("cost", 0) for c in finops_calls)
    total_calls = len(finops_calls)
    cost_per_call = total_cost / max(1, total_calls)
    finops_score = max(0, 10 - round(cost_per_call / 0.001)) if total_calls > 0 else 1

    metrics = {
        "Revenue Impact": revenue_score,
        "Scalability": scalability_score,
        "Reusability": reusability_score,
        "Automation Impact": automation_score,
        "Knowledge Impact": knowledge_score,
        "Reliability": reliability_score,
        "Founder Independence": founder_score,
        "Operational Simplicity": simplicity_score,
        "Customer Value": customer_score,
        "FinOps Efficiency": finops_score,
    }
    total = sum(metrics.values())
    return {"total": total, "metrics": metrics}


def _read_score_history() -> list:
    history = []
    if SCORE_LOG.exists():
        with open(SCORE_LOG) as f:
            for line in f:
                line = line.strip()
                if "Enterprise Score:" in line:
                    try:
                        ts = line[1:20]
                        score = int(line.split(":")[-1].strip().split("/")[0])
                        history.append({"timestamp": ts, "score": score})
                    except (ValueError, IndexError):
                        pass
    return history
