"""
医疗机构模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Hospital(Base):
    """医疗机构模型"""
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="医疗机构编码")
    name = Column(String(200), nullable=False, comment="医疗机构名称")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    users = relationship("User", back_populates="hospital")
    model_versions = relationship("ModelVersion", back_populates="hospital")
    departments = relationship("Department", back_populates="hospital")
    charge_items = relationship("ChargeItem", back_populates="hospital")
    data_templates = relationship("DataTemplate", back_populates="hospital")
