"""
模型节点模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Numeric, Boolean, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base


class ModelNode(Base):
    """模型节点模型"""
    __tablename__ = "model_nodes"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False, index=True, comment="模型版本ID")
    parent_id = Column(Integer, ForeignKey("model_nodes.id", ondelete="CASCADE"), nullable=True, index=True, comment="父节点ID")
    sort_order = Column(Numeric(10, 2), default=0, nullable=False, index=True, comment="排序序号")
    name = Column(String(100), nullable=False, comment="节点名称")
    code = Column(String(50), nullable=False, comment="节点编码")
    node_type = Column(String(20), nullable=False, comment="节点类型(sequence/dimension)")
    is_leaf = Column(Boolean, default=False, nullable=False, comment="是否为末级维度")
    calc_type = Column(String(20), comment="算法类型(statistical=指标/calculational=目录)")
    weight = Column(Numeric(10, 4), comment="权重/单价")
    unit = Column(String(20), default='%', comment="单位")
    business_guide = Column(Text, comment="业务导向")
    script = Column(Text, comment="SQL/Python脚本")
    rule = Column(Text, comment="规则说明")
    orientation_rule_id = Column(Integer, ForeignKey("orientation_rules.id", ondelete="SET NULL"), nullable=True, comment="关联导向规则ID（已废弃，使用orientation_rule_ids）")
    orientation_rule_ids = Column(ARRAY(Integer), nullable=True, comment="关联导向规则ID列表")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    version = relationship("ModelVersion", back_populates="nodes")
    parent = relationship("ModelNode", remote_side=[id], back_populates="children")
    children = relationship("ModelNode", back_populates="parent", cascade="all, delete-orphan")
    orientation_rule = relationship("OrientationRule", back_populates="model_nodes")
