"""
指标项目模型 - 智能问数系统
指标树的根节点，用于组织指标
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class MetricProject(Base):
    """指标项目模型"""
    __tablename__ = "metric_projects"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    name = Column(String(100), nullable=False, comment="项目名称")
    description = Column(String(500), nullable=True, comment="项目描述")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序顺序")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 关系
    hospital = relationship("Hospital", back_populates="metric_projects")
    topics = relationship("MetricTopic", back_populates="project", cascade="all, delete-orphan")
