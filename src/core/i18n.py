from typing import Any, Dict, Optional
import json
from pathlib import Path
import structlog
from fastapi import Request
from babel import Locale
from babel.support import Translations

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
    def get_locale_from_request(request: Request) -> str:
        """Extract locale from request."""
        # Try to get locale from query params
        locale = request.query_params.get("lang")
        if locale:
            return locale
            
        # Try to get locale from Accept-Language header
        accept_language = request.headers.get("Accept-Language", "")
        if accept_language:
            # Parse the Accept-Language header
            try:
                locale = accept_language.split(",")[0].split("-")[0]
                return locale
            except Exception:
                pass
                
        return "en"

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

class LocalizationMiddleware:
    """Middleware for handling localization in requests."""
    
    def __init__(
        self,
        i18n: I18nManager,
        default_locale: str = "en"
    ):
        self.i18n = i18n
        self.default_locale = default_locale

    async def __call__(self, request: Request, call_next):
        # Get locale from request
        locale = I18nManager.get_locale_from_request(request)
        
        # Validate locale
        if locale not in self.i18n.supported_locales:
            locale = self.default_locale
            
        # Add locale and translator to request state
        request.state.locale = locale
        request.state.translator = self.i18n.get_translator(locale)
        
        response = await call_next(request)
        return response

def setup_i18n(app, translations_dir: Path, supported_locales: Optional[list[str]] = None):
    """Setup internationalization for the application."""
    i18n = I18nManager(
        translations_dir=translations_dir,
        supported_locales=supported_locales
    )
    app.add_middleware(LocalizationMiddleware, i18n=i18n)
    return i18n