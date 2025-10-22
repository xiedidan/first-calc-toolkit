"""
Permission model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Permission(Base):
    """Permission model"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    resource = Column(String(50), nullable=False)  # 资源类型，如：user, role, model, department
    action = Column(String(50), nullable=False)    # 操作类型，如：create, read, update, delete
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
