from http import HTTPStatus
from typing import Annotated, Any
from typing_extensions import Doc
from fastapi.exceptions import HTTPException


wrong_credentials_exception = HTTPException(
    status_code=HTTPStatus.BAD_REQUEST, detail="Email ou senha incorretos"
)

invalid_permission_exception = HTTPException(
    status_code=HTTPStatus.UNAUTHORIZED, detail="Não autorizado"
)


class NotFoundException(HTTPException):
    def __init__(
        self,
        entity: Annotated[
            Any,
            Doc("""
                    Name of the missing entity.
                    """),
        ],
        headers: Annotated[
            dict[str, str] | None,
            Doc("""
                    Any headers to send to the client in the response.
                    """),
        ] = None,
    ) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"{entity} não consta no MADR",
            headers=headers,
        )


class ConflictException(HTTPException):
    def __init__(
        self,
        entity: Annotated[
            Any,
            Doc("""
                    Name of the conflicting entity.
                    """),
        ],
        headers: Annotated[
            dict[str, str] | None,
            Doc("""
                    Any headers to send to the client in the response.
                    """),
        ] = None,
    ) -> None:
        super().__init__(
            status_code=HTTPStatus.CONFLICT,
            detail=f"{entity} já consta no MADR",
            headers=headers,
        )
