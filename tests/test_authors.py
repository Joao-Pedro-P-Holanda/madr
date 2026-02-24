from faker import Faker
from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from madr.models import Author
from madr.schema import AuthorSchema
from tests.conftest import does_not_raise, get_random_substring
from tests.factories import AuthorCreateFactory

base_url = "/romancista"


def test_get_author_without_token_succeeds(existing_author: Author, client: TestClient):
    response = client.get(f"{base_url}/{existing_author.id}")

    assert response.status_code == 200
    with does_not_raise(ValidationError):
        AuthorSchema.model_validate(response.json())


def test_get_author_with_invalid_id_fails(existing_author: Author, client: TestClient):
    response = client.get(f"{base_url}/{existing_author.id + 1}")

    assert response.status_code == 404


filters = [
    (lambda x: "", lambda response: len(response) == 1),
    (lambda x: x, lambda response: len(response) == 1),
    (lambda x: get_random_substring(x), lambda response: len(response) == 1),
    (lambda x: Faker().text(), lambda response: len(response) == 0),
]


@pytest.mark.parametrize("used_filter,expected_result", filters)
def test_list_authors_can_filter_name_partially(
    used_filter, expected_result, existing_author: Author, client: TestClient
):
    response = client.get(
        f"{base_url}", params={"nome": used_filter(existing_author.name)}
    )

    assert response.status_code == 200
    assert expected_result(response.json())


@pytest.mark.asyncio
async def test_list_authors_paginates_exceeding_results(
    session: AsyncSession, client: TestClient, page_size=20
):
    to_create = AuthorCreateFactory.create_batch(page_size + 1)
    instances = [Author(**create.model_dump()) for create in to_create]
    session.add_all(instances)
    await session.commit()

    first_page_response = client.get(f"{base_url}")
    assert len(first_page_response.json()) == page_size

    second_page_response = client.get(f"{base_url}", params={"deslocamento": page_size})
    assert len(second_page_response.json()) == 1


def test_list_authors_returns_empty_without_authors(client: TestClient):
    response = client.get(f"{base_url}")

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_authenticated_user_can_insert_author(token: str, client: TestClient):
    response = client.post(
        f"{base_url}",
        headers={"Authorization": f"Bearer {token}"},
        json=AuthorCreateFactory.create().model_dump(mode="json"),
    )

    assert response.status_code == 201
    with does_not_raise(ValidationError):
        AuthorSchema.model_validate(response.json())


def test_authenticated_user_can_not_insert_author_with_existing_name(
    token: str, existing_author: Author, client: TestClient
):
    response = client.post(
        f"{base_url}",
        headers={"Authorization": f"Bearer {token}"},
        json=AuthorCreateFactory.create(name=existing_author.name).model_dump(
            mode="json"
        ),
    )

    assert response.status_code == 409


def test_authenticated_user_can_update_existing_author(
    token: str, existing_author: Author, client: TestClient
):
    response = client.patch(
        f"{base_url}/{existing_author.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=AuthorCreateFactory.create().model_dump(mode="json"),
    )

    assert response.status_code == 200


def test_authenticated_user_can_not_update_unexisting_author(
    token: str, client: TestClient
):
    response = client.patch(
        f"{base_url}/1",
        headers={"Authorization": f"Bearer {token}"},
        json=AuthorCreateFactory.create().model_dump(mode="json"),
    )

    assert response.status_code == 404


def test_authenticated_user_can_not_update_author_to_existing_name(
    token: str, existing_author: Author, another_author: Author, client: TestClient
):
    response = client.patch(
        f"{base_url}/{existing_author.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=AuthorCreateFactory.create(name=another_author.name).model_dump(
            mode="json"
        ),
    )

    assert response.status_code == 409


def test_unauthenticated_user_can_not_update_existing_author(
    existing_author: Author, client: TestClient
):
    response = client.patch(
        f"{base_url}/{existing_author.id}",
        json=AuthorCreateFactory.create().model_dump(mode="json"),
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_authenticated_user_can_delete_existing_author(
    token: str, existing_author: Author, session: AsyncSession, client: TestClient
):
    response = client.delete(
        f"{base_url}/{existing_author.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    assert (await session.get(Author, existing_author.id)) is None


@pytest.mark.asyncio
async def test_unauthenticated_user_can_not_delete_existing_author(
    existing_author: Author, session: AsyncSession, client: TestClient
):
    response = client.delete(f"{base_url}/{existing_author.id}")

    assert response.status_code == 401

    assert (await session.get(Author, existing_author.id)) is not None


def test_authenticated_user_can_not_delete_unexisting_author(
    token: str, client: TestClient
):
    response = client.delete(
        f"/{base_url}/1", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
