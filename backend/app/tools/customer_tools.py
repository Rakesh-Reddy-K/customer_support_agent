"""
LangChain tools for customer operations.
"""
import json
from langchain_core.tools import tool
from app.database.database import db_manager
from app.services import customer_service


@tool
async def get_customer_info(customer_id: str) -> str:
    """Get customer information by customer ID (e.g., CUS1001). Use to verify customer identity."""
    async with db_manager.session() as session:
        result = await customer_service.get_customer_by_id(session, customer_id)
    if not result:
        return json.dumps({"error": f"Customer {customer_id} not found"})
    return json.dumps(result, default=str)