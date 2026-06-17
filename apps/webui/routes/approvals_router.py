from fastapi import APIRouter

router = APIRouter()


@router.get("/api/approvals")
async def list_approvals():
    from src.core.unified_bridge import UnifiedSystem

    system = UnifiedSystem()
    return {
        "pending": system.control.list_pending(),
        "count": system.control.pending_count(),
    }


@router.post("/api/approvals/{ticket}/approve")
async def approve_action(ticket: str):
    from src.core.unified_bridge import UnifiedSystem

    system = UnifiedSystem()
    if system.control.approve(ticket):
        return {"status": "approved", "ticket": ticket}
    return {"status": "error", "message": "Not found or already processed"}


@router.post("/api/approvals/{ticket}/reject")
async def reject_action(ticket: str):
    from src.core.unified_bridge import UnifiedSystem

    system = UnifiedSystem()
    if system.control.reject(ticket):
        return {"status": "rejected", "ticket": ticket}
    return {"status": "error", "message": "Not found or already processed"}
