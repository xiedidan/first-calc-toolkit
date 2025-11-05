"""
科室模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Department(Base):
    """科室模型"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属医疗机构ID")
    sort_order = Column(Numeric(10, 2), default=0, nullable=False, index=True, comment="排序序号")
    his_code = Column(String(50), nullable=False, index=True, comment="HIS科室代码")
    his_name = Column(String(100), nullable=False, comment="HIS科室名称")
    cost_center_code = Column(String(50), comment="成本中心代码")
    cost_center_name = Column(String(100), comment="成本中心名称")
    accounting_unit_code = Column(String(50), comment="核算单元代码")
    accounting_unit_name = Column(String(100), comment="核算单元名称")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否参与评估")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    hospital = relationship("Hospital", back_populates="departments")
