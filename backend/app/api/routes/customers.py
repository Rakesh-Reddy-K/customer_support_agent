"""
Customers API endpoints.
"""
from fastapi import APIRouter, HTTPException
from app.database.database import db_manager
from app.services import customer_service


router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/{customer_id}")
async def get_customer(customer_id: str):
    """Get customer information."""
    async with db_manager.session() as session:
        result = await customer_service.get_customer_by_id(session, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result