"""
指标模型 - 智能问数系统
具有业务含义的数据度量单位
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class MetricType:
    """指标类型常量"""
    ATOMIC = "atomic"           # 原子指标
    COMPOSITE = "composite"     # 复合指标


class Metric(Base):
    """指标模型"""
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    topic_id = Column(Integer, ForeignKey("metric_topics.id", ondelete="CASCADE"), nullable=False, index=True, comment="主题ID")
    name_cn = Column(String(200), nullable=False, comment="中文名称")
    name_en = Column(String(200), nullable=True, comment="英文名称")
    metric_type = Column(String(50), nullable=False, default=MetricType.ATOMIC, comment="指标类型")
    metric_level = Column(String(100), nullable=True, comment="指标层级")
    business_caliber = Column(Text, nullable=True, comment="业务口径")
    technical_caliber = Column(Text, nullable=True, comment="技术口径")
    source_tables = Column(JSONB, nullable=True, comment="源表列表")
    dimension_tables = Column(JSONB, nullable=True, comment="关联维表")
    dimensions = Column(JSONB, nullable=True, comment="指标维度")
    data_source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True, index=True, comment="数据源ID")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序顺序")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 关系
    topic = relationship("MetricTopic", back_populates="metrics")
    data_source = relationship("DataSource", back_populates="metrics")
    # 指标关联关系 - 作为源指标
    source_relations = relationship("MetricRelation", foreign_keys="MetricRelation.source_metric_id", back_populates="source_metric", cascade="all, delete-orphan")
    # 指标关联关系 - 作为目标指标
    target_relations = relationship("MetricRelation", foreign_keys="MetricRelation.target_metric_id", back_populates="target_metric", cascade="all, delete-orphan")
