"""
Role schemas
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.role import RoleType


class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    code: str = Field(..., min_length=1, max_length=50, description="角色代码")
    role_type: RoleType = Field(..., description="角色类型")
    description: Optional[str] = Field(None, description="角色描述")


class RoleCreate(RoleBase):
    """Schema for creating role"""
    menu_permissions: Optional[List[str]] = Field(None, description="菜单权限列表")


class RoleUpdate(BaseModel):
    """Schema for updating role"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="角色名称")
    role_type: Optional[RoleType] = Field(None, description="角色类型")
    menu_permissions: Optional[List[str]] = Field(None, description="菜单权限列表")
    description: Optional[str] = Field(None, description="角色描述")


class Role(RoleBase):
    """Schema for role response"""
    id: int
    menu_permissions: Optional[List[str]] = Field(None, description="菜单权限列表")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleListItem(BaseModel):
    """Schema for role list item"""
    id: int
    name: str
    code: str
    role_type: RoleType
    role_type_display: str = Field(..., description="角色类型显示名称")
    description: Optional[str] = None
    user_count: int = Field(0, description="使用此角色的用户数")
    created_at: datetime

    class Config:
        from_attributes = True


# 菜单项定义
class MenuItem(BaseModel):
    """菜单项"""
    path: str = Field(..., description="菜单路径")
    name: str = Field(..., description="菜单名称")
    children: Optional[List["MenuItem"]] = Field(None, description="子菜单")


# 角色类型显示名称映射
ROLE_TYPE_DISPLAY = {
    RoleType.DEPARTMENT_USER: "科室用户",
    RoleType.HOSPITAL_USER: "全院用户",
    RoleType.ADMIN: "管理员",
    RoleType.MAINTAINER: "维护者",
}
