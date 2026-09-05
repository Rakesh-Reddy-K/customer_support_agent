"""
Customer service operations.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Customer


async def get_customer_by_id(session: AsyncSession, customer_id: str) -> dict | None:
    """Get customer by ID."""
    result = await session.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        return None
    return {
        "id": customer.id, "email": customer.email, "phone": customer.phone,
        "first_name": customer.first_name, "last_name": customer.last_name,
        "full_name": f"{customer.first_name} {customer.last_name}",
    }