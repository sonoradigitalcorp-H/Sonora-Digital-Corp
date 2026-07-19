"""
Sonora Client API — client learning & insights.

Exposes client learning data from the memory system:
  - Per-client profiles, interactions, patterns, recommendations
  - Aggregated niche insights
  - Cross-client patterns

Usage:
  python3 -m products.client_api.main
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from evolution.client_learner import ClientLearner
from memory.client_store import ClientStore

app = FastAPI(
    title="Sonora Client API",
    version="1.0.0",
    docs_url="/clients/docs",
    redoc_url="/clients/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = ClientStore()
learner = ClientLearner(store=store)


def _emit_event(event_type: str, payload: dict) -> None:
    events_file = REPO / "state" / "events" / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    with open(events_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


@app.get("/clients/health")
def health():
    return {
        "status": "ok",
        "clients_dir": str(store.base_dir),
        "total_clients": len(store.all_clients()),
    }


@app.get("/clients/stats")
def stats():
    return store.stats()


@app.get("/clients")
def list_clients(niche: str = "", active_only: bool = False):
    all_ids = store.all_clients()
    result = []
    for cid in all_ids:
        profile = store.get_profile(cid)
        if not profile:
            continue
        if niche and profile.get("niche") != niche:
            continue
        if active_only and not profile.get("active", True):
            continue
        result.append(profile)
    return {"clients": result, "total": len(result)}


@app.get("/clients/{client_id}")
def get_client(client_id: str):
    profile = store.get_profile(client_id)
    if not profile:
        raise HTTPException(404, f"Client {client_id} not found")
    interactions = store.get_interactions(client_id, limit=20)
    analysis = learner.analyze_client(client_id)
    return {
        "profile": profile,
        "recent_interactions": interactions,
        "analysis": analysis,
    }


@app.post("/clients/{client_id}/interaction")
def record_interaction(client_id: str, interaction: dict):
    if not store.get_profile(client_id):
        raise HTTPException(404, f"Client {client_id} not found")
    entry = store.save_interaction(client_id, interaction)
    _emit_event("client:interaction", {
        "client_id": client_id,
        "type": interaction.get("type", "message"),
        "service": interaction.get("service", ""),
    })
    return {"ok": True, "interaction": entry}


@app.put("/clients/{client_id}")
def update_client(client_id: str, updates: dict):
    if not store.get_profile(client_id):
        raise HTTPException(404, f"Client {client_id} not found")
    updated = store.update_profile(client_id, updates)
    _emit_event("client:updated", {"client_id": client_id, "updates": updates})
    return {"ok": True, "profile": updated}


@app.get("/clients/{client_id}/patterns")
def client_patterns(client_id: str):
    if not store.get_profile(client_id):
        raise HTTPException(404, f"Client {client_id} not found")
    patterns = store.get_patterns(client_id)
    analysis = learner.analyze_client(client_id)
    return {"client_id": client_id, "patterns": patterns, "analysis": analysis}


@app.get("/clients/{client_id}/recommendations")
def client_recommendations(client_id: str):
    if not store.get_profile(client_id):
        raise HTTPException(404, f"Client {client_id} not found")
    recommendations = store.get_recommendations(client_id)
    auto_recommendation = learner.get_recommendation(client_id)
    return {
        "client_id": client_id,
        "recommendations": recommendations,
        "auto_recommendation": auto_recommendation,
    }


@app.get("/niches/{niche}/insights")
def niche_insights(niche: str):
    analysis = learner.analyze_niche(niche)
    if analysis.get("client_count", 0) == 0:
        raise HTTPException(404, f"No clients found in niche '{niche}'")
    return analysis


@app.get("/insights")
def all_insights():
    return {"insights": learner.get_niche_insights()}


@app.get("/report")
def learning_report():
    report = learner.analyze_all()
    return report


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("CLIENT_API_PORT", "6500"))
    uvicorn.run("products.client_api.main:app", host="0.0.0.0", port=port, reload=False)
