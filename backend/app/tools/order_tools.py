"""
LangChain tools for order operations.
"""
import json
from langchain_core.tools import tool
from app.database.database import db_manager
from app.services import order_service


@tool
async def lookup_order(order_id: str) -> str:
    """Look up order details by order ID (e.g., TK10023). Use this when a customer asks about a specific order."""
    async with db_manager.session() as session:
        result = await order_service.get_order_by_id(session, order_id)
    if not result:
        return json.dumps({"error": f"Order {order_id} not found"})
    return json.dumps(result, default=str)


@tool
async def lookup_order_with_auth(order_id: str, customer_id: str) -> str:
    """Look up order details with customer authorization check. Only returns the order if it belongs to the customer."""
    async with db_manager.session() as session:
        result = await order_service.get_order_with_ownership(session, order_id, customer_id)
    if not result:
        return json.dumps({"error": "Order not found or you are not authorized to view this order"})
    return json.dumps(result, default=str)


@tool
async def list_customer_orders(customer_id: str) -> str:
    """List all orders for a customer. Use this to show customer's order history."""
    async with db_manager.session() as session:
        results = await order_service.get_orders_by_customer(session, customer_id)
    return json.dumps({"orders": results, "count": len(results)}, default=str)


@tool
async def track_shipment(order_id: str) -> str:
    """Track shipment status for an order. Returns tracking info, carrier, estimated delivery."""
    async with db_manager.session() as session:
        result = await order_service.get_order_by_id(session, order_id)
    if not result:
        return json.dumps({"error": f"Order {order_id} not found"})
    shipment = result.get("shipment")
    if not shipment:
        return json.dumps({"error": "No shipment information available"})
    return json.dumps(shipment, default=str)


@tool
async def check_refund_eligibility(order_id: str) -> str:
    """Check if an order is eligible for a refund. Returns eligibility status and reason."""
    async with db_manager.session() as session:
        result = await order_service.check_refund_eligibility(session, order_id)
    return json.dumps(result, default=str)