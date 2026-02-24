from collections.abc import Iterable, Mapping
from functools import lru_cache
from pathlib import Path
from .settings import settings
import os
import madr
import tomllib

LOCALE_DIR = Path(f"{os.path.dirname(madr.__file__)}/../locales")


def get_translation(languages: Iterable[str]) -> Mapping[str, str]:
    """
    Recebe uma sequência ordenada de idiomas e retorna o primeiro disponível,
    se nenhum idioma estiver registrado usa o idioma padrão
    """

    # utilizando casamento exato, por quê normalmente uma requisição com
    # Accept-Language vai definir a versão padrão e específica de um país
    # p. ex. en, en-US

    for lang in languages:
        if lang in settings.SUPPORTED_LOCALES:
            return _load_locale_file(lang)
    else:
        return _load_locale_file(settings.DEFAULT_LOCALE)


@lru_cache
def _load_locale_file(lang: str):
    with open(LOCALE_DIR / f"{lang}.toml", "rb") as file:
        return tomllib.load(file)
