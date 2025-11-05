"""
维度-收费项目映射模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class DimensionItemMapping(Base):
    """维度-收费项目映射模型"""
    __tablename__ = "dimension_item_mappings"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属医疗机构ID")
    dimension_code = Column(String(100), nullable=False, index=True, comment="维度节点编码")
    item_code = Column(String(100), nullable=False, index=True, comment="收费项目编码")
    charge_item_id = Column(Integer, ForeignKey("charge_items.id", ondelete="CASCADE"), nullable=True, index=True, comment="收费项目ID")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    charge_item = relationship("ChargeItem", backref="dimension_mappings")
