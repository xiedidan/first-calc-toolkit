"""
系统设置模型
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base


class SystemSetting(Base):
    """系统设置表"""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    key = Column(String(100), unique=True, nullable=False, index=True, comment="设置键")
    value = Column(Text, nullable=True, comment="设置值")
    description = Column(Text, nullable=True, comment="设置描述")
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
