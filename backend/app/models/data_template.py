"""
数据模板模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class DataTemplate(Base):
    """数据模板模型 - 存储医院需要提供的原始数据表模板"""
    __tablename__ = "data_templates"
    __table_args__ = (
        UniqueConstraint('hospital_id', 'table_name', name='uq_hospital_table_name'),
    )

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属医疗机构ID")
    table_name = Column(String(100), nullable=False, index=True, comment="表名")
    table_name_cn = Column(String(200), nullable=False, comment="中文名")
    description = Column(Text, comment="表说明")
    is_core = Column(Boolean, default=False, nullable=False, index=True, comment="是否核心表")
    sort_order = Column(Numeric(10, 2), nullable=False, comment="排序序号")
    definition_file_path = Column(Text, comment="表定义文档存储路径")
    definition_file_name = Column(String(255), comment="表定义文档原始文件名")
    sql_file_path = Column(Text, comment="SQL建表代码存储路径")
    sql_file_name = Column(String(255), comment="SQL建表代码原始文件名")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    hospital = relationship("Hospital", back_populates="data_templates")
