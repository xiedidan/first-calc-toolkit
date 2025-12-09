"""
成本基准模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class CostBenchmark(Base):
    """成本基准模型"""
    __tablename__ = "cost_benchmarks"
    __table_args__ = (
        UniqueConstraint(
            'hospital_id', 'department_code', 'version_id', 'dimension_code',
            name='uq_cost_benchmark_dept_version_dimension'
        ),
        {'comment': '成本基准表'},
    )

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属医疗机构ID"
    )
    department_code = Column(String(50), nullable=False, index=True, comment="科室代码")
    department_name = Column(String(100), nullable=False, comment="科室名称")
    version_id = Column(
        Integer,
        ForeignKey("model_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="模型版本ID"
    )
    version_name = Column(String(100), nullable=False, comment="模型版本名称")
    dimension_code = Column(String(100), nullable=False, index=True, comment="维度代码")
    dimension_name = Column(String(200), nullable=False, comment="维度名称")
    benchmark_value = Column(Numeric(15, 2), nullable=False, comment="基准值")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    hospital = relationship("Hospital", back_populates="cost_benchmarks")
    version = relationship("ModelVersion", back_populates="cost_benchmarks")
