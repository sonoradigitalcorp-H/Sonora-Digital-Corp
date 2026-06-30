from fastapi import APIRouter, HTTPException, Query
from src.core.sales_pipeline import pipeline, PipelineStage

router = APIRouter()


@router.post("/api/sales/leads")
async def capture_lead(data: dict):
    lead = pipeline.capture_lead(
        name=data.get("name", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        source=data.get("source", "web_form"),
        niche=data.get("niche", "general"),
        plan_interest=data.get("plan_interest", ""),
        notes=data.get("notes", ""),
    )
    return {"lead_id": lead.id, "score": lead.score, "stage": lead.stage}


@router.get("/api/sales/leads/{lead_id}")
async def get_lead(lead_id: str):
    lead = pipeline.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead.__dict__


@router.get("/api/sales/leads")
async def list_leads(stage: str = Query(None)):
    leads = pipeline.list_leads(stage)
    return {"leads": [l.__dict__ for l in leads]}


@router.post("/api/sales/leads/{lead_id}/qualify")
async def qualify_lead(lead_id: str):
    lead = pipeline.qualify_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"lead_id": lead.id, "score": lead.score, "stage": lead.stage}


@router.get("/api/sales/leads/{lead_id}/proposal")
async def generate_proposal(lead_id: str):
    proposal = pipeline.generate_proposal(lead_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"proposal": proposal}


@router.post("/api/sales/leads/{lead_id}/accept")
async def accept_proposal(lead_id: str):
    ok = pipeline.accept_proposal(lead_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "accepted"}


@router.post("/api/sales/leads/{lead_id}/won")
async def close_won(lead_id: str, data: dict = None):
    deal = pipeline.close_won(
        lead_id,
        payment_ref=(data or {}).get("payment_ref", ""),
        amount=(data or {}).get("amount", 0.0),
    )
    if not deal:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"deal_id": deal.id, "status": "won"}


@router.post("/api/sales/leads/{lead_id}/lost")
async def close_lost(lead_id: str, data: dict = None):
    deal = pipeline.close_lost(
        lead_id,
        reason=(data or {}).get("reason", ""),
    )
    if not deal:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"deal_id": deal.id, "status": "lost"}


@router.get("/api/sales/dashboard")
async def sales_dashboard():
    return pipeline.get_dashboard()
