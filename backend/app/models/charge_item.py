"""
收费项目模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class ChargeItem(Base):
    """收费项目模型 - 存储HIS系统的收费项目"""
    __tablename__ = "charge_items"
    __table_args__ = (
        UniqueConstraint('hospital_id', 'item_code', name='uq_hospital_item_code'),
    )

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属医疗机构ID")
    item_code = Column(String(100), nullable=False, index=True, comment="收费项目编码")
    item_name = Column(String(255), nullable=False, index=True, comment="收费项目名称")  # 添加索引用于搜索
    item_category = Column(String(100), index=True, comment="收费项目分类")  # 添加索引用于筛选
    unit_price = Column(String(50), comment="单价")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    hospital = relationship("Hospital", back_populates="charge_items")
