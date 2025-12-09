"""
导向规则模型
"""
from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class OrientationCategory(str, enum.Enum):
    """导向类别枚举"""
    benchmark_ladder = "benchmark_ladder"  # 基准阶梯
    direct_ladder = "direct_ladder"  # 直接阶梯
    other = "other"  # 其他


class OrientationRule(Base):
    """导向规则模型"""
    __tablename__ = "orientation_rules"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    name = Column(String(100), nullable=False, comment="导向名称")
    category = Column(
        Enum(OrientationCategory, name="orientation_category"),
        nullable=False,
        comment="导向类别"
    )
    description = Column(String(1024), nullable=True, comment="导向规则描述")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    hospital = relationship("Hospital", back_populates="orientation_rules")
    benchmarks = relationship("OrientationBenchmark", back_populates="rule", cascade="all, delete-orphan")
    ladders = relationship("OrientationLadder", back_populates="rule", cascade="all, delete-orphan")
    model_nodes = relationship("ModelNode", back_populates="orientation_rule")
    orientation_values = relationship("OrientationValue", back_populates="orientation_rule", cascade="all, delete-orphan")

    # 唯一约束
    __table_args__ = (
        # UniqueConstraint 已在迁移文件中定义
    )
