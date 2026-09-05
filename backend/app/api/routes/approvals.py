"""
Approvals API endpoints for HITL workflow.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database.database import db_manager
from app.services import approval_service


router = APIRouter(prefix="/approvals", tags=["approvals"])


class DecisionRequest(BaseModel):
    decision: str  # "approve", "reject", "edit"
    decided_by: str = "SUPPORT_AGENT"
    edited_amount: float | None = None
    edited_reason: str | None = None
    notes: str | None = None


@router.get("/pending")
async def get_pending():
    """Get all pending approvals."""
    async with db_manager.session() as session:
        results = await approval_service.get_pending_approvals(session)
    return {"approvals": results, "count": len(results)}


@router.get("/{thread_id}")
async def get_approval(thread_id: str):
    """Get approval by thread ID."""
    async with db_manager.session() as session:
        result = await approval_service.get_approval_by_thread(session, thread_id)
    if not result:
        raise HTTPException(status_code=404, detail="Approval not found")
    return result


@router.post("/{thread_id}/decide")
async def decide(thread_id: str, request: DecisionRequest):
    """Decide on a pending approval (approve, reject, or edit)."""
    async with db_manager.session() as session:
        result = await approval_service.decide_approval(
            session, thread_id, request.decision, request.decided_by,
            edited_amount=request.edited_amount,
            edited_reason=request.edited_reason,
            notes=request.notes,
        )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Decision failed"))
    return result