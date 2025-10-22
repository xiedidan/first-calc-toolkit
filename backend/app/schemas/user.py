"""
User schemas
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserStatus


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    """Schema for creating user"""
    password: str = Field(..., min_length=6, max_length=50)
    role_ids: List[int] = Field(default_factory=list)


class UserUpdate(BaseModel):
    """Schema for updating user"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=50)
    role_ids: Optional[List[int]] = None
    status: Optional[UserStatus] = None


class UserInDB(UserBase):
    """Schema for user in database"""
    id: int
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    """Schema for user response"""
    roles: List[str] = Field(default_factory=list)  # Role codes


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data"""
    username: Optional[str] = None
    user_id: Optional[int] = None
