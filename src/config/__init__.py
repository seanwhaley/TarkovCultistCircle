from typing import Type
from src.types.config import ConfigProtocol
from .config import get_config

Config: Type[ConfigProtocol] = get_config()

__all__ = ['Config']