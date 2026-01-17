"""
维度分析模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class DimensionAnalysis(Base):
    """维度分析表
    
    存储用户对维度的分析文字，分为两类：
    - 当期分析：与医院、科室、月份、维度挂钩
    - 长期分析：与医院、科室、维度挂钩（period 为 NULL）
    
    两类分析都不和任务挂钩
    """
    __tablename__ = "dimension_analyses"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True, comment="医疗机构ID")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True, comment="科室ID")
    node_id = Column(Integer, ForeignKey("model_nodes.id"), nullable=False, index=True, comment="维度节点ID")
    
    # 月份：NULL 表示长期分析，非 NULL 表示当期分析
    period = Column(String(7), nullable=True, index=True, comment="统计月份(YYYY-MM)，NULL表示长期分析")
    
    # 分析内容
    content = Column(Text, nullable=False, comment="分析内容")
    
    # 审计字段
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建人ID")
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="更新人ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    hospital = relationship("Hospital", backref="dimension_analyses")
    department = relationship("Department", backref="dimension_analyses")
    node = relationship("ModelNode", backref="dimension_analyses")
    creator = relationship("User", foreign_keys=[created_by], backref="created_dimension_analyses")
    updater = relationship("User", foreign_keys=[updated_by], backref="updated_dimension_analyses")
    
    __table_args__ = (
        # 唯一约束：同一医院、科室、维度、月份只能有一条分析
        # 对于长期分析（period=NULL），使用 COALESCE 处理
        UniqueConstraint('hospital_id', 'department_id', 'node_id', 'period', 
                        name='uq_dimension_analysis_key'),
        {'comment': '维度分析表 - 存储用户对维度的分析文字'}
    )
