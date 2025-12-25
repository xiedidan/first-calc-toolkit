"""
AI提示词模块模型 - 智能问数系统
按功能模块配置独立的提示词，支持不同场景的AI响应优化
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class PromptModuleCode:
    """提示词模块代码常量"""
    # 智能分类分级
    CLASSIFICATION = "classification"
    
    # 业务价值报表
    REPORT_ISSUES = "report_issues"
    REPORT_PLANS = "report_plans"
    
    # 智能问数系统
    QUERY_CALIBER = "query_caliber"      # 指标口径查询
    QUERY_KEYWORD = "query_keyword"      # 指标关键字提取
    QUERY_DATA = "query_data"            # 查询数据生成
    QUERY_SQL = "query_sql"              # SQL代码编写


class AIPromptModule(Base):
    """AI提示词模块模型"""
    __tablename__ = "ai_prompt_modules"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    module_code = Column(String(100), nullable=False, comment="模块代码")
    module_name = Column(String(200), nullable=False, comment="模块名称")
    description = Column(Text, nullable=True, comment="模块描述")
    ai_interface_id = Column(Integer, ForeignKey("ai_interfaces.id", ondelete="SET NULL"), nullable=True, index=True, comment="AI接口ID")
    temperature = Column(Float, default=0.7, nullable=False, comment="模型温度")
    placeholders = Column(JSONB, nullable=False, default=list, comment="支持的占位符")
    system_prompt = Column(Text, nullable=True, comment="系统提示词")
    user_prompt = Column(Text, nullable=False, comment="用户提示词")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 关系
    hospital = relationship("Hospital", back_populates="ai_prompt_modules")
    ai_interface = relationship("AIInterface", back_populates="prompt_modules")

    # 唯一约束：每个医疗机构的模块代码唯一
    __table_args__ = (
        UniqueConstraint('hospital_id', 'module_code', name='uq_ai_prompt_module_hospital_code'),
    )
