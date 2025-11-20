from contextlib import contextmanager
from faker import Faker
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql import insert
from madr.app import app
from fastapi.testclient import TestClient

from madr.core.database import get_async_session
from madr.core.orm.mapping import init_mappings, mapping_registry, remove_mappings
from madr.models import Author, Book, User
from tests.factories import AuthorCreateFactory, BookCreateFactory, UserCreateFactory

engine = create_async_engine("sqlite+aiosqlite:///:memory:")

sessionmaker = async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def session():
    async with engine.begin() as conn:
        await conn.run_sync(mapping_registry.metadata.drop_all)
        await conn.run_sync(mapping_registry.metadata.create_all)

    async with sessionmaker() as session:
        init_mappings()
        yield session
        remove_mappings()


@pytest.fixture
def client(session: AsyncSession):
    def session_override():
        return session

    app.dependency_overrides[get_async_session] = session_override
    # mapeamento imperativo é controlado na fixture session, por isso
    # client não está em um bloco with que faria o lifespan executar
    client = TestClient(app)
    return client


# https://stackoverflow.com/questions/20274987/how-to-use-pytest-to-check-that-error-is-not-raised
@contextmanager
def does_not_raise(e: type[Exception]):
    try:
        yield
    except e:
        pytest.fail(f"Raised exception {e}")


def get_random_substring(s: str):
    """
    Gera uma substring contígua aleatória a partir de uma string base
    """
    faker = Faker()
    positions = list(range(len(s)))
    substr_start = faker.random_element(positions[:])
    if substr_start < len(s) - 1:
        substr_end = faker.random_element(
            positions[positions.index(substr_start) + 1 :]
        )
        return s[substr_start:substr_end]
    else:
        return s[substr_start:]


@pytest_asyncio.fixture
async def existing_user(client, session: AsyncSession) -> User:
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
async def another_user(client, session: AsyncSession) -> User:
    result = (
        await session.execute(
            insert(User)
            .values(UserCreateFactory.create(password="password").model_dump())
            .returning(User)
        )
    ).scalar_one()
    await session.commit()

    return result


@pytest.fixture
def token(existing_user: User, client: TestClient) -> str:
    token_response = client.post(
        "/token", data={"username": existing_user.email, "password": "password"}
    )
    return token_response.json()["access_token"]


@pytest_asyncio.fixture
async def existing_book(session: AsyncSession) -> Book:
    book = Book(**BookCreateFactory.create().model_dump(exclude={"author_ids"}))
    session.add(book)
    await session.commit()

    return book


@pytest_asyncio.fixture
async def another_book(session: AsyncSession) -> Book:
    book = Book(**BookCreateFactory.create().model_dump(exclude={"author_ids"}))
    session.add(book)
    await session.commit()

    return book


@pytest_asyncio.fixture
async def existing_author(session: AsyncSession) -> Author:
    author = Author(**AuthorCreateFactory.create().model_dump())
    session.add(author)
    await session.commit()

    return author


@pytest_asyncio.fixture
async def another_author(session: AsyncSession) -> Author:
    author = Author(**AuthorCreateFactory.create().model_dump())
    session.add(author)
    await session.commit()

    return author
