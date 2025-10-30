"""
计算步骤执行日志模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class CalculationStepLog(Base):
    """计算步骤执行日志模型"""
    __tablename__ = "calculation_step_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), ForeignKey("calculation_tasks.task_id", ondelete="CASCADE"), nullable=False, index=True, comment="计算任务ID")
    step_id = Column(Integer, ForeignKey("calculation_steps.id", ondelete="CASCADE"), nullable=False, index=True, comment="计算步骤ID")
    department_id = Column(Integer, comment="科室ID")
    status = Column(String(20), nullable=False, comment="执行状态(success/failed)")
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    duration_ms = Column(Integer, comment="执行耗时(毫秒)")
    result_data = Column(JSONB, comment="执行结果数据")
    execution_info = Column(Text, comment="执行信息")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    step = relationship("CalculationStep", back_populates="logs")
    task = relationship("CalculationTask", back_populates="step_logs")
