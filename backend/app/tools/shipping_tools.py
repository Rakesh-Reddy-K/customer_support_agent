"""
LangChain tools for shipping operations.
"""
import json
from langchain_core.tools import tool
from app.database.database import db_manager
from app.services import order_service


@tool
async def get_shipping_status(order_id: str) -> str:
    """Get the shipping/tracking status for an order. Returns carrier, tracking number, and estimated delivery."""
    async with db_manager.session() as session:
        result = await order_service.get_order_by_id(session, order_id)
    if not result:
        return json.dumps({"error": f"Order {order_id} not found"})
    shipment = result.get("shipment")
    if not shipment:
        return json.dumps({"status": "not_shipped", "message": "Order has not been shipped yet"})
    return json.dumps({
        "order_id": order_id,
        "tracking_number": shipment.get("tracking_number"),
        "carrier": shipment.get("carrier"),
        "status": shipment.get("status"),
        "shipped_at": shipment.get("shipped_at"),
        "estimated_delivery": shipment.get("estimated_delivery"),
        "delivered_at": shipment.get("delivered_at"),
        "tracking_url": shipment.get("tracking_url"),
    }, default=str)