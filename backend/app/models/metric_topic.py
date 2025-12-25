"""
指标主题模型 - 智能问数系统
项目下的一级分类，用于归类指标
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class MetricTopic(Base):
    """指标主题模型"""
    __tablename__ = "metric_topics"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    project_id = Column(Integer, ForeignKey("metric_projects.id", ondelete="CASCADE"), nullable=False, index=True, comment="项目ID")
    name = Column(String(100), nullable=False, comment="主题名称")
    description = Column(String(500), nullable=True, comment="主题描述")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序顺序")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 关系
    project = relationship("MetricProject", back_populates="topics")
    metrics = relationship("Metric", back_populates="topic", cascade="all, delete-orphan")
