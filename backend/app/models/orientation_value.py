"""
业务导向实际值模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class OrientationValue(Base):
    """业务导向实际值模型"""
    __tablename__ = "orientation_values"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    year_month = Column(String(7), nullable=False, comment="年月(格式: YYYY-MM)")
    department_code = Column(String(50), nullable=False, comment="科室代码")
    department_name = Column(String(100), nullable=False, comment="科室名称")
    orientation_rule_id = Column(Integer, ForeignKey("orientation_rules.id", ondelete="CASCADE"), nullable=False, index=True, comment="导向规则ID")
    actual_value = Column(Numeric(15, 4), nullable=False, comment="导向实际取值")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    hospital = relationship("Hospital", back_populates="orientation_values")
    orientation_rule = relationship("OrientationRule", back_populates="orientation_values")

    # 唯一约束: 同一医院、同一年月、同一科室、同一导向规则只能有一条记录
    __table_args__ = (
        # UniqueConstraint 将在迁移文件中定义
    )
