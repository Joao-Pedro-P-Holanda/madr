from collections.abc import Mapping
from typing import Annotated, Any

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from madr.core.database import get_async_session
from madr.core.i18n import get_translation
from madr.utils.headers import get_languages_from_header


def get_i18n(request: Request) -> Mapping[str, str]:
    raw_text = request.headers.get("accept-language") or ""

    langs_with_weights = get_languages_from_header(raw_text)

    return get_translation(lang[0] for lang in langs_with_weights)


I18nDep = Annotated[Mapping[str, Any], Depends(get_i18n)]

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
