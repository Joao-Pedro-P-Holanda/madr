from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID


@dataclass
class User:
    id: UUID
    name: str
    email: str
    password: str
    created_at: datetime = field(init=False)


@dataclass
class Author:
    id: int = field(init=False)

    name: str
    nationality: str
    birth_date: date
    created_at: datetime = field(init=False)


@dataclass
class Book:
    id: int = field(init=False)

    name: str
    year: int
    isbn: str | None = None
    authors: list[Author] = field(default_factory=list)
    created_at: datetime = field(init=False)
