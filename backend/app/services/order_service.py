"""
Order service - business logic for order operations.
"""
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Order, OrderItem, Payment, Shipment, Refund, OrderStatus, PaymentStatus


async def get_order_by_id(session: AsyncSession, order_id: str) -> dict | None:
    """Get order details by order ID."""
    result = await session.execute(
        select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.payment),
            selectinload(Order.shipment),
            selectinload(Order.refunds),
        ).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    return _order_to_dict(order) if order else None


async def get_orders_by_customer(session: AsyncSession, customer_id: str) -> list[dict]:
    """Get all orders for a customer."""
    result = await session.execute(
        select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.payment),
            selectinload(Order.shipment),
            selectinload(Order.refunds),
        ).where(Order.customer_id == customer_id).order_by(Order.created_at.desc())
    )
    return [_order_to_dict(o) for o in result.scalars().all()]


async def get_order_with_ownership(session: AsyncSession, order_id: str, customer_id: str) -> dict | None:
    """Get order only if it belongs to the customer (authorization check)."""
    result = await session.execute(
        select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.payment),
            selectinload(Order.shipment),
            selectinload(Order.refunds),
        ).where(Order.id == order_id, Order.customer_id == customer_id)
    )
    order = result.scalar_one_or_none()
    return _order_to_dict(order) if order else None


async def check_refund_eligibility(session: AsyncSession, order_id: str) -> dict:
    """Check if an order is eligible for refund based on business rules."""
    result = await session.execute(
        select(Order).options(
            selectinload(Order.payment),
            selectinload(Order.refunds),
            selectinload(Order.items).selectinload(OrderItem.product),
        ).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        return {"eligible": False, "reason": "Order not found"}
    if order.status in [OrderStatus.CANCELLED, OrderStatus.REFUNDED]:
        return {"eligible": False, "reason": "Order already cancelled or refunded"}
    completed = [r for r in order.refunds if r.status == PaymentStatus.COMPLETED]
    if completed:
        return {"eligible": False, "reason": "Refund already processed"}
    pending = [r for r in order.refunds if r.status == PaymentStatus.PENDING]
    if pending:
        return {"eligible": False, "reason": "Refund request already pending"}
    if not order.payment or order.payment.status != PaymentStatus.COMPLETED:
        return {"eligible": False, "reason": "No completed payment found"}
    if order.delivered_at:
        days = (datetime.utcnow() - order.delivered_at).days
        cats = {i.product.category for i in order.items if i.product}
        window = 15 if ("smartphone" in cats or "laptop" in cats) else (7 if "accessories" in cats else 30)
        if days > window:
            return {"eligible": False, "reason": f"Outside {window}-day refund window"}
    remaining = order.payment.amount - sum(r.amount for r in completed)
    if remaining <= 0:
        return {"eligible": False, "reason": "Full amount already refunded"}
    return {"eligible": True, "reason": "Eligible for refund", "order_id": order.id,
            "total_amount": order.total_amount, "refundable_amount": remaining}


def _order_to_dict(order: Order) -> dict:
    """Convert Order ORM to dict."""
    items = [{"product_id": i.product_id, "product_name": i.product.name if i.product else "Unknown",
              "category": i.product.category if i.product else "unknown",
              "brand": i.product.brand if i.product else "Unknown",
              "quantity": i.quantity, "unit_price": i.unit_price, "total_price": i.total_price}
             for i in (order.items or [])]
    payment = None
    if order.payment:
        p = order.payment
        payment = {"id": p.id, "amount": p.amount, "status": p.status.value if p.status else None,
                   "payment_method": p.payment_method, "paid_at": p.paid_at.isoformat() if p.paid_at else None}
    shipment = None
    if order.shipment:
        s = order.shipment
        shipment = {"id": s.id, "tracking_number": s.tracking_number, "carrier": s.carrier,
                    "status": s.status.value if s.status else None,
                    "shipped_at": s.shipped_at.isoformat() if s.shipped_at else None,
                    "estimated_delivery": s.estimated_delivery.isoformat() if s.estimated_delivery else None,
                    "delivered_at": s.delivered_at.isoformat() if s.delivered_at else None,
                    "tracking_url": s.tracking_url}
    refunds = [{"id": r.id, "amount": r.amount, "reason": r.reason,
                "status": r.status.value if r.status else None,
                "processed_at": r.processed_at.isoformat() if r.processed_at else None}
               for r in (order.refunds or [])]
    return {"id": order.id, "customer_id": order.customer_id,
            "status": order.status.value if order.status else None,
            "total_amount": order.total_amount, "shipping_address": order.shipping_address,
            "items": items, "payment": payment, "shipment": shipment, "refunds": refunds,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "shipped_at": order.shipped_at.isoformat() if order.shipped_at else None,
            "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None}