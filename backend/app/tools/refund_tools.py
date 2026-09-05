"""
LangChain tools for refund operations.
"""
import json
from langchain_core.tools import tool
from app.database.database import db_manager
from app.services import refund_service, order_service


@tool
async def process_refund(order_id: str, amount: float, reason: str) -> str:
    """Process a refund for an order. This action requires human approval and should NOT be called directly. Instead, create a refund proposal."""
    return json.dumps({
        "error": "Refund processing requires human approval. Please create a refund proposal instead.",
        "action_required": "propose_refund",
    })


@tool
async def execute_approved_refund(order_id: str, amount: float, reason: str, approved_by: str = "SYSTEM") -> str:
    """Execute an already-approved refund. Only call this after human approval has been granted."""
    async with db_manager.session() as session:
        result = await refund_service.process_refund(
            session, order_id, amount, reason, approved_by
        )
    return json.dumps(result, default=str)


@tool
async def request_refund_proposal(order_id: str, amount: float = 0.0, reason: str = "Customer requested refund") -> str:
    """Create a refund proposal that requires human approval. Use this when a customer wants a refund.
    You can pass amount=0 if you don't know the exact order amount — the tool will auto-detect it from the order."""
    async with db_manager.session() as session:
        eligibility = await order_service.check_refund_eligibility(session, order_id)
    
    if not eligibility.get("eligible"):
        return json.dumps({
            "action": "refund_rejected",
            "reason": eligibility.get("reason", "Not eligible"),
        })
    
    # Use the refundable_amount from eligibility when LLM didn't provide amount
    effective_amount = amount if amount > 0 else eligibility.get("refundable_amount", 0)
    effective_amount = min(effective_amount, eligibility.get("refundable_amount", effective_amount))

    return json.dumps({
        "action": "refund_proposed",
        "order_id": order_id,
        "amount": effective_amount,
        "reason": reason,
        "requires_approval": True,
        "ai_reasoning_summary": f"Customer requested refund of ₹{effective_amount} for order {order_id}. Reason: {reason}. {eligibility.get('reason', '')}",
    })