from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
)
from pydantic_extra_types.isbn import ISBN

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


class BookBase(BaseModel):
    isbn: ISBN
    name: Annotated[str, BeforeValidator(sanitize_name)] = Field(alias="nome")
    year: int = Field(alias="ano")
    author_ids: list[int] = Field(alias="ids_romancistas", default=[])

    model_config = ConfigDict(validate_by_name=True)


class BookCreate(BookBase): ...


class BookUpdate(BaseModel):
    isbn: ISBN | None
    name: Annotated[str | None, BeforeValidator(sanitize_name)] = Field(alias="nome")
    year: int | None = Field(alias="ano")
    author_ids: list[int] | None = Field(alias="ids_romancistas")

    model_config = ConfigDict(validate_by_name=True)


class BookSchema(BookBase):
    id: int


class AuthorBase(BaseModel):
    name: str = Field(alias="nome")
    nationality: str = Field(alias="nacionalidade")
    birth_date: date = Field(alias="data-nascimento")

    model_config = ConfigDict(validate_by_name=True)


class AuthorSchema(AuthorBase):
    id: int


class AuthorCreate(AuthorBase): ...


class AuthorUpdate(BaseModel):
    name: str | None
    nationality: str | None = Field(alias="nacionalidade")
    birth_date: date | None = Field(alias="data-nascimento")

    model_config = ConfigDict(validate_by_name=True)
