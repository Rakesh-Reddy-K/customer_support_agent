"""
Approval service for human-in-the-loop workflow.
"""
import json
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Approval, ApprovalStatus


async def get_pending_approvals(session: AsyncSession) -> list[dict]:
    """Get all pending approvals."""
    result = await session.execute(
        select(Approval).where(Approval.status == ApprovalStatus.PENDING)
        .order_by(Approval.created_at.desc())
    )
    return [_approval_to_dict(a) for a in result.scalars().all()]


async def get_approval_by_thread(session: AsyncSession, thread_id: str) -> dict | None:
    """Get approval by thread ID."""
    result = await session.execute(
        select(Approval).where(Approval.thread_id == thread_id)
        .order_by(Approval.created_at.desc())
    )
    a = result.first()
    return _approval_to_dict(a[0]) if a else None


async def create_approval(session: AsyncSession, data: dict) -> dict:
    """Create a new approval request."""
    approval = Approval(
        id=f"APR{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        thread_id=data["thread_id"],
        customer_id=data["customer_id"],
        order_id=data.get("order_id"),
        action_type=data["action_type"],
        status=ApprovalStatus.PENDING,
        requested_amount=data.get("requested_amount"),
        requested_reason=data.get("requested_reason"),
        requested_data=json.dumps(data.get("requested_data", {})),
        ai_reasoning_summary=data.get("ai_reasoning_summary"),
    )
    session.add(approval)
    await session.flush()
    return _approval_to_dict(approval)


async def decide_approval(
    session: AsyncSession, thread_id: str,
    decision: str, decided_by: str,
    edited_amount: float | None = None,
    edited_reason: str | None = None,
    notes: str | None = None,
) -> dict:
    """Approve, reject, or edit an approval."""
    result = await session.execute(
        select(Approval).where(
            Approval.thread_id == thread_id,
            Approval.status == ApprovalStatus.PENDING,
        )
    )
    approval = result.scalar_one_or_none()
    if not approval:
        return {"success": False, "error": "No pending approval found"}

    now = datetime.utcnow()
    approval.decision = decision
    approval.decided_by = decided_by
    approval.decided_at = now
    approval.decision_notes = notes

    if decision == "approve":
        approval.status = ApprovalStatus.APPROVED
    elif decision == "reject":
        approval.status = ApprovalStatus.REJECTED
    elif decision == "edit":
        approval.status = ApprovalStatus.EDITED
        if edited_amount is not None:
            approval.edited_amount = edited_amount
        if edited_reason is not None:
            approval.edited_reason = edited_reason
    else:
        return {"success": False, "error": "Invalid decision"}

    await session.flush()
    return {"success": True, "status": approval.status.value}


async def mark_executed(session: AsyncSession, thread_id: str, result_data: str) -> None:
    """Mark an approval as executed."""
    res = await session.execute(
        select(Approval).where(Approval.thread_id == thread_id)
        .order_by(Approval.created_at.desc())
    )
    a = res.scalar_one_or_none()
    if a:
        a.status = ApprovalStatus.EXECUTED
        a.executed_at = datetime.utcnow()
        a.execution_result = result_data
        await session.flush()


def _approval_to_dict(a: Approval) -> dict:
    return {
        "id": a.id, "thread_id": a.thread_id,
        "customer_id": a.customer_id, "order_id": a.order_id,
        "action_type": a.action_type.value if a.action_type else None,
        "status": a.status.value if a.status else None,
        "requested_amount": a.requested_amount,
        "requested_reason": a.requested_reason,
        "requested_data": json.loads(a.requested_data) if a.requested_data else None,
        "decision": a.decision,
        "edited_amount": a.edited_amount,
        "edited_reason": a.edited_reason,
        "decided_by": a.decided_by,
        "decided_at": a.decided_at.isoformat() if a.decided_at else None,
        "decision_notes": a.decision_notes,
        "executed_at": a.executed_at.isoformat() if a.executed_at else None,
        "execution_result": a.execution_result,
        "ai_reasoning_summary": a.ai_reasoning_summary,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }