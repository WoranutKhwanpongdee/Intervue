import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import get_settings

logger = logging.getLogger("intervue.db")
settings = get_settings()

Base = declarative_base()

# Choose database URL
db_url = settings.DATABASE_URL
if "sqlite" in db_url:
    # Ensure correct connect args for SQLite async
    engine = create_async_engine(db_url, echo=settings.DEBUG)
else:
    try:
        engine = create_async_engine(db_url, echo=settings.DEBUG)
    except Exception as e:
        logger.warning(f"Error configuring database with {db_url}: {e}. Falling back to SQLite.")
        engine = create_async_engine(settings.SQLITE_FALLBACK_URL, echo=settings.DEBUG)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    global engine, AsyncSessionLocal
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized.")
    except Exception as e:
        logger.warning(f"PostgreSQL initialization failed ({e}). Switching to SQLite fallback...")
        engine = create_async_engine(settings.SQLITE_FALLBACK_URL, echo=settings.DEBUG)
        AsyncSessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized with SQLite fallback.")
