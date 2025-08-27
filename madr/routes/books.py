from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError

from madr.core.security import CurrentUserDep
from madr.deps import SessionDep
from madr.exceptions import ConflictException, NotFoundException
from madr.models import Book
from madr.schema import BookBase, BookCreate, BookSchema, BookUpdate

router = APIRouter(prefix="/livro", tags=["Livros"])


@router.get("/")
async def get_list(
    session: SessionDep,
    name: Annotated[str | None, Query(alias="nome")] = None,
    start_year: Annotated[int | None, Query(alias="ano-inicial")] = None,
    end_year: Annotated[int | None, Query(alias="ano-final")] = None,
    limit: Annotated[int, Query(alias="limite")] = 20,
    offset: Annotated[int, Query(alias="deslocamento")] = 0,
):
    query = select(Book).limit(limit).offset(offset)

    if name:
        query = query.filter(
            Book.name.contains(name, autoescape=True),
        )

    if start_year:
        query = query.filter(Book.year >= start_year)

    if end_year:
        query = query.filter(Book.year <= end_year)

    results = (await session.execute(query)).scalars()

    return [
        BookSchema.model_validate(result, from_attributes=True, by_name=True)
        for result in results
    ]


@router.get("/{id}")
async def get_one(id: int, session: SessionDep):
    result = await session.get(Book, id)

    if not result:
        raise NotFoundException("Livro")

    return result


@router.post("/", status_code=HTTPStatus.CREATED)
async def create(book: BookCreate, session: SessionDep, _: CurrentUserDep):
    try:
        book_instance = Book(**book.model_dump())
        session.add(book_instance)
        await session.commit()

        return BookSchema.model_validate(
            book_instance, from_attributes=True, by_name=True
        )
    except IntegrityError:
        raise ConflictException("Livro")


@router.patch("/{id}")
async def update_book(
    id: int, book: BookUpdate, session: SessionDep, _: CurrentUserDep
):
    try:
        query = (
            update(Book)
            .values(
                {
                    k: v
                    for (k, v) in book.model_dump().items()
                    if v is not None and k in Book.__annotations__
                }
            )
            .filter(Book.id == id)
            .returning(Book)
        )

        updated_author = (await session.execute(query)).scalar_one_or_none()

        if updated_author:
            await session.commit()
            return BookBase.model_validate(
                updated_author, from_attributes=True, by_name=True
            )
        else:
            raise NotFoundException("Livro")
    except IntegrityError:
        raise ConflictException("Livro")


@router.delete("/{id}")
async def delete_book(id: int, session: SessionDep, _: CurrentUserDep):
    deleted_rows = (await session.execute(delete(Book).filter(Book.id == id))).rowcount

    if deleted_rows == 1:
        await session.commit()
        return {"message": "Livro deletado no MADR"}
    elif deleted_rows == 0:
        raise NotFoundException("Livro")
    else:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Falha ao deletar livro",
        )
