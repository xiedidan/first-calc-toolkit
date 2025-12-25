"""
AI接口配置模型 - 智能问数系统
支持多AI接口管理，按模块分配不同的AI服务
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class AIInterface(Base):
    """AI接口配置模型"""
    __tablename__ = "ai_interfaces"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    name = Column(String(100), nullable=False, comment="接口名称")
    api_endpoint = Column(String(500), nullable=False, comment="API端点")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    api_key_encrypted = Column(Text, nullable=False, comment="加密的API密钥")
    call_delay = Column(Float, default=1.0, nullable=False, comment="调用延迟（秒）")
    daily_limit = Column(Integer, default=10000, nullable=False, comment="每日调用限额")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 关系
    hospital = relationship("Hospital", back_populates="ai_interfaces")
    prompt_modules = relationship("AIPromptModule", back_populates="ai_interface")
