import json
import logging
import os
import httpx
import yaml

logger = logging.getLogger(__name__)

EVOLUTION_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "evolution")
os.makedirs(EVOLUTION_PATH, exist_ok=True)

PATTERNS_FILE = os.path.join(EVOLUTION_PATH, "patterns.json")
PROPOSALS_FILE = os.path.join(EVOLUTION_PATH, "proposals.json")
AB_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "ab-config.yaml")


def detect_patterns(ab_stats, all_scores):
    patterns = []
    
    variants = {k: v for k, v in ab_stats.items() if v.get("count", 0) > 0}
    if len(variants) >= 2:
        max_var = max(variants.items(), key=lambda x: x[1].get("avg", 0))
        min_var = min(variants.items(), key=lambda x: x[1].get("avg", 0))
        diff = max_var[1]["avg"] - min_var[1]["avg"]
        if diff > 5:
            patterns.append({
                "type": "AB_TEST_WINNER",
                "detail": f"Variante {max_var[0]} (avg {max_var[1]['avg']}) supera a {min_var[0]} (avg {min_var[1]['avg']})",
                "confidence": min(diff / 10, 0.9),
                "action": f"Migrar todos los tenants a variante {max_var[0]}",
            })

    if len(all_scores) > 5:
        recent = all_scores[-5:]
        avg = sum(s["score"] for s in recent) / len(recent)
        if avg < 50:
            patterns.append({
                "type": "LOW_SCORE_TREND",
                "detail": f"Promedio de últimos 5 scores: {avg:.1f}. Posible degradación.",
                "confidence": 0.5,
                "action": "Revisar prompts y pipelines",
            })
        elif avg > 80:
            patterns.append({
                "type": "HIGH_SCORE_TREND",
                "detail": f"Promedio de últimos 5 scores: {avg:.1f}. Sistema funcionando bien.",
                "confidence": 0.8,
                "action": "Mantener configuración actual",
            })

    save_json(PATTERNS_FILE, patterns)
    return patterns


def apply_proposal(proposal):
    if proposal["type"] == "SWITCH_AB_VARIANT":
        winner = proposal["target"]
        config = yaml.safe_load(open(AB_CONFIG_PATH)) if os.path.exists(AB_CONFIG_PATH) else {}
        if "variants" in config:
            for v in config["variants"]:
                config["variants"][v]["weight"] = 0
            config["variants"][winner]["weight"] = 100
        with open(AB_CONFIG_PATH, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        logger.info(f"Evolution: migrado 100% del tráfico a variante {winner}")
        return True

    proposals = load_json(PROPOSALS_FILE, [])
    proposals.append({
        "type": proposal["type"],
        "detail": proposal.get("detail", ""),
        "score": proposal.get("score", 60),
        "applied": True,
        "timestamp": __import__("time").time(),
    })
    save_json(PROPOSALS_FILE, proposals)
    return True


def evaluate_and_apply(ab_stats, all_scores):
    patterns = detect_patterns(ab_stats, all_scores)
    applied = []
    for p in patterns:
        if p["confidence"] >= 0.7 and p.get("action"):
            if "variante" in p["action"].lower():
                import re
                match = re.search(r"variante\s+([A-Z])", p["action"])
                if match:
                    applied.append(apply_proposal({
                        "type": "SWITCH_AB_VARIANT",
                        "target": match.group(1),
                        "detail": p["detail"],
                        "score": int(p["confidence"] * 100),
                    }))
            else:
                applied.append(apply_proposal(p))
    return {"patterns": len(patterns), "applied": sum(applied)}


def load_json(path, default=None):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
