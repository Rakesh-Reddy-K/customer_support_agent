"""
Refund service operations.
"""
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import (
    Refund, Order, Payment, PaymentStatus, OrderStatus
)


async def process_refund(
    session: AsyncSession, order_id: str, amount: float,
    reason: str, approved_by: str, payment_id: str | None = None,
) -> dict:
    """Process a refund for an order. Deterministic backend logic."""
    result = await session.execute(
        select(Order).options(
            select(Payment).where(Payment.order_id == order_id),
        ).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        return {"success": False, "error": "Order not found"}

    # Find payment
    pay_result = await session.execute(
        select(Payment).where(Payment.order_id == order_id)
    )
    payment = pay_result.scalar_one_or_none()
    if not payment:
        return {"success": False, "error": "No payment found"}
    if payment.status != PaymentStatus.COMPLETED:
        return {"success": False, "error": "Payment not completed"}

    # Validate amount
    existing_refunds = await session.execute(
        select(Refund).where(
            Refund.order_id == order_id,
            Refund.status == PaymentStatus.COMPLETED,
        )
    )
    already_refunded = sum(r.amount for r in existing_refunds.scalars().all())
    refundable = payment.amount - already_refunded
    if amount > refundable:
        return {"success": False, "error": f"Amount {amount} exceeds refundable {refundable}"}
    if amount <= 0:
        return {"success": False, "error": "Invalid refund amount"}

    # Create refund record
    refund_id = f"REF{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    refund = Refund(
        id=refund_id, order_id=order_id, payment_id=payment.id,
        amount=amount, reason=reason, status=PaymentStatus.COMPLETED,
        approved_by=approved_by, approved_at=datetime.utcnow(),
        processed_at=datetime.utcnow(),
    )
    session.add(refund)

    # Update order status
    total_after = already_refunded + amount
    if total_after >= payment.amount:
        order.status = OrderStatus.REFUNDED
        payment.status = PaymentStatus.REFUNDED
    else:
        payment.status = PaymentStatus.PARTIALLY_REFUNDED

    await session.flush()
    return {
        "success": True, "refund_id": refund_id,
        "amount": amount, "status": "processed",
    }