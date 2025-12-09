"""业务导向调整明细模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class OrientationAdjustmentDetail(Base):
    """业务导向调整明细表 - 记录完整的调整计算过程"""
    __tablename__ = "orientation_adjustment_details"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(50), nullable=False, index=True, comment="计算任务ID")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    year_month = Column(String(7), nullable=False, index=True, comment="计算年月(格式: YYYY-MM)")
    
    # 科室信息
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False, index=True, comment="科室ID")
    department_code = Column(String(50), nullable=False, comment="科室代码")
    department_name = Column(String(100), nullable=False, comment="科室名称")
    
    # 维度信息
    node_id = Column(Integer, ForeignKey("model_nodes.id", ondelete="CASCADE"), nullable=False, index=True, comment="模型节点ID")
    node_code = Column(String(50), nullable=False, comment="维度代码")
    node_name = Column(String(200), nullable=False, comment="维度名称")
    
    # 导向规则信息
    orientation_rule_id = Column(Integer, ForeignKey("orientation_rules.id", ondelete="CASCADE"), nullable=False, index=True, comment="导向规则ID")
    orientation_rule_name = Column(String(100), nullable=False, comment="导向规则名称")
    orientation_type = Column(String(20), nullable=False, comment="导向类型: benchmark_ladder/fixed_benchmark")
    
    # 计算过程 - 输入值
    actual_value = Column(Numeric(15, 4), nullable=True, comment="导向实际值")
    benchmark_value = Column(Numeric(15, 4), nullable=True, comment="导向基准值")
    
    # 计算过程 - 中间结果
    orientation_ratio = Column(Numeric(10, 6), nullable=True, comment="导向比例 = 实际值/基准值")
    
    # 计算过程 - 阶梯匹配（仅基准阶梯型）
    ladder_id = Column(Integer, nullable=True, comment="匹配的阶梯ID")
    ladder_lower_limit = Column(Numeric(10, 6), nullable=True, comment="阶梯下限")
    ladder_upper_limit = Column(Numeric(10, 6), nullable=True, comment="阶梯上限")
    adjustment_intensity = Column(Numeric(10, 6), nullable=True, comment="调整力度/管控力度")
    
    # 计算过程 - 权重调整
    original_weight = Column(Numeric(15, 4), nullable=False, comment="原始权重（全院业务价值）")
    adjusted_weight = Column(Numeric(15, 4), nullable=True, comment="调整后权重 = 原始权重 × 调整力度")
    
    # 调整状态
    is_adjusted = Column(Boolean, nullable=False, default=False, comment="是否实际调整")
    adjustment_reason = Column(String(200), nullable=True, comment="未调整原因")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    hospital = relationship("Hospital", back_populates="orientation_adjustment_details")
    department = relationship("Department")
    node = relationship("ModelNode")
    orientation_rule = relationship("OrientationRule")

    def __repr__(self):
        return f"<OrientationAdjustmentDetail(task_id={self.task_id}, dept={self.department_name}, node={self.node_name}, adjusted={self.is_adjusted})>"
