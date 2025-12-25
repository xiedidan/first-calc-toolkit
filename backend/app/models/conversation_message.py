"""
对话消息模型 - 智能问数系统
存储对话中的每条消息，包括用户消息和AI回复
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class MessageRole:
    """消息角色常量"""
    USER = "user"           # 用户消息
    ASSISTANT = "assistant" # AI回复


class ContentType:
    """内容类型常量"""
    TEXT = "text"           # 纯文本
    TABLE = "table"         # 表格数据
    CODE = "code"           # 代码块
    CHART = "chart"         # 图表
    ERROR = "error"         # 错误信息


class ConversationMessage(Base):
    """对话消息模型"""
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True, comment="对话ID")
    role = Column(String(20), nullable=False, comment="角色(user/assistant)")
    content = Column(Text, nullable=False, comment="消息内容")
    content_type = Column(String(50), nullable=False, default=ContentType.TEXT, comment="内容类型")
    message_metadata = Column(JSONB, nullable=True, comment="元数据(图表配置等)")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")

    # 关系
    conversation = relationship("Conversation", back_populates="messages")
