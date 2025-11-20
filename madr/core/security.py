from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, encode, decode, ExpiredSignatureError
from sqlalchemy import select

from madr.deps import SessionDep
from madr.models import User
from .settings import settings
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

pwd_context = PasswordHash((Argon2Hasher(),))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", refreshUrl="refresh-token")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=settings.JWT_EXPIRATION_TIME
    )
    to_encode.update({"exp": expire})

    encoded_jwt = encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def hash_password(password: str) -> str:
    return pwd_context.hash(password=password)


def verify_password_hash(plain_password: str, hashed_password: str):
    return pwd_context.verify(password=plain_password, hash=hashed_password)


async def get_current_user(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        subject_email = payload.get("sub")

        if not subject_email:
            raise credentials_exception

    except (DecodeError, ExpiredSignatureError):
        raise credentials_exception

    query = select(User).filter(User.email == subject_email)
    user = (await session.execute(query)).scalar_one_or_none()

    if not user:
        raise credentials_exception

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
