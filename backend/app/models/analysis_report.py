"""
科室运营分析报告模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.database import Base


class AnalysisReport(Base):
    """科室运营分析报告模型"""
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(
        Integer, 
        ForeignKey("hospitals.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True, 
        comment="所属医疗机构ID"
    )
    department_id = Column(
        Integer, 
        ForeignKey("departments.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True, 
        comment="科室ID"
    )
    period = Column(String(20), nullable=False, index=True, comment="年月 (YYYY-MM格式)")
    current_issues = Column(Text, comment="当前存在问题 (Markdown格式，最大2000字符)")
    future_plans = Column(Text, comment="未来发展计划 (Markdown格式，最大2000字符)")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True, 
        comment="创建人ID"
    )
    task_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="关联的计算任务ID，用于获取计算结果数据"
    )

    # 唯一约束：同一医疗机构、同一科室、同一年月只能有一条报告
    __table_args__ = (
        UniqueConstraint('hospital_id', 'department_id', 'period', name='uq_analysis_report_hospital_dept_period'),
        Index('ix_analysis_reports_hospital_period', 'hospital_id', 'period'),
    )

    # 关系
    hospital = relationship("Hospital", back_populates="analysis_reports")
    department = relationship("Department", back_populates="analysis_reports")
    creator = relationship("User", backref="created_analysis_reports")
