"""
计算任务模型
"""
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class CalculationTask(Base):
    """计算任务表"""
    __tablename__ = "calculation_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, index=True, nullable=False, comment="任务ID")
    model_version_id = Column(Integer, ForeignKey("model_versions.id"), nullable=False, comment="模型版本ID")
    workflow_id = Column(Integer, ForeignKey("calculation_workflows.id"), nullable=True, comment="计算流程ID")
    period = Column(String(20), nullable=False, comment="计算周期(YYYY-MM)")
    status = Column(String(20), nullable=False, default="pending", comment="任务状态")
    progress = Column(DECIMAL(5, 2), default=0, comment="进度百分比")
    description = Column(Text, comment="任务描述")
    error_message = Column(Text, comment="错误信息")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    started_at = Column(DateTime, comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")

    # 关系
    model_version = relationship("ModelVersion", back_populates="calculation_tasks")
    workflow = relationship("CalculationWorkflow", back_populates="calculation_tasks")
    # 注意：results 不使用 relationship，因为没有外键约束
    # 如需查询结果，请使用: db.query(CalculationResult).filter(CalculationResult.task_id == task.task_id)
    step_logs = relationship("CalculationStepLog", back_populates="task", cascade="all, delete-orphan")


class CalculationResult(Base):
    """计算结果明细表
    
    注意：此表不使用外键约束，以便支持灵活的数据插入和历史数据保留
    不定义 relationship，查询时直接使用 task_id 字段
    """
    __tablename__ = "calculation_results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), nullable=False, comment="任务ID", index=True)
    department_id = Column(Integer, nullable=False, comment="科室ID", index=True)
    node_id = Column(Integer, nullable=False, comment="节点ID")
    node_name = Column(String(255), nullable=False, comment="节点名称")
    node_code = Column(String(100), comment="节点编码")
    node_type = Column(String(50), comment="节点类型")
    parent_id = Column(Integer, comment="父节点ID")
    workload = Column(DECIMAL(20, 4), comment="工作量")
    weight = Column(DECIMAL(10, 4), comment="权重/单价")
    value = Column(DECIMAL(20, 4), comment="价值")
    ratio = Column(DECIMAL(10, 4), comment="占比")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class CalculationSummary(Base):
    """计算结果汇总表
    
    注意：此表不使用外键约束，以便支持灵活的数据插入和历史数据保留
    使用唯一约束 (task_id, department_id) 以支持 ON CONFLICT 更新
    不定义 relationship，查询时直接使用 task_id 和 department_id 字段
    """
    __tablename__ = "calculation_summaries"
    __table_args__ = (
        sa.UniqueConstraint('task_id', 'department_id', name='uq_calculation_summaries_task_dept'),
    )

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), nullable=False, comment="任务ID", index=True)
    department_id = Column(Integer, nullable=False, comment="科室ID", index=True)
    doctor_value = Column(DECIMAL(20, 4), default=0, comment="医生价值")
    doctor_ratio = Column(DECIMAL(10, 4), default=0, comment="医生占比")
    nurse_value = Column(DECIMAL(20, 4), default=0, comment="护理价值")
    nurse_ratio = Column(DECIMAL(10, 4), default=0, comment="护理占比")
    tech_value = Column(DECIMAL(20, 4), default=0, comment="医技价值")
    tech_ratio = Column(DECIMAL(10, 4), default=0, comment="医技占比")
    total_value = Column(DECIMAL(20, 4), default=0, comment="科室总价值")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
