from fastapi import APIRouter
from models import ContactRequest
from database import query_db
from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["contact"])

@router.post("/contact")
def submit_contact(req: ContactRequest):
    query_db(
        "INSERT INTO contacts (name, email, phone, service_interest, message, status) VALUES (:name, :email, :phone, :service, :message, 'new')",
        {"name": req.name, "email": req.email, "phone": "", "service": req.service, "message": req.message}
    )
    return {"ok": True}

@router.get("/admin/contacts")
def get_contacts():
    return query_db("SELECT * FROM contacts ORDER BY created_at DESC")
