"""
Tests for API endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "TechKart" in data["service"]


@pytest.mark.asyncio
async def test_get_customer():
    from app.database.database import db_manager
    from app.database.seed import seed_database
    await db_manager.initialize()
    await seed_database()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/customers/CUS1001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "CUS1001"

    await db_manager.close()


@pytest.mark.asyncio
async def test_get_customer_not_found():
    from app.database.database import db_manager
    await db_manager.initialize()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/customers/INVALID")
    assert response.status_code == 404

    await db_manager.close()


@pytest.mark.asyncio
async def test_get_order():
    from app.database.database import db_manager
    from app.database.seed import seed_database
    await db_manager.initialize()
    await seed_database()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/orders/TK10001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "TK10001"
    assert "items" in data
    assert "payment" in data

    await db_manager.close()


@pytest.mark.asyncio
async def test_get_pending_approvals():
    from app.database.database import db_manager
    from app.database.seed import seed_database
    await db_manager.initialize()
    await seed_database()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/approvals/pending")
    assert response.status_code == 200
    data = response.json()
    assert "approvals" in data
    assert data["count"] >= 1

    await db_manager.close()