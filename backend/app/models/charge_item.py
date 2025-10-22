"""
收费项目模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class ChargeItem(Base):
    """收费项目模型 - 存储HIS系统的收费项目"""
    __tablename__ = "charge_items"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(100), unique=True, nullable=False, index=True, comment="收费项目编码")
    item_name = Column(String(255), nullable=False, index=True, comment="收费项目名称")  # 添加索引用于搜索
    item_category = Column(String(100), index=True, comment="收费项目分类")  # 添加索引用于筛选
    unit_price = Column(String(50), comment="单价")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
