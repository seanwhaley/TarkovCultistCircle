from typing import Protocol, Dict, Any, Union, Optional, TypedDict, Literal, List, runtime_checkable
from pathlib import Path
from datetime import timedelta

class RateLimitConfig(TypedDict):
    enabled: bool
    default_limit: int
    default_window: int
    headers_enabled: bool

class DatabaseConfig(TypedDict):
    uri: str
    auth_type: Literal["basic", "oauth"]
    user: str
    password: str
    max_pool_size: int
    connection_timeout: int

class LogConfig(TypedDict):
    level: str
    format: str
    file: Path
    max_size: int
    backup_count: int
    json_indent: Optional[int]

@runtime_checkable
class ConfigProtocol(Protocol):
    """Protocol defining required configuration attributes"""
    APP_NAME: str
    SECRET_KEY: str
    DEBUG: bool
    TESTING: bool
    
    # Database settings
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    NEO4J_AUTH_TYPE: Literal["basic", "oauth"]
    
    # Cache settings
    CACHE_TYPE: str
    CACHE_DEFAULT_TIMEOUT: int
    CACHE_THRESHOLD: int
    
    # Rate limiting
    RATELIMIT_ENABLED: bool
    RATELIMIT_DEFAULT: int
    RATELIMIT_WINDOW: int
    
    # Pagination
    ITEMS_PER_PAGE: int
