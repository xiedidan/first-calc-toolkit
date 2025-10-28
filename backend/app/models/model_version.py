"""
模型版本模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base


class ModelVersion(Base):
    """模型版本模型"""
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), unique=True, nullable=False, index=True, comment="版本号")
    name = Column(String(100), nullable=False, comment="版本名称")
    description = Column(Text, comment="版本描述")
    is_active = Column(Boolean, default=False, nullable=False, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    nodes = relationship("ModelNode", back_populates="version", cascade="all, delete-orphan")
    workflows = relationship("CalculationWorkflow", back_populates="version", cascade="all, delete-orphan")
