"""
Orders API endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database.database import db_manager
from app.services import order_service


router = APIRouter(prefix="/orders", tags=["orders"])


class OrderQuery(BaseModel):
    customer_id: str | None = None


@router.get("/{order_id}")
async def get_order(order_id: str):
    """Get order details by ID."""
    async with db_manager.session() as session:
        result = await order_service.get_order_by_id(session, order_id)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


@router.get("/{order_id}/status")
async def get_order_status(order_id: str):
    """Get order status summary."""
    async with db_manager.session() as session:
        result = await order_service.get_order_by_id(session, order_id)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "order_id": result["id"],
        "status": result["status"],
        "shipment_status": result["shipment"]["status"] if result.get("shipment") else None,
        "payment_status": result["payment"]["status"] if result.get("payment") else None,
    }


@router.get("/customer/{customer_id}")
async def get_customer_orders(customer_id: str):
    """Get all orders for a customer."""
    async with db_manager.session() as session:
        results = await order_service.get_orders_by_customer(session, customer_id)
    return {"orders": results, "count": len(results)}