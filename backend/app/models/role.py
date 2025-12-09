"""
Role model
"""
from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app.database import Base


class RoleType(str, enum.Enum):
    """角色类型枚举"""
    DEPARTMENT_USER = "department_user"  # 科室用户：必须有医疗机构+科室，只能查看本科室报表
    HOSPITAL_USER = "hospital_user"      # 全院用户：必须有医疗机构，可操作本院所有数据
    ADMIN = "admin"                      # 管理员：无医疗机构，可跨院操作，不能管理维护者和AI接口
    MAINTAINER = "maintainer"            # 维护者：最高权限，可管理所有用户和AI接口


class Role(Base):
    """Role model"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    role_type = Column(Enum(RoleType, values_callable=lambda x: [e.value for e in x]), nullable=False, comment="角色类型")
    menu_permissions = Column(JSON, nullable=True, comment="菜单权限列表，JSON数组格式")
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
