from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings

#Workflow:
#Request -> FastAPI calls get_db()
#->creates new session
#->yields session to the endpoint
#->endpoint uses session to interact with the database
#->auto commit if no error
#->auto rollback if error
#->auto close session

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL in debug mode
    poolclass=NullPool,   # For SQLite compatibility
)


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered
        # This must be done before create_all()
        from app.models.account import Account
        from app.models.payment import Payment
        from app.models.payment_log import PaymentLog
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("[OK] Database tables created successfully")


async def drop_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("[OK] Database tables dropped")