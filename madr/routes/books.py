from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError

from madr.core.security import CurrentUserDep
from madr.deps import SessionDep
from madr.exceptions import ConflictException, NotFoundException
from madr.models import Author, Book
from madr.schema import BookCreate, BookSchema, BookUpdate

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

    results = (await session.execute(query)).scalars().unique()

    return [
        BookSchema.model_validate(
            {
                **result.__dict__,
                **{"authors_names": [author.name for author in result.authors]},
            },
            by_name=True,
        )
        for result in results
    ]


@router.get("/{id}")
async def get_one(id: int, session: SessionDep):
    result = (
        (await session.execute(select(Book).filter(Book.id == id)))
        .unique()
        .scalar_one_or_none()
    )

    if not result:
        raise NotFoundException("Livro")

    return BookSchema.model_validate(
        {
            **result.__dict__,
            "authors_names": [author.name for author in result.authors],
        },
        by_name=True,
    )


@router.post("/", status_code=HTTPStatus.CREATED)
async def create(book: BookCreate, session: SessionDep, _: CurrentUserDep):
    try:
        book_instance = Book(**book.model_dump())
        authors_to_add = (
            (
                await session.execute(
                    select(Author).filter(Author.id.in_(book.author_ids))
                )
            )
            .scalars()
            .all()
        )

        if len(authors_to_add) != len(book.author_ids):
            existing_ids = [author.id for author in authors_to_add]

            unmatched_ids = [
                author_id
                for author_id in book.author_ids
                if author_id not in existing_ids
            ]
            raise HTTPException(
                detail=f"Autores com ids {unmatched_ids} não foram encontrados",
                status_code=404,
            )

        book_instance.authors.extend(authors_to_add)

        session.add(book_instance)

        await session.commit()

        await session.refresh(book_instance)

        response = BookSchema.model_validate(
            {
                **book_instance.__dict__,
                "authors_names": [author.name for author in book_instance.authors],
            },
            by_name=True,
        )
        return response

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
        updated_book = (await session.execute(query)).unique().scalar_one_or_none()
        if updated_book:
            if book.author_ids is not None:
                authors_to_use = (
                    (
                        await session.execute(
                            select(Author).filter(Author.id.in_(book.author_ids))
                        )
                    )
                    .scalars()
                    .all()
                )
                if len(authors_to_use) != len(book.author_ids):
                    existing_ids = [author.id for author in authors_to_use]

                    unmatched_ids = [
                        author_id
                        for author_id in book.author_ids
                        if author_id not in existing_ids
                    ]
                    raise HTTPException(
                        detail=f"Autores com ids {unmatched_ids} não foram encontrados",
                        status_code=404,
                    )
                await session.refresh(updated_book)
                updated_book.authors = list(authors_to_use)

            await session.commit()
            await session.refresh(updated_book)

            return BookSchema.model_validate(
                {
                    **updated_book.__dict__,
                    "authors_names": [author.name for author in updated_book.authors],
                },
                by_name=True,
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
