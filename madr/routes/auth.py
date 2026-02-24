from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError

from madr.core.security import (
    CurrentUserDep,
    create_access_token,
    verify_password_hash,
)
from madr.deps import I18nDep, SessionDep
from madr.exceptions import ConflictException
from madr.models import User as UserTable
from madr.schema import AccessToken, UserCreate, UserSchema

router = APIRouter(tags=["Conta"])


@router.get("/conta/minha-conta")
async def account_info(current_user: CurrentUserDep):
    return UserSchema.model_validate(current_user, from_attributes=True, by_name=True)


@router.post("/token")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    i18n: I18nDep,
    session: SessionDep,
):
    query = select(UserTable).where(UserTable.email == form.username)
    user = await session.scalar(query)

    if not user or not verify_password_hash(
        plain_password=form.password, hashed_password=user.password
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=i18n["exceptions"]["wrong_credentials"],
        )

    token = create_access_token({"sub": user.email})

    return AccessToken(access_token=token, token_type="Bearer")


@router.post("/refresh-token")
async def refresh_token(current_user: CurrentUserDep):
    new_token = create_access_token({"sub": current_user.email})
    return AccessToken(access_token=new_token, token_type="Bearer")


@router.post("/conta", status_code=HTTPStatus.CREATED)
async def sign_up(user: UserCreate, i18n: I18nDep, session: SessionDep):
    try:
        query = insert(UserTable).values(user.model_dump()).returning(UserTable)
        result = (await session.execute(query)).scalar_one()
        serialized_result = UserSchema.model_validate(
            result, from_attributes=True, by_name=True
        )
        await session.commit()

        return serialized_result
    except IntegrityError:
        raise ConflictException(entity="user", i18n=i18n)


@router.put("/conta/{id}")
async def update_account(
    user: UserCreate,
    id: UUID,
    i18n: I18nDep,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    try:
        if id != current_user.id:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=i18n["exceptions"]["unauthorized"],
            )

        query = (
            update(UserTable)
            .values(user.model_dump())
            .filter(UserTable.id == id)
            .returning(UserTable)
        )

        result = (await session.execute(query)).scalar_one()
        serialized_result = UserSchema.model_validate(
            result, from_attributes=True, by_name=True
        )

        await session.commit()

        return serialized_result

    except IntegrityError:
        raise ConflictException(entity="user", i18n=i18n)


@router.delete("/conta/{id}")
async def delete_account(
    id: UUID, i18n: I18nDep, session: SessionDep, current_user: CurrentUserDep
):
    if id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=i18n["exceptions"]["unauthorized"],
        )

    query = delete(UserTable).filter(UserTable.id == id)
    deleted_rows = (await session.execute(query)).rowcount

    if deleted_rows == 1:
        await session.commit()
        return i18n["success"]["delete"].format(i18n["entities"]["user"])
    else:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=i18n["exceptions"]["delete"].format(i18n["entities"]["user"]),
        )
