"""
Permission schemas
"""
from datetime import datetime
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """Base permission schema"""
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=1, max_length=50)
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)


class PermissionCreate(PermissionBase):
    """Schema for creating permission"""
    pass


class PermissionInDB(PermissionBase):
    """Schema for permission in database"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Permission(PermissionInDB):
    """Schema for permission response"""
    pass
