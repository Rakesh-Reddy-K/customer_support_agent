"""
Database connection and session management.
"""
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import settings
from app.database.models import Base


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.database_url
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize the database engine and session factory."""
        self.engine = create_async_engine(
            self.database_url,
            echo=settings.environment == "development",
            future=True,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        """Close the database engine."""
        if self.engine:
            await self.engine.dispose()
    
    @asynccontextmanager
    async def session(self) -> AsyncSession:
        """Get a database session."""
        if not self.session_factory:
            await self.initialize()
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def get_session(self) -> AsyncSession:
        """Get a database session (for dependency injection)."""
        if not self.session_factory:
            await self.initialize()
        return self.session_factory()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_session() -> AsyncSession:
    """FastAPI dependency for database session."""
    async with db_manager.session() as session:
        yield session