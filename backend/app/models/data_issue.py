"""
数据问题记录模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ProcessingStage(str, enum.Enum):
    """处理阶段枚举"""
    NOT_STARTED = "not_started"      # 待开始
    IN_PROGRESS = "in_progress"      # 进行中
    RESOLVED = "resolved"            # 已解决
    CONFIRMED = "confirmed"          # 已确认


class DataIssue(Base):
    """数据问题记录模型"""
    __tablename__ = "data_issues"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(200), nullable=False, comment="问题标题")
    description = Column(Text, nullable=False, comment="问题描述")
    reporter = Column(String(100), nullable=False, comment="记录人姓名")
    reporter_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="记录人用户ID")
    assignee = Column(String(100), nullable=True, comment="负责人姓名")
    assignee_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="负责人用户ID")
    processing_stage = Column(Enum(ProcessingStage, values_callable=lambda x: [e.value for e in x]), default=ProcessingStage.NOT_STARTED.value, nullable=False, index=True, comment="处理阶段")
    resolution = Column(Text, nullable=True, comment="解决方案")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属医疗机构ID")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="记录时间")
    resolved_at = Column(DateTime, nullable=True, comment="解决时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # Relationships
    reporter_user = relationship("User", foreign_keys=[reporter_user_id])
    assignee_user = relationship("User", foreign_keys=[assignee_user_id])
    hospital = relationship("Hospital", back_populates="data_issues")
