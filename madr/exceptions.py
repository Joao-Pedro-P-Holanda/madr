from collections.abc import Mapping
from http import HTTPStatus
from typing import Annotated, Any
from typing_extensions import Doc
from fastapi.exceptions import HTTPException


class NotFoundException(HTTPException):
    def __init__(
        self,
        entity: Annotated[
            Any,
            Doc("""
                    Name of the missing entity.
                    """),
        ],
        i18n: Annotated[
            Mapping[str, Any],
            Doc("""
                    Translation keys
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
            detail=i18n["exceptions"]["not_found"].format(i18n["entities"][entity]),
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
        i18n: Annotated[
            Mapping[str, Any],
            Doc("""
                    Translation keys
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
            detail=i18n["exceptions"]["conflict"].format(i18n["entities"][entity]),
            headers=headers,
        )
