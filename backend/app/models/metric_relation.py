"""
指标关联模型 - 智能问数系统
定义指标之间的关联关系，支持复合指标的计算和追溯
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class RelationType:
    """关联类型常量"""
    COMPONENT = "component"     # 组成关系（复合指标由原子指标组成）
    DERIVED = "derived"         # 派生关系
    RELATED = "related"         # 相关关系


class MetricRelation(Base):
    """指标关联模型"""
    __tablename__ = "metric_relations"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    source_metric_id = Column(Integer, ForeignKey("metrics.id", ondelete="CASCADE"), nullable=False, index=True, comment="源指标ID")
    target_metric_id = Column(Integer, ForeignKey("metrics.id", ondelete="CASCADE"), nullable=False, index=True, comment="目标指标ID")
    relation_type = Column(String(50), nullable=False, default=RelationType.COMPONENT, comment="关联类型")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")

    # 关系
    source_metric = relationship("Metric", foreign_keys=[source_metric_id], back_populates="source_relations")
    target_metric = relationship("Metric", foreign_keys=[target_metric_id], back_populates="target_relations")

    # 唯一约束：同一对指标只能有一种关联关系
    __table_args__ = (
        UniqueConstraint('source_metric_id', 'target_metric_id', name='uq_metric_relation_source_target'),
    )
