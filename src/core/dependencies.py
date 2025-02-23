"""Dependency injection system."""
from typing import AsyncGenerator, Callable, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from neo4j import AsyncGraphDatabase

from src.services.tarkov_client import TarkovClient
from src.services.optimizer import ItemOptimizer
from src.config.settings import get_settings
from src.core.config import Settings
from src.core.database import DatabaseManager
from src.models.user import User
from src.services.auth_service import AuthService
from src.services.item_service import ItemService

settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_db():
    """Get database connection."""
    try:
        await DatabaseManager.initialize(settings)
        yield DatabaseManager()
    finally:
        await DatabaseManager.close()

async def get_item_service(db=Depends(get_db)) -> ItemService:
    """Get ItemService instance."""
    return ItemService(db)

async def get_auth_service(db=Depends(get_db)) -> AuthService:
    """Get AuthService instance."""
    return AuthService(db)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Get current authenticated user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await auth_service.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current user and verify they are active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user and verify they are an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_tarkov_client() -> TarkovClient:
    """Get Tarkov.dev API client."""
    return TarkovClient(settings.TARKOV_API_URL)

async def get_optimizer() -> ItemOptimizer:
    """Get item optimizer instance."""
    return ItemOptimizer()

# Commonly used dependencies
CommonDeps = Callable[..., AsyncGenerator[dict, None]]

async def common_dependencies() -> AsyncGenerator[dict, None]:
    """Common dependencies used across routes."""
    deps = {
        "db": await anext(get_db()),
        "client": await get_tarkov_client(),
        "optimizer": await get_optimizer(),
        "cache": CACHE
    }
    try:
        yield deps
    finally:
        await deps["db"].close()