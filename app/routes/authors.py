from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError

from app.core.security import CurrentUserDep
from app.deps import SessionDep
from app.exceptions import ConflictException, NotFoundException
from app.models import Author
from app.schema import AuthorCreate, AuthorSchema, AuthorUpdate

router = APIRouter(prefix="/romancista", tags=["Autores"])


@router.get("/")
async def get_list(
    session: SessionDep,
    name: Annotated[str | None, Query(alias="nome")] = None,
    limit: Annotated[int, Query(alias="limite")] = 20,
    offset: Annotated[int, Query(alias="deslocamento")] = 0,
):
    query = select(Author).limit(limit).offset(offset)

    if name:
        query = query.filter(
            Author.name.contains(name),
        )

    results = (await session.execute(query)).scalars()

    return [
        AuthorSchema.model_validate(result, from_attributes=True, by_name=True)
        for result in results
    ]


@router.get("/{id}")
async def get_one(
    id: int,
    session: SessionDep,
):
    result = await session.get(Author, id)

    if not result:
        raise NotFoundException("Autor")

    return AuthorSchema.model_validate(result, from_attributes=True, by_name=True)


@router.post("/", status_code=HTTPStatus.CREATED)
async def create(author: AuthorCreate, session: SessionDep, _: CurrentUserDep):
    try:
        result = (
            await session.execute(
                insert(Author).values(author.model_dump()).returning(Author)
            )
        ).scalar_one()

        await session.commit()
        await session.refresh(result)

        return AuthorSchema.model_validate(result, from_attributes=True, by_name=True)
    except IntegrityError:
        raise ConflictException("Autor")


@router.patch("/{id}")
async def update_author(
    author: AuthorUpdate, id: int, session: SessionDep, _: CurrentUserDep
):
    try:
        query = (
            update(Author)
            .values({k: v for (k, v) in author.model_dump().items() if v is not None})
            .filter(Author.id == id)
            .returning(Author)
        )

        updated_author = (await session.execute(query)).scalar_one_or_none()

        if updated_author:
            await session.commit()
            return AuthorSchema.model_validate(
                updated_author, from_attributes=True, by_name=True
            )
        else:
            raise NotFoundException("Autor")
    except IntegrityError:
        raise ConflictException("Autor")


@router.delete("/{id}")
async def delete_author(id: int, session: SessionDep, _: CurrentUserDep):
    deleted_rows = (
        await session.execute(delete(Author).filter(Author.id == id))
    ).rowcount

    if deleted_rows == 1:
        await session.commit()
        return {"message": "Romancista deletado no MADR"}
    elif deleted_rows == 0:
        raise NotFoundException("Autor")
    else:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Falha ao deletar autor",
        )
