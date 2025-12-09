"""
导向阶梯模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class OrientationLadder(Base):
    """导向阶梯模型"""
    __tablename__ = "orientation_ladders"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    rule_id = Column(Integer, ForeignKey("orientation_rules.id", ondelete="CASCADE"), nullable=False, index=True, comment="导向规则ID")
    ladder_order = Column(Integer, nullable=False, comment="阶梯次序")
    upper_limit = Column(Numeric(10, 4), nullable=True, comment="阶梯上限（NULL表示正无穷）")
    lower_limit = Column(Numeric(10, 4), nullable=True, comment="阶梯下限（NULL表示负无穷）")
    adjustment_intensity = Column(Numeric(10, 4), nullable=False, comment="调整力度")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    hospital = relationship("Hospital", back_populates="orientation_ladders")
    rule = relationship("OrientationRule", back_populates="ladders")

    # 唯一约束
    __table_args__ = (
        # UniqueConstraint 已在迁移文件中定义
    )
