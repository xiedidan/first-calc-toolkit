"""
Role schemas
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating role"""
    permission_ids: List[int] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    """Schema for updating role"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class RoleInDB(RoleBase):
    """Schema for role in database"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Role(RoleInDB):
    """Schema for role response"""
    permissions: List[str] = Field(default_factory=list)  # Permission codes
