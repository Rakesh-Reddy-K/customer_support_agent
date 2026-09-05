"""
TechKart AI Customer Support Agent - FastAPI Application.
"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import settings
from app.database.database import db_manager
from app.middleware.observability import ObservabilityMiddleware
from app.api.routes import chat, orders, approvals, customers
from app.utils.logging import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    setup_logging()
    logger.info("TechKart AI Support Agent starting up...")

    # Initialize database
    await db_manager.initialize()
    logger.info("Database initialized")

    # Initialize RAG vectorstore
    try:
        from app.rag.vectorstore import get_vectorstore
        get_vectorstore()
        logger.info("RAG vectorstore initialized")
    except Exception as e:
        logger.warning(f"RAG vectorstore init failed (non-fatal): {e}")

    logger.info("Application ready")
    yield

    # Shutdown
    await db_manager.close()
    logger.info("Application shut down")


app = FastAPI(
    title="TechKart AI Customer Support Agent",
    description="AI-powered customer support agent with LangGraph, RAG, and HITL approvals",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Observability
app.add_middleware(ObservabilityMiddleware)

# Routes
app.include_router(chat.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(approvals.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "techkart-ai-support"}


@app.get("/")
async def root():
    return {
        "service": "TechKart AI Customer Support Agent",
        "version": "1.0.0",
        "docs": "/docs",
    }