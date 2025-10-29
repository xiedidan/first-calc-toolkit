"""
计算步骤模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class CalculationStep(Base):
    """计算步骤模型"""
    __tablename__ = "calculation_steps"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("calculation_workflows.id", ondelete="CASCADE"), nullable=False, index=True, comment="计算流程ID")
    name = Column(String(200), nullable=False, comment="步骤名称")
    description = Column(Text, comment="步骤描述")
    code_type = Column(String(20), nullable=False, comment="代码类型(python/sql)")
    code_content = Column(Text, nullable=False, comment="代码内容")
    data_source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True, index=True, comment="数据源ID（SQL步骤使用）")
    python_env = Column(String(200), nullable=True, comment="Python虚拟环境路径（Python步骤使用）")
    sort_order = Column(Numeric(10, 2), nullable=False, index=True, comment="执行顺序")
    is_enabled = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    workflow = relationship("CalculationWorkflow", back_populates="steps")
    data_source = relationship("DataSource", foreign_keys=[data_source_id])
    logs = relationship("CalculationStepLog", back_populates="step", cascade="all, delete-orphan")
