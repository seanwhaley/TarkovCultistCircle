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
    
    # Redis settings
    REDIS_URL: str = "redis://redis:6379/0"
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    API_RATE_LIMIT: int = 1000
    API_REFRESH_LIMIT: int = 20
    
    # Auth settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_PASSWORD_HASH: str
    AUTH_REGISTER_LIMIT: int = 3
    
    # Feature flags
    ENABLE_GRAPHQL: bool = True
    ENABLE_DEBUG_ROUTES: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True