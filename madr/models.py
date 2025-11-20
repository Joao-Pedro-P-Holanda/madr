from dataclasses import dataclass, field
from datetime import date
from uuid import UUID


@dataclass
class User:
    id: UUID
    name: str
    email: str
    password: str


@dataclass
class Author:
    id: int = field(init=False)

    name: str
    nationality: str
    birth_date: date


@dataclass
class Book:
    id: int = field(init=False)

    name: str
    year: int
    isbn: str | None = None
    authors: list[Author] = field(default_factory=list)
