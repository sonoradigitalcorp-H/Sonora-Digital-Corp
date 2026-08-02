import json
import os
import time

SCORES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "scores")
os.makedirs(SCORES_PATH, exist_ok=True)


def score_interaction(transcript, response, had_objection, objection_handled, duration_sec):
    score = 50
    
    if had_objection and objection_handled:
        score += 20
    elif had_objection and not objection_handled:
        score -= 15

    if duration_sec > 120:
        score += 10
    elif duration_sec < 15:
        score -= 5

    response_len = len(response)
    if 30 < response_len < 400:
        score += 10
    elif response_len > 600:
        score -= 10
    elif response_len < 10:
        score -= 10

    resolution_keywords = ["gracias", "entendí", "claro", "perfecto", "ok", "sí", "si",
                          "de acuerdo", "suena bien", "adelante", "excelente"]
    if any(kw in response.lower() for kw in resolution_keywords):
        score += 10

    return max(0, min(100, score))


def save_score(tenant_id, call_id, score, ab_variant, lead_type):
    record = {
        "tenant_id": tenant_id,
        "call_id": call_id,
        "score": score,
        "ab_variant": ab_variant,
        "lead_type": lead_type,
        "timestamp": time.time(),
    }
    path = os.path.join(SCORES_PATH, f"{call_id}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
    return record


def get_ab_stats():
    stats = {"A": {"count": 0, "total_score": 0}, "B": {"count": 0, "total_score": 0}, "C": {"count": 0, "total_score": 0}}
    if os.path.exists(SCORES_PATH):
        for fname in os.listdir(SCORES_PATH):
            if fname.endswith(".json"):
                with open(os.path.join(SCORES_PATH, fname)) as f:
                    record = json.load(f)
                variant = record.get("ab_variant", "A")
                if variant in stats:
                    stats[variant]["count"] += 1
                    stats[variant]["total_score"] += record.get("score", 0)
    for v in stats:
        if stats[v]["count"] > 0:
            stats[v]["avg"] = round(stats[v]["total_score"] / stats[v]["count"], 1)
        else:
            stats[v]["avg"] = 0
    return stats
