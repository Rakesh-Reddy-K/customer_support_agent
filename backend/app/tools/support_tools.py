"""
LangChain tools for support ticket operations.
"""
import json
from datetime import datetime
from langchain_core.tools import tool
from app.database.database import db_manager
from sqlalchemy import select
from app.database import SupportTicket, TicketStatus


@tool
async def create_support_ticket(customer_id: str, subject: str, description: str, order_id: str = "", priority: str = "medium") -> str:
    """Create a support ticket for the customer. Use when an issue needs to be tracked or escalated."""
    async with db_manager.session() as session:
        ticket_id = f"TCK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        ticket = SupportTicket(
            id=ticket_id, customer_id=customer_id,
            order_id=order_id if order_id else None,
            subject=subject, description=description,
            status=TicketStatus.OPEN, priority=priority,
            assigned_team="Level 1 Support",
        )
        session.add(ticket)
        await session.flush()
    return json.dumps({
        "success": True, "ticket_id": ticket_id,
        "message": f"Support ticket {ticket_id} created successfully",
    })


@tool
async def get_customer_tickets(customer_id: str) -> str:
    """Get all support tickets for a customer."""
    async with db_manager.session() as session:
        result = await session.execute(
            select(SupportTicket).where(SupportTicket.customer_id == customer_id)
            .order_by(SupportTicket.created_at.desc())
        )
        tickets = result.scalars().all()
    ticket_list = [{
        "id": t.id, "subject": t.subject, "status": t.status.value if t.status else None,
        "priority": t.priority, "created_at": t.created_at.isoformat() if t.created_at else None,
        "order_id": t.order_id,
    } for t in tickets]
    return json.dumps({"tickets": ticket_list, "count": len(ticket_list)}, default=str)