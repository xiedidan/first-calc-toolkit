"""
分类预案模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PlanStatus(str, enum.Enum):
    """预案状态枚举"""
    draft = "draft"
    submitted = "submitted"


class ClassificationPlan(Base):
    """分类预案模型"""
    __tablename__ = "classification_plans"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    task_id = Column(Integer, ForeignKey("classification_tasks.id", ondelete="CASCADE"), nullable=False, unique=True, comment="分类任务ID")
    plan_name = Column(String(100), nullable=True, comment="预案名称")
    status = Column(SQLEnum(PlanStatus), default=PlanStatus.draft, nullable=False, comment="预案状态")
    submitted_at = Column(DateTime, nullable=True, comment="提交时间")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 关系
    hospital = relationship("Hospital", back_populates="classification_plans")
    task = relationship("ClassificationTask", back_populates="plan")
    items = relationship("PlanItem", back_populates="plan", cascade="all, delete-orphan")
