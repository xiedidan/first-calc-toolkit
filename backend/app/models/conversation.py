"""
对话模型 - 智能问数系统
用户与AI之间的一次完整交互会话
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ConversationType:
    """对话类型常量"""
    CALIBER = "caliber"      # 指标口径查询
    DATA = "data"            # 数据智能查询
    SQL = "sql"              # SQL代码编写


class Conversation(Base):
    """对话模型"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    group_id = Column(Integer, ForeignKey("conversation_groups.id", ondelete="SET NULL"), nullable=True, index=True, comment="分组ID")
    title = Column(String(200), nullable=False, comment="对话标题")
    description = Column(String(500), nullable=True, comment="对话描述")
    conversation_type = Column(String(50), nullable=False, default=ConversationType.CALIBER, comment="对话类型")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 关系
    hospital = relationship("Hospital", back_populates="conversations")
    group = relationship("ConversationGroup", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")
