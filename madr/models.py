from datetime import date, datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey, MetaData, UniqueConstraint


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "pk_%(table_name)s",
}


meta = MetaData(naming_convention=naming_convention)


class Base(DeclarativeBase):
    metadata = meta

    created_at: Mapped[datetime] = mapped_column(default=datetime.now())


class User(Base):
    __tablename__ = "user"
    __table_args__ = (UniqueConstraint("email"),)

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()


class Author(Base):
    __tablename__ = "author"
    __table_args__ = (UniqueConstraint("name"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()
    nationality: Mapped[str] = mapped_column()
    birth_date: Mapped[date] = mapped_column()


class Book(Base):
    __tablename__ = "book"
    __table_args__ = (UniqueConstraint("name"),)
    id: Mapped[int] = mapped_column(primary_key=True)

    isbn: Mapped[str | None] = mapped_column()

    name: Mapped[str] = mapped_column()

    year: Mapped[int] = mapped_column()


class BookAuthorship(Base):
    __tablename__ = "book_authorship"

    author_id = mapped_column(ForeignKey(Author.id), primary_key=True)
    book_id = mapped_column(ForeignKey(Book.id), primary_key=True)
