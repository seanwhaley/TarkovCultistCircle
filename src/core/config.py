from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings for automatic env loading."""
    
    # Core settings
    DEBUG: bool = False
    SECRET_KEY: str
    ENVIRONMENT: str = "development"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:3000"]
    
    # Database settings
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str
    NEO4J_MAX_POOL_SIZE: int = 50
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    API_RATE_LIMIT: int = 1000  # Requests per hour
    API_REFRESH_LIMIT: int = 20  # Market data refreshes per hour
    
    # Auth settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_PASSWORD_HASH: str
    
    # Rate limiting settings
    RATELIMIT_STORAGE_URL: str = "memory://"
    RATELIMIT_STRATEGY: str = "fixed-window"
    RATELIMIT_DEFAULT: str = "1000 per hour"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True