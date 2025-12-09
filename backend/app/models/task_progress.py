"""
任务进度记录模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ProgressStatus(str, enum.Enum):
    """进度状态枚举"""
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class TaskProgress(Base):
    """任务进度记录模型"""
    __tablename__ = "task_progress"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    task_id = Column(Integer, ForeignKey("classification_tasks.id", ondelete="CASCADE"), nullable=False, index=True, comment="分类任务ID")
    charge_item_id = Column(Integer, ForeignKey("charge_items.id", ondelete="CASCADE"), nullable=False, comment="收费项目ID")
    status = Column(SQLEnum(ProgressStatus), default=ProgressStatus.pending, nullable=False, comment="处理状态")
    error_message = Column(Text, nullable=True, comment="错误信息")
    processed_at = Column(DateTime, nullable=True, comment="处理时间")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")

    # 关系
    task = relationship("ClassificationTask", back_populates="progress_records")
    charge_item = relationship("ChargeItem")

    # 唯一约束：同一任务中每个项目只记录一次
    __table_args__ = (
        UniqueConstraint('task_id', 'charge_item_id', name='uq_task_progress'),
    )
