"""
预案项目模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ProcessingStatus(str, enum.Enum):
    """处理状态枚举"""
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class PlanItem(Base):
    """预案项目模型"""
    __tablename__ = "plan_items"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    plan_id = Column(Integer, ForeignKey("classification_plans.id", ondelete="CASCADE"), nullable=False, index=True, comment="预案ID")
    charge_item_id = Column(Integer, ForeignKey("charge_items.id", ondelete="CASCADE"), nullable=False, comment="收费项目ID")
    charge_item_name = Column(String(200), nullable=False, comment="收费项目名称")
    ai_suggested_dimension_id = Column(Integer, ForeignKey("model_nodes.id", ondelete="SET NULL"), nullable=True, comment="AI建议维度ID")
    ai_confidence = Column(Numeric(5, 4), nullable=True, comment="AI确信度（0-1）")
    user_set_dimension_id = Column(Integer, ForeignKey("model_nodes.id", ondelete="SET NULL"), nullable=True, comment="用户设置维度ID")
    is_adjusted = Column(Boolean, default=False, nullable=False, comment="是否已调整")
    processing_status = Column(
        SQLEnum(ProcessingStatus, name='processing_status', create_type=False),
        default=ProcessingStatus.pending,
        nullable=False,
        comment="处理状态"
    )
    error_message = Column(Text, nullable=True, comment="错误信息")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 关系
    hospital = relationship("Hospital")
    plan = relationship("ClassificationPlan", back_populates="items")
    charge_item = relationship("ChargeItem")
    ai_suggested_dimension = relationship("ModelNode", foreign_keys=[ai_suggested_dimension_id])
    user_set_dimension = relationship("ModelNode", foreign_keys=[user_set_dimension_id])

    # 唯一约束：同一预案中每个收费项目只能出现一次
    __table_args__ = (
        UniqueConstraint('plan_id', 'charge_item_id', name='uq_plan_item'),
    )
