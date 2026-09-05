"""
Pytest configuration for TechKart backend tests.
"""
import asyncio
import pytest


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    import os
    os.environ["OPENAI_API_KEY"] = "test-key-not-real"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_techkart.db"
    os.environ["CHROMA_PERSIST_DIR"] = "./test_chroma_db"
    os.environ["ENVIRONMENT"] = "testing"