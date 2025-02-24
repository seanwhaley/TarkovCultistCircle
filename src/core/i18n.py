"""Internationalization support for Flask applications."""
from typing import Any, Dict, Optional
import json
from pathlib import Path
import structlog
from flask import request, g
import gettext

logger = structlog.get_logger(__name__)

class I18nManager:
    """Internationalization manager for handling translations."""
    
    def __init__(
        self,
        translations_dir: Path,
        default_locale: str = "en",
        supported_locales: Optional[list[str]] = None
    ):
        self.translations_dir = translations_dir
        self.default_locale = default_locale
        self.supported_locales = supported_locales or ["en"]
        self._translations: Dict[str, Translations] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        """Load all translation files."""
        try:
            for locale in self.supported_locales:
                locale_dir = self.translations_dir / locale / "LC_MESSAGES"
                if locale_dir.exists():
                    self._translations[locale] = Translations.load(
                        dirname=str(locale_dir),
                        domain="messages"
                    )
                else:
                    logger.warning(f"No translations found for locale: {locale}")
        except Exception as e:
            logger.error(f"Failed to load translations: {str(e)}")

    def get_translator(self, locale: str) -> Translations:
        """Get translations for a specific locale."""
        if locale not in self._translations:
            logger.warning(
                f"Locale {locale} not found, falling back to {self.default_locale}"
            )
            locale = self.default_locale
        return self._translations[locale]

    @staticmethod
    def get_locale_from_request() -> str:
        """Extract locale from request."""
        return gettext.translation('messages', 
                             localedir='locales',
                             languages=[request.accept_languages.best_match(['en', 'ru', 'de']) or 'en']).info()['language']

    def translate(
        self,
        key: str,
        locale: str,
        **variables: Any
    ) -> str:
        """Translate a message key."""
        translator = self.get_translator(locale)
        return translator.gettext(key) % variables

    def translate_plural(
        self,
        singular: str,
        plural: str,
        n: int,
        locale: str,
        **variables: Any
    ) -> str:
        """Translate plural forms of a message."""
        translator = self.get_translator(locale)
        return translator.ngettext(singular, plural, n) % variables

def setup_i18n(app, translations_dir: Path, supported_locales: Optional[list[str]] = None):
    """Setup internationalization for the Flask app."""
    i18n = I18nManager(
        translations_dir=translations_dir,
        supported_locales=supported_locales
    )
    
    @app.before_request
    def before_request():
        g.locale = I18nManager.get_locale_from_request()
        g.translator = i18n.get_translator(g.locale)
        
    return i18n