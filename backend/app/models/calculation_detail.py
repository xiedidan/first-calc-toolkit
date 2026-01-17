"""
核算明细模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL
from app.database import Base


class CalculationDetail(Base):
    """核算明细表
    
    存储按(hospital_id, task_id, department_id, node_id, item_code)聚合的收费明细
    用于支持维度下钻功能，将统计逻辑从API层移到计算流程中
    
    注意：此表不使用外键约束，以便支持灵活的数据插入
    """
    __tablename__ = "calculation_details"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, nullable=False, index=True, comment="医疗机构ID")
    task_id = Column(String(100), nullable=False, index=True, comment="计算任务ID")
    department_id = Column(Integer, nullable=False, index=True, comment="科室ID")
    department_code = Column(String(50), nullable=False, comment="科室代码")
    
    # 维度信息
    node_id = Column(Integer, nullable=False, index=True, comment="维度节点ID")
    node_code = Column(String(100), nullable=False, comment="维度编码")
    node_name = Column(String(255), nullable=False, comment="维度名称")
    parent_id = Column(Integer, comment="父节点ID")
    
    # 收费项目信息
    item_code = Column(String(100), nullable=False, index=True, comment="收费项目编码")
    item_name = Column(String(200), comment="收费项目名称")
    item_category = Column(String(100), comment="项目类别")
    
    # 业务属性
    business_type = Column(String(20), comment="业务类型（门诊/住院）")
    
    # 数值
    amount = Column(DECIMAL(20, 4), nullable=False, default=0, comment="金额")
    quantity = Column(DECIMAL(20, 4), nullable=False, default=0, comment="数量")
    
    # 时间
    period = Column(String(7), nullable=False, comment="统计月份(YYYY-MM)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
