"""
AI提示词配置模型（按分类）
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class AIPromptCategory:
    """AI提示词分类常量"""
    CLASSIFICATION = "classification"  # 智能分类分级
    REPORT_ISSUES = "report_issues"    # 业务价值报表-当前存在问题
    REPORT_PLANS = "report_plans"      # 业务价值报表-未来发展计划


class AIPromptConfig(Base):
    """AI提示词配置模型（按分类）"""
    __tablename__ = "ai_prompt_configs"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    category = Column(String(50), nullable=False, index=True, comment="提示词分类")
    system_prompt = Column(Text, nullable=True, comment="系统提示词")
    user_prompt = Column(Text, nullable=False, comment="用户提示词模板")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 关系
    hospital = relationship("Hospital", back_populates="ai_prompt_configs")

    # 唯一约束：每个医疗机构每个分类只有一个配置
    __table_args__ = (
        UniqueConstraint('hospital_id', 'category', name='uq_ai_prompt_config_hospital_category'),
    )
