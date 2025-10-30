"""
计算流程模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class CalculationWorkflow(Base):
    """计算流程模型"""
    __tablename__ = "calculation_workflows"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False, index=True, comment="模型版本ID")
    name = Column(String(200), nullable=False, comment="流程名称")
    description = Column(Text, comment="流程描述")
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    version = relationship("ModelVersion", back_populates="workflows")
    steps = relationship("CalculationStep", back_populates="workflow", cascade="all, delete-orphan", order_by="CalculationStep.sort_order")
    calculation_tasks = relationship("CalculationTask", back_populates="workflow")
