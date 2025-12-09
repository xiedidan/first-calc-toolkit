"""
导向基准模型
"""
from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class BenchmarkType(str, enum.Enum):
    """基准类别枚举"""
    average = "average"  # 平均值
    median = "median"  # 中位数
    max = "max"  # 最大值
    min = "min"  # 最小值
    other = "other"  # 其他


class OrientationBenchmark(Base):
    """导向基准模型"""
    __tablename__ = "orientation_benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    rule_id = Column(Integer, ForeignKey("orientation_rules.id", ondelete="CASCADE"), nullable=False, index=True, comment="导向规则ID")
    department_code = Column(String(50), nullable=False, comment="科室代码")
    department_name = Column(String(100), nullable=False, comment="科室名称")
    benchmark_type = Column(
        Enum(BenchmarkType, name="benchmark_type"),
        nullable=False,
        comment="基准类别"
    )
    control_intensity = Column(Numeric(10, 4), nullable=False, comment="管控力度")
    stat_start_date = Column(DateTime, nullable=False, comment="统计开始时间")
    stat_end_date = Column(DateTime, nullable=False, comment="统计结束时间")
    benchmark_value = Column(Numeric(10, 4), nullable=False, comment="基准值")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    hospital = relationship("Hospital", back_populates="orientation_benchmarks")
    rule = relationship("OrientationRule", back_populates="benchmarks")

    # 唯一约束
    __table_args__ = (
        # UniqueConstraint 已在迁移文件中定义
    )
