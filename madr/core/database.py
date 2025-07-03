from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from .settings import settings

engine = create_async_engine(settings.DATABASE_URI.get_secret_value())


def get_async_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine)
