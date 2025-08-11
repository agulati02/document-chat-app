from contextlib import asynccontextmanager
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from fastapi import FastAPI
from config.settings import POSTGRESQL_CONNECTION_STRING
from models.orm import Base

# Global engine and session factory
async_engine: AsyncEngine = None
AsyncSessionLocal = None

def initialize_database():
    """Initialize database engine and session factory."""
    global async_engine, AsyncSessionLocal
    
    logging.info("Creating PostgreSQL async engine.")
    async_engine = create_async_engine(
        POSTGRESQL_CONNECTION_STRING, 
        echo=True,
        pool_size=10,
        max_overflow=20
    )
    
    logging.info("Creating session factory.")
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine, 
        class_=AsyncSession,
        expire_on_commit=False
    )

async def get_database_session():
    """
    Dependency to provide a database session.
    This should only be used in FastAPI route dependencies.
    """
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager."""
    logging.info("Starting up application...")
    
    # Initialize database
    initialize_database()
    
    try:
        logging.info("Creating database tables...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("Database tables created successfully")
        logging.info("Application startup complete")
    except Exception as e:
        logging.error(f"Error during startup: {e}")
        raise e
    
    yield

    logging.info("Shutting down application...")
    try:
        if async_engine:
            await async_engine.dispose()
        logging.info("Database connections closed")
    except Exception as e:
        logging.error(f"Error during shutdown: {e}")
    
    logging.info("Application shutdown complete")