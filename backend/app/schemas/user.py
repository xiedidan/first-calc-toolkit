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
    role: str = Field(..., description="用户角色：admin或user")
    hospital_id: Optional[int] = Field(None, description="所属医疗机构ID，管理员为空，普通用户必填")


class UserUpdate(BaseModel):
    """Schema for updating user"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=50)
    role: Optional[str] = Field(None, description="用户角色：admin或user")
    status: Optional[UserStatus] = None
    hospital_id: Optional[int] = Field(None, description="所属医疗机构ID，管理员为空，普通用户必填")


class UserInDB(UserBase):
    """Schema for user in database"""
    id: int
    status: UserStatus
    hospital_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    """Schema for user response"""
    role: str = Field(..., description="用户角色：admin或user")
    hospital_name: Optional[str] = Field(None, description="所属医疗机构名称")


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
