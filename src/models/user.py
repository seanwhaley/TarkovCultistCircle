from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    password: Optional[str] = Field(default=None, min_length=8)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class User(UserBase):
    """Complete user model."""
    uid: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "username": "testuser",
                "is_active": True,
                "is_admin": False,
                "created_at": "2024-02-17T00:00:00",
                "updated_at": "2024-02-17T00:00:00"
            }
        }

class Token(BaseModel):
    """Token model."""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Token payload model."""
    sub: Optional[str] = None