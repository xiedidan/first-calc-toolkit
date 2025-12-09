"""
AI接口配置模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class AIConfig(Base):
    """AI接口配置模型"""
    __tablename__ = "ai_configs"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    api_endpoint = Column(String(500), nullable=False, comment="API访问端点")
    model_name = Column(String(100), default="deepseek-chat", nullable=False, comment="AI模型名称")
    api_key_encrypted = Column(Text, nullable=False, comment="加密的API密钥")
    system_prompt = Column(Text, nullable=True, comment="系统提示词")
    prompt_template = Column(Text, nullable=False, comment="用户提示词模板")
    call_delay = Column(Float, default=1.0, nullable=False, comment="调用延迟（秒）")
    daily_limit = Column(Integer, default=10000, nullable=False, comment="每日调用限额")
    batch_size = Column(Integer, default=100, nullable=False, comment="批次大小")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 关系
    hospital = relationship("Hospital", back_populates="ai_configs")

    # 唯一约束：每个医疗机构只有一个AI配置
    __table_args__ = (
        UniqueConstraint('hospital_id', name='uq_ai_config_hospital'),
    )
