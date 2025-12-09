"""
User schemas
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserStatus
from app.models.role import RoleType


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    """Schema for creating user"""
    password: str = Field(..., min_length=6, max_length=50)
    role_id: int = Field(..., description="角色ID")
    hospital_id: Optional[int] = Field(None, description="所属医疗机构ID")
    department_id: Optional[int] = Field(None, description="所属科室ID")


class UserUpdate(BaseModel):
    """Schema for updating user"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=50)
    role_id: Optional[int] = Field(None, description="角色ID")
    status: Optional[UserStatus] = None
    hospital_id: Optional[int] = Field(None, description="所属医疗机构ID")
    department_id: Optional[int] = Field(None, description="所属科室ID")


class UserInDB(UserBase):
    """Schema for user in database"""
    id: int
    status: UserStatus
    hospital_id: Optional[int] = None
    department_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    """Schema for user response"""
    role_id: int = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")
    role_type: RoleType = Field(..., description="角色类型")
    hospital_name: Optional[str] = Field(None, description="所属医疗机构名称")
    department_name: Optional[str] = Field(None, description="所属科室名称")
    menu_permissions: Optional[List[str]] = Field(None, description="菜单权限列表")


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
