from datetime import datetime
from http import HTTPStatus
from fastapi import Request, Response


def get_last_modified_response(
    last_modified: datetime, request: Request
) -> Response | None:
    """
    Returns a NOT MODIFIED blank response only if the
    last_modified date is older than the if-modified-since header
    """
    if "if-modified-since" in request.headers:
        if last_modified <= datetime.fromisoformat(
            request.headers["if-modified-since"]
        ):
            return Response(
                headers={"Last-Modified": last_modified.isoformat()},
                status_code=HTTPStatus.NOT_MODIFIED,
            )
