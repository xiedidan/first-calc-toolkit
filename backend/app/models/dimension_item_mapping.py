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
    dimension_id = Column(Integer, nullable=False, index=True, comment="维度节点ID")
    item_code = Column(String(100), nullable=False, index=True, comment="收费项目编码")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
