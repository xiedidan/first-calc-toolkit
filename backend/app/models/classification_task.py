"""
分类任务模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    paused = "paused"


class ClassificationTask(Base):
    """分类任务模型"""
    __tablename__ = "classification_tasks"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    task_name = Column(String(100), nullable=False, comment="任务名称")
    model_version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False, comment="模型版本ID")
    charge_categories = Column(JSON, nullable=False, comment="收费类别列表")
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.pending, nullable=False, comment="任务状态")
    total_items = Column(Integer, default=0, nullable=False, comment="总项目数")
    processed_items = Column(Integer, default=0, nullable=False, comment="已处理项目数")
    failed_items = Column(Integer, default=0, nullable=False, comment="失败项目数")
    celery_task_id = Column(String(255), nullable=True, comment="Celery任务ID")
    error_message = Column(Text, nullable=True, comment="错误信息")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 关系
    hospital = relationship("Hospital", back_populates="classification_tasks")
    model_version = relationship("ModelVersion", back_populates="classification_tasks")
    creator = relationship("User")
    plan = relationship("ClassificationPlan", back_populates="task", uselist=False, cascade="all, delete-orphan")
    progress_records = relationship("TaskProgress", back_populates="task", cascade="all, delete-orphan")
