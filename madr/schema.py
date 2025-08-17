from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, BeforeValidator

from madr.core.security import hash_password
from madr.utils.sanitization import sanitize_name


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    name: Annotated[str, BeforeValidator(sanitize_name)] = Field(
        alias="username", min_length=1
    )
    email: EmailStr

    model_config = ConfigDict(validate_by_name=True)


class UserCreate(UserBase):
    password: Annotated[str, BeforeValidator(hash_password)] = Field(
        alias="senha", min_length=8
    )


class UserSchema(UserBase):
    id: UUID


class BookSchema(BaseModel):
    isbn: str


class Author(BaseModel): ...
