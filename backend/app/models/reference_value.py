"""
参考价值模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class ReferenceValue(Base):
    """参考价值表"""
    __tablename__ = "reference_values"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True, comment="医疗机构ID")
    period = Column(String(7), nullable=False, index=True, comment="年月，格式：YYYY-MM")
    department_code = Column(String(50), nullable=False, index=True, comment="科室代码")
    department_name = Column(String(100), nullable=False, comment="科室名称")
    reference_value = Column(Numeric(18, 4), nullable=False, comment="参考总价值")
    doctor_reference_value = Column(Numeric(18, 4), nullable=True, comment="医生参考价值")
    nurse_reference_value = Column(Numeric(18, 4), nullable=True, comment="护理参考价值")
    tech_reference_value = Column(Numeric(18, 4), nullable=True, comment="医技参考价值")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联
    hospital = relationship("Hospital", backref="reference_values")
    
    # 唯一约束：同一医院、同一月份、同一科室只能有一条记录
    __table_args__ = (
        UniqueConstraint('hospital_id', 'period', 'department_code', name='uq_reference_value_hospital_period_dept'),
        {'comment': '参考价值表'}
    )
