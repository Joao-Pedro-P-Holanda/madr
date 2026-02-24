from unittest.mock import patch
from madr.deps import get_translation
from madr.core.settings import settings
from madr.utils.headers import get_languages_from_header


def test_get_translation_fallbacks_to_default_on_invalid_language(monkeypatch):
    monkeypatch.setattr(settings, "SUPPORTED_LOCALES", ["kz", "uz"])

    result = get_translation(["jp"])
    assert result == get_translation(settings.DEFAULT_LOCALE)


def test_get_languages_from_header_preserve_declared_order():
    result = get_languages_from_header("pt;en;de")
    assert [lang[0] for lang in result] == ["pt", "en", "de"]


def test_get_languages_from_header_recognizes_extras():
    result = get_languages_from_header("pt-BR;en-US")
    assert [lang[0] for lang in result] == ["pt-BR", "en-US"]


def test_get_languages_from_header_picks_language_with_higher_priority():
    result = get_languages_from_header("pt;q=0.7,fr;q=0.2,en")
    assert [lang[0] for lang in result] == ["en", "pt", "fr"]
