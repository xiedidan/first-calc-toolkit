"""
成本报表模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class CostReport(Base):
    """成本报表"""
    __tablename__ = "cost_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True, comment="医疗机构ID")
    period = Column(String(7), nullable=False, index=True, comment="年月，格式：YYYY-MM")
    department_code = Column(String(50), nullable=False, index=True, comment="科室代码")
    department_name = Column(String(100), nullable=False, comment="科室名称")
    personnel_cost = Column(Numeric(18, 4), nullable=False, default=0, comment="人员经费")
    material_cost = Column(Numeric(18, 4), nullable=False, default=0, comment="不收费卫生材料费")
    medicine_cost = Column(Numeric(18, 4), nullable=False, default=0, comment="不收费药品费")
    depreciation_cost = Column(Numeric(18, 4), nullable=False, default=0, comment="折旧风险费")
    other_cost = Column(Numeric(18, 4), nullable=False, default=0, comment="其他费用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联
    hospital = relationship("Hospital", backref="cost_reports")
    
    # 唯一约束：同一医院、同一月份、同一科室只能有一条记录
    __table_args__ = (
        UniqueConstraint('hospital_id', 'period', 'department_code', name='uq_cost_report_hospital_period_dept'),
        {'comment': '成本报表'}
    )
