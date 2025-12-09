"""成本值模型"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class CostValue(Base):
    """成本值表"""
    __tablename__ = "cost_values"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True)
    year_month = Column(String(7), nullable=False, index=True, comment="年月，格式：YYYY-MM")
    dept_code = Column(String(50), nullable=False, index=True, comment="科室代码")
    dept_name = Column(String(200), nullable=False, comment="科室名称")
    dimension_code = Column(String(50), nullable=False, index=True, comment="维度代码")
    dimension_name = Column(String(200), nullable=False, comment="维度名称")
    cost_value = Column(Numeric(15, 2), nullable=False, comment="成本值")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # 关系
    hospital = relationship("Hospital", back_populates="cost_values")

    def __repr__(self):
        return f"<CostValue(id={self.id}, hospital_id={self.hospital_id}, year_month={self.year_month}, dept={self.dept_name}, dimension={self.dimension_name}, cost={self.cost_value})>"
