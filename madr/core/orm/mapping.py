from uuid import uuid4
from sqlalchemy import (
    UUID,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    text,
)
from madr.models import User, Author, Book
from sqlalchemy.orm import registry, relationship


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "pk_%(table_name)s",
}


meta = MetaData(naming_convention=naming_convention)


mapping_registry = registry(metadata=meta)

user_table = Table(
    "user",
    meta,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("name", String, nullable=False),
    Column("email", String, nullable=False, unique=True),
    Column("password", String, nullable=False),
    Column(
        "created_at", DateTime, nullable=False, server_default=text("current_timestamp")
    ),
    UniqueConstraint("email", name="uq_user_email"),
)

author_table = Table(
    "author",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("nationality", String, nullable=False),
    Column("birth_date", Date, nullable=False),
    Column(
        "created_at", DateTime, nullable=False, server_default=text("current_timestamp")
    ),
    UniqueConstraint("name", name="uq_author_name"),
)

book_table = Table(
    "book",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("isbn", String, nullable=True),
    Column("name", String, nullable=False),
    Column("year", Integer, nullable=False),
    Column(
        "created_at", DateTime, nullable=False, server_default=text("current_timestamp")
    ),
    UniqueConstraint("name", name="uq_book_name"),
)

book_authorship_table = Table(
    "book_authorship",
    meta,
    Column("author_id", Integer, ForeignKey("author.id"), primary_key=True),
    Column("book_id", Integer, ForeignKey("book.id"), primary_key=True),
    Column(
        "created_at", DateTime, nullable=False, server_default=text("current_timestamp")
    ),
)


def init_mappings():
    mapping_registry.map_imperatively(User, user_table)
    mapping_registry.map_imperatively(Author, author_table)
    mapping_registry.map_imperatively(
        Book,
        book_table,
        properties={
            "authors": relationship(Author, lazy="joined", secondary="book_authorship")
        },
    )


def remove_mappings():
    mapping_registry.dispose()
