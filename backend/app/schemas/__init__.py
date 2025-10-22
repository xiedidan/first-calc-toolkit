"""
Pydantic模型（请求/响应模型）
"""
from .user import (
    User,
    UserCreate,
    UserUpdate,
    UserLogin,
    Token,
    TokenData,
)
from .role import Role, RoleCreate, RoleUpdate
from .permission import Permission, PermissionCreate
from .department import (
    Department,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentList,
)

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserLogin",
    "Token",
    "TokenData",
    "Role",
    "RoleCreate",
    "RoleUpdate",
    "Permission",
    "PermissionCreate",
    "Department",
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentList",
]
