import json
import os
import random
import yaml

AB_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "ab-config.yaml")

DEFAULT_CONFIG = {
    "variants": {
        "A": {"weight": 34, "description": "Control: prompt original"},
        "B": {"weight": 33, "description": "Test: enfoque consultivo"},
        "C": {"weight": 33, "description": "Test: enfoque directo"},
    },
    "auto_optimize": True,
    "min_samples_for_decision": 30,
    "improvement_threshold": 5,
}


def load_config():
    if os.path.exists(AB_CONFIG_PATH):
        with open(AB_CONFIG_PATH) as f:
            return yaml.safe_load(f) or DEFAULT_CONFIG
    return DEFAULT_CONFIG


def save_config(config):
    with open(AB_CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


def assign_variant(tenant_id, lead_type):
    config = load_config()
    variants = config["variants"]
    total_weight = sum(v["weight"] for v in variants.values())
    roll = random.randint(1, total_weight)
    cumulative = 0
    for name, v in variants.items():
        cumulative += v["weight"]
        if roll <= cumulative:
            return name
    return "A"


def register_result(variant, score):
    config = load_config()
    variants = config["variants"]
    if variant not in variants:
        return
    v = variants[variant]
    v.setdefault("results", [])
    v["results"].append(score)
    if len(v["results"]) > 100:
        v["results"] = v["results"][-100:]
    v["avg_score"] = round(sum(v["results"]) / len(v["results"]), 1)
    v["count"] = len(v["results"])
    save_config(config)
    return check_optimization(config)


def check_optimization(config):
    if not config.get("auto_optimize"):
        return None
    min_samples = config.get("min_samples_for_decision", 30)
    threshold = config.get("improvement_threshold", 5)
    variants = config["variants"]
    
    valid = {k: v for k, v in variants.items() if v.get("count", 0) >= min_samples}
    if len(valid) < 2:
        return None
    
    best = max(valid.items(), key=lambda x: x[1].get("avg_score", 0))
    worst = min(valid.items(), key=lambda x: x[1].get("avg_score", 0))
    
    if best[1]["avg_score"] - worst[1]["avg_score"] >= threshold:
        return {
            "winner": best[0],
            "loser": worst[0],
            "winner_score": best[1]["avg_score"],
            "loser_score": worst[1]["avg_score"],
            "diff": best[1]["avg_score"] - worst[1]["avg_score"],
            "samples": {k: v["count"] for k, v in valid.items()},
        }
    return None
