from collections.abc import AsyncGenerator
from typing import Any
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from .settings import settings

engine = create_async_engine(settings.DATABASE_URI.get_secret_value())

session_maker = async_sessionmaker(engine)


async def get_async_session() -> AsyncGenerator[AsyncSession, Any]:
    async with session_maker() as session:
        yield session
