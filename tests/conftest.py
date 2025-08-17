import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql import insert
from madr.app import app
from fastapi.testclient import TestClient

from madr.core.database import get_async_session
from madr.models import Base, User
from tests.factories import UserCreateFactory

engine = create_async_engine("sqlite+aiosqlite:///:memory:")

sessionmaker = async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with sessionmaker() as session:
        yield session


@pytest.fixture
def client(session: AsyncSession):
    def session_override():
        return session

    app.dependency_overrides[get_async_session] = session_override
    client = TestClient(app)
    return client


@pytest_asyncio.fixture
async def existing_user(session: AsyncSession) -> User:
    result = (
        await session.execute(
            insert(User)
            .values(UserCreateFactory.create(password="password").model_dump())
            .returning(User)
        )
    ).scalar_one()
    await session.commit()

    return result


@pytest_asyncio.fixture
async def another_user(session: AsyncSession) -> User:
    result = (
        await session.execute(
            insert(User)
            .values(UserCreateFactory.create(password="password").model_dump())
            .returning(User)
        )
    ).scalar_one()
    await session.commit()

    return result
