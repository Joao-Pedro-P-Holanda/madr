from typing import Callable
from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from madr.models import Book
from madr.schema import BookSchema
from tests.conftest import does_not_raise
from tests.factories import BookCreateFactory


def test_get_book_without_token_succeeds(existing_book: Book, client: TestClient):
    response = client.get(f"/livro/{existing_book.id}")
    assert response.status_code == 200
    with does_not_raise(ValidationError):
        BookSchema.model_validate(response.json())


def test_get_book_with_invalid_id_fails(existing_book: Book, client: TestClient):
    response = client.get(f"/livro/{existing_book.id + 1}")
    assert response.status_code == 404


def _get_random_substring(s: str):
    """
    Gera uma substring contígua aleatória a partir de uma string base
    """
    faker = Faker()
    positions = list(range(len(s)))
    substr_start = faker.random_element(positions)
    substr_end = faker.random_element(positions[positions.index(substr_start) + 1 :])
    return s[substr_start:substr_end]


# TODO: com certeza existe uma forma melhor de parametrizar os filtros a serem testados
filters = [
    # string vazia não vai fazer nenhum filtro
    (("nome", "name"), lambda x: "", lambda x: len(x) == 1),
    (("nome", "name"), lambda x: _get_random_substring(x), lambda x: len(x) > 0),
    (("nome", "name"), lambda x: x, lambda x: len(x) == 1),
    (
        ("ano-inicial", "year"),
        lambda x: x - 1,
        lambda x: len(x) == 1,
    ),
    (
        ("ano-inicial", "year"),
        lambda x: x + 1,
        lambda x: len(x) == 0,
    ),
    (
        ("ano-final", "year"),
        lambda x: x + 1,
        lambda x: len(x) == 1,
    ),
    (
        ("ano-final", "year"),
        lambda x: x - 1,
        lambda x: len(x) == 0,
    ),
]


@pytest.mark.parametrize("field_pair,query_value, expected_result", filters)
def test_list_books_can_apply_filter(
    field_pair: tuple[str, str],
    query_value: Callable,
    expected_result: Callable,
    client: TestClient,
    existing_book: Book,
):
    response = client.get(
        "/livro",
        params={field_pair[0]: query_value(getattr(existing_book, field_pair[1]))},
    )

    assert response.status_code == 200
    assert expected_result(response.json())


def test_list_books_returns_empty_without_books(client: TestClient):
    response = client.get(f"/livro")

    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_list_books_paginates_exceeding_results(
    session: AsyncSession, client: TestClient, page_size=20
):
    to_create = BookCreateFactory.create_batch(page_size + 1)
    instances = [Book(**create.model_dump()) for create in to_create]
    session.add_all(instances)
    await session.commit()

    first_page_response = client.get("/livro")
    assert len(first_page_response.json()) == page_size

    second_page_response = client.get("/livro", params={"deslocamento": page_size})
    assert len(second_page_response.json()) == 1


def test_authenticated_user_can_create_book(token: str, client: TestClient):
    response = client.post(
        "/livro",
        headers={"Authorization": f"Bearer {token}"},
        json=BookCreateFactory().model_dump(),
    )

    assert response.status_code == 201
    with does_not_raise(ValidationError):
        BookSchema.model_validate(response.json())


def test_authenticated_user_can_not_create_book_with_used_name(
    token: str, existing_book: Book, client: TestClient
):
    response = client.post(
        "/livro",
        headers={"Authorization": f"Bearer {token}"},
        json=BookCreateFactory(name=existing_book.name).model_dump(),
    )

    assert response.status_code == 409


def test_unauthenticated_user_can_not_create_book(client: TestClient):
    response = client.post(
        "/livro",
        json=BookCreateFactory().model_dump(),
    )

    assert response.status_code == 401


def test_authenticated_user_can_update_existing_book(
    token: str, existing_book: Book, client: TestClient
):
    response = client.patch(
        f"/livro/{existing_book.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=BookCreateFactory().model_dump(),
    )

    assert response.status_code == 200


def test_authenticated_user_can_not_update_to_existing_name(
    token: str, existing_book: Book, another_book: Book, client: TestClient
):
    response = client.patch(
        f"/livro/{existing_book.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=BookCreateFactory(name=another_book.name).model_dump(),
    )

    assert response.status_code == 409


def test_authenticated_user_can_not_update_unexisting_book(
    token: str, existing_book: Book, client: TestClient
):
    response = client.patch(
        f"/livro/-1",
        headers={"Authorization": f"Bearer {token}"},
        json=BookCreateFactory().model_dump(),
    )

    assert response.status_code == 404


def test_unauthenticated_user_can_not_update_existing_book(
    existing_book: Book, client: TestClient
):
    response = client.patch(
        f"/livro/{existing_book.id}",
        json=BookCreateFactory().model_dump(),
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_authenticated_user_can_delete_existing_book(
    token: str, existing_book: Book, session: AsyncSession, client: TestClient
):
    delete_response = client.delete(
        f"/livro/{existing_book.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert delete_response.status_code == 200

    assert (await session.get(Book, existing_book.id)) is None


def test_authenticated_user_can_not_delete_unexisting_book(
    token: str, client: TestClient
):
    delete_response = client.delete(
        f"/livro/1", headers={"Authorization": f"Bearer {token}"}
    )

    assert delete_response.status_code == 404


@pytest.mark.asyncio
async def test_unauthenticated_user_can_not_delete_existing_book(
    existing_book: Book, session: AsyncSession, client: TestClient
):
    delete_response = client.delete(f"/livro/{existing_book.id}")

    assert delete_response.status_code == 401

    assert (await session.get(Book, existing_book.id)) is not None
