from datetime import datetime, timedelta
from typing import Optional
import logging
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext
from src.core.config import Settings
from src.core.exceptions import AuthenticationError, ValidationError
from src.models.user import User, UserCreate, UserUpdate
from src.services.base import BaseService

settings = Settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

class AuthService(BaseService[User]):
    """Service for handling authentication and user operations."""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.model_class = User

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def _get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm="HS256"
        )

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        query = """
        MATCH (u:User {username: $username, is_active: true})
        RETURN u
        """
        result = await self._execute_query(
            query,
            {"username": username},
            single_result=True
        )
        
        if not result:
            return None
            
        user = User(**result["u"])
        if not self._verify_password(password, user.password_hash):
            return None
            
        return user

    async def create_user(self, user_in: UserCreate) -> User:
        """Create a new user."""
        # Check if username exists
        existing = await self._execute_query(
            "MATCH (u:User {username: $username}) RETURN u",
            {"username": user_in.username},
            single_result=True
        )
        if existing:
            raise ValidationError("Username already registered")

        # Create user with hashed password
        user_data = user_in.model_dump()
        user_data["uid"] = str(uuid.uuid4())
        user_data["password_hash"] = self._get_password_hash(user_data.pop("password"))
        user_data["created_at"] = datetime.utcnow().isoformat()
        user_data["updated_at"] = user_data["created_at"]

        query = """
        CREATE (u:User $user_data)
        RETURN u
        """
        result = await self._execute_query(
            query,
            {"user_data": user_data},
            single_result=True
        )
        return User(**result["u"])

    async def update_user(self, user_id: str, user_update: UserUpdate) -> User:
        """Update a user's information."""
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = self._get_password_hash(
                update_data.pop("password")
            )
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        query = """
        MATCH (u:User {uid: $user_id})
        SET u += $update_data
        RETURN u
        """
        result = await self._execute_query(
            query,
            {"user_id": user_id, "update_data": update_data},
            single_result=True
        )
        if not result:
            raise ValidationError("User not found")
        
        return User(**result["u"])

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        query = """
        MATCH (u:User {uid: $user_id})
        SET u.is_active = false,
            u.updated_at = $timestamp
        RETURN u
        """
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            single_result=True
        )
        return bool(result)

    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """Change a user's password."""
        # Get user
        user = await self.get_by_id(user_id)
        if not user:
            raise ValidationError("User not found")
            
        # Verify current password
        if not self._verify_password(current_password, user.password_hash):
            raise AuthenticationError("Invalid current password")
            
        # Update password
        query = """
        MATCH (u:User {uid: $user_id})
        SET u.password_hash = $new_password_hash,
            u.updated_at = $timestamp
        RETURN u
        """
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "new_password_hash": self._get_password_hash(new_password),
                "timestamp": datetime.utcnow().isoformat()
            },
            single_result=True
        )
        return bool(result)

    async def logout(self, user_id: str) -> None:
        """Handle user logout."""
        # Currently just logs the event, but could be extended to handle
        # token revocation or session management if needed
        logger.info(f"User {user_id} logged out")
        return None

    async def verify_admin(self, user_id: str) -> bool:
        """Verify if a user has admin privileges."""
        query = """
        MATCH (u:User {uid: $user_id})
        RETURN u.is_admin as is_admin
        """
        result = await self._execute_query(
            query,
            {"user_id": user_id},
            single_result=True
        )
        return bool(result and result.get("is_admin", False))
