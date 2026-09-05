"""
Tests for database models and seed data.
"""
import pytest
import asyncio
from app.database.database import db_manager
from app.database import (
    Customer, Product, Order, OrderItem, Payment, Shipment, Refund,
    SupportTicket, Approval, OrderStatus, PaymentStatus, ShipmentStatus,
    TicketStatus, ApprovalStatus, ApprovalActionType,
)
from sqlalchemy import select, func


@pytest.mark.asyncio
async def test_database_initialization():
    """Test that database can be initialized."""
    await db_manager.initialize()
    assert db_manager.engine is not None
    assert db_manager.session_factory is not None
    await db_manager.close()


@pytest.mark.asyncio
async def test_seed_data():
    """Test that seed data creates expected records."""
    await db_manager.initialize()
    from app.database.seed import seed_database
    await seed_database()

    async with db_manager.session() as session:
        # Check customers
        result = await session.execute(select(func.count(Customer.id)))
        count = result.scalar()
        assert count >= 20, f"Expected >= 20 customers, got {count}"

        # Check products
        result = await session.execute(select(func.count(Product.id)))
        count = result.scalar()
        assert count >= 25, f"Expected >= 25 products, got {count}"

        # Check orders
        result = await session.execute(select(func.count(Order.id)))
        count = result.scalar()
        assert count >= 20, f"Expected >= 20 orders, got {count}"

        # Check CUS1001 orders
        result = await session.execute(
            select(func.count(Order.id)).where(Order.customer_id == "CUS1001")
        )
        count = result.scalar()
        assert count >= 5, f"Expected >= 5 orders for CUS1001, got {count}"

    await db_manager.close()


@pytest.mark.asyncio
async def test_model_relationships():
    """Test that model relationships work correctly."""
    await db_manager.initialize()
    from app.database.seed import seed_database
    await seed_database()

    async with db_manager.session() as session:
        result = await session.execute(
            select(Order).where(Order.id == "TK10001")
        )
        order = result.scalar_one_or_none()
        assert order is not None
        assert order.customer_id == "CUS1001"
        assert order.payment is not None
        assert order.shipment is not None
        assert len(order.items) > 0

    await db_manager.close()