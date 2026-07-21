"""
Mystic Shield API — FastAPI backend.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "mcp/servers"))
from shield_mcp import shield_diagnose, REPORTS_DIR
sys.path.insert(0, str(Path(__file__).parent))
from request_handler import save_request, notify_admin, list_requests

app = FastAPI(title="Mystic Shield API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LANDING_DIR = Path(__file__).parent.parent.parent.parent / "frontends/mystic-shield"
if LANDING_DIR.exists():
    app.mount("/", StaticFiles(directory=str(LANDING_DIR), html=True), name="landing")

class DiagnoseRequest(BaseModel):
    target: str
    company_name: str
    ceo_phone: Optional[str] = ""
    ceo_email: Optional[str] = ""
    company_email: Optional[str] = ""

class LeadRequest(BaseModel):
    email: str
    company: str
    phone: str = ""

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "mystic-shield",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.post("/api/request-diagnosis")
async def request_diagnosis(req: LeadRequest):
    lead = save_request(email=req.email, company=req.company, phone=req.phone)
    notify_admin(lead)
    return {"success": True, "message": "Recibido. Te contactamos en 24h.", "id": lead["id"]}

@app.post("/api/diagnose", response_model=dict)
async def diagnose(req: DiagnoseRequest):
    result = await shield_diagnose(
        target=req.target,
        company_name=req.company_name,
        ceo_phone=req.ceo_phone,
        ceo_email=req.ceo_email,
        company_email=req.company_email,
    )
    data = json.loads(result)
    if not data.get("success"):
        raise HTTPException(status_code=400, detail=data.get("error", "Diagnosis failed"))
    return data

@app.get("/api/report/{diagnosis_id}")
async def get_report(diagnosis_id: str):
    meta_path = REPORTS_DIR / f"{diagnosis_id}.json"
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return json.loads(meta_path.read_text())

@app.get("/api/reports")
async def list_all_reports(limit: int = 10):
    reports = sorted(REPORTS_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)
    result = []
    for p in reports[:limit]:
        data = json.loads(p.read_text())
        result.append({
            "id": data.get("id"),
            "company_name": data.get("company_name"),
            "timestamp": data.get("timestamp"),
            "total_hosts": data.get("scan", {}).get("total_hosts", 0),
            "active_hosts": data.get("scan", {}).get("hosts_with_open_ports", 0),
        })
    return {"reports": result, "total": len(result)}

@app.get("/api/leads")
async def list_all_leads(limit: int = 20):
    return {"leads": list_requests(limit)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8931))
    uvicorn.run(app, host="127.0.0.1", port=port)
