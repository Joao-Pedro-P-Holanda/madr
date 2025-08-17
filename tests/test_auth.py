from datetime import datetime, timedelta
from http import HTTPStatus
from fastapi.testclient import TestClient
import re
from freezegun import freeze_time
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from madr.core.settings import settings
from madr.models import User
from .factories import UserCreateFactory


def test_user_can_create_account_with_valid_email_and_password(client: TestClient):
    user = UserCreateFactory.create()

    response = client.post("/conta", json=user.model_dump(mode="python"))
    assert response.status_code == HTTPStatus.CREATED
    user_name = response.json()["username"]
    assert re.findall(r"\s", user_name) == re.findall(" ", user_name)
    assert user_name.replace(" ", "").isalpha()


def test_user_can_not_create_account_with_existing_email(
    client: TestClient, existing_user: User
):
    new_user = UserCreateFactory.create(email=existing_user.email)

    response = client.post("/conta", json=new_user.model_dump(mode="python"))
    assert response.status_code == HTTPStatus.CONFLICT


def test_user_can_get_token_with_valid_email_and_password(
    client: TestClient, existing_user: User
):
    response = client.post(
        "/token", data={"username": existing_user.email, "password": "password"}
    )
    assert response.status_code == HTTPStatus.OK


def test_user_cannot_get_token_with_not_existing_email(client: TestClient):
    response = client.post(
        "/token", data={"username": "notvalid@mail.com", "password": "mypassword"}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_user_cannot_get_token_with_invalid_password(
    client: TestClient, existing_user: User
):
    response = client.post(
        "/token", data={"username": existing_user.email, "password": "invalidpassword"}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_user_can_use_non_expired_token(client: TestClient, existing_user: User):
    token_response = client.post(
        "/token", data={"username": existing_user.email, "password": "password"}
    )
    assert token_response.status_code == HTTPStatus.OK

    info_response = client.get(
        "/conta/minha-conta",
        headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
    )

    assert info_response.status_code == HTTPStatus.OK


def test_user_cannot_use_expired_token(client: TestClient, existing_user: User):
    now = datetime.now()
    with freeze_time(now):
        token_response = client.post(
            "/token", data={"username": existing_user.email, "password": "password"}
        )
        assert token_response.status_code == HTTPStatus.OK

    with freeze_time(now + timedelta(minutes=settings.JWT_EXPIRATION_TIME + 1)):
        info_response = client.get(
            "/conta/minha-conta",
            headers={
                "Authorization": f"Bearer {token_response.json()['access_token']}"
            },
        )

        assert info_response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_cannot_use_token_of_deleted_user(
    client: TestClient, existing_user: User, session: AsyncSession
):
    token_response = client.post(
        "/token", data={"username": existing_user.email, "password": "password"}
    )
    assert token_response.status_code == HTTPStatus.OK

    await session.delete(existing_user)
    await session.commit()

    info_response = client.get(
        "/conta/minha-conta",
        headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
    )

    assert info_response.status_code == HTTPStatus.UNAUTHORIZED


def test_user_can_refresh_non_expired_token(client: TestClient, existing_user: User):
    token_response = client.post(
        "/token", data={"username": existing_user.email, "password": "password"}
    )
    assert token_response.status_code == HTTPStatus.OK

    refresh_response = client.post(
        "/refresh-token",
        headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
    )

    assert refresh_response.status_code == HTTPStatus.OK
    assert (
        refresh_response.json()["access_token"] == token_response.json()["access_token"]
    )


def test_user_cannot_refresh_expired_token(client: TestClient, existing_user: User):
    now = datetime.now()
    with freeze_time(now):
        token_response = client.post(
            "/token", data={"username": existing_user.email, "password": "password"}
        )
        assert token_response.status_code == HTTPStatus.OK

    with freeze_time(now + timedelta(minutes=settings.JWT_EXPIRATION_TIME + 1)):
        refresh_response = client.post(
            "/refresh-token",
            headers={
                "Authorization": f"Bearer {token_response.json()['access_token']}"
            },
        )

        assert refresh_response.status_code == HTTPStatus.UNAUTHORIZED


def test_user_can_update_its_own_information(client: TestClient, existing_user: User):
    token_response = client.post(
        "/token", data={"username": existing_user.email, "password": "password"}
    )
    assert token_response.status_code == HTTPStatus.OK

    update_response = client.put(
        f"/conta/{existing_user.id}",
        headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
        json=UserCreateFactory.create().model_dump(mode="python"),
    )

    assert update_response.status_code == HTTPStatus.OK


def test_user_cannot_update_to_already_existing_email(
    client: TestClient, existing_user: User, another_user: User
):
    token_response = client.post(
        "/token", data={"username": existing_user.email, "password": "password"}
    )
    assert token_response.status_code == HTTPStatus.OK

    update_response = client.put(
        f"/conta/{existing_user.id}",
        headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
        json=UserCreateFactory.create(email=another_user.email).model_dump(
            mode="python"
        ),
    )

    assert update_response.status_code == HTTPStatus.CONFLICT


def test_user_cannot_update_another_user_information(
    client: TestClient, existing_user: User, another_user
):
    token_response = client.post(
        "/token", data={"username": existing_user.email, "password": "password"}
    )
    assert token_response.status_code == HTTPStatus.OK

    update_response = client.put(
        f"/conta/{another_user.id}",
        headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
        json=UserCreateFactory.create().model_dump(mode="python"),
    )

    assert update_response.status_code == HTTPStatus.UNAUTHORIZED


def test_user_can_delete_its_own_account(client: TestClient, existing_user: User):
    token_response = client.post(
        "/token", data={"username": existing_user.email, "password": "password"}
    )
    assert token_response.status_code == HTTPStatus.OK

    delete_response = client.delete(
        f"/conta/{existing_user.id}",
        headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
    )

    assert delete_response.status_code == HTTPStatus.OK


def test_user_cannot_delete_another_user_account(
    client: TestClient, existing_user: User, another_user
):
    token_response = client.post(
        "/token", data={"username": existing_user.email, "password": "password"}
    )
    assert token_response.status_code == HTTPStatus.OK

    delete_response = client.delete(
        f"/conta/{another_user.id}",
        headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
    )

    assert delete_response.status_code == HTTPStatus.UNAUTHORIZED
