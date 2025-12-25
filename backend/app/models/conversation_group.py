"""
对话分组模型 - 智能问数系统
用于组织和管理多个相关对话的容器
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ConversationGroup(Base):
    """对话分组模型"""
    __tablename__ = "conversation_groups"

    id = Column(Integer, primary_key=True, index=True, comment="主键")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True, comment="医疗机构ID")
    name = Column(String(100), nullable=False, comment="分组名称")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序顺序")
    is_collapsed = Column(Boolean, default=False, nullable=False, comment="是否收起")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")

    # 关系
    hospital = relationship("Hospital", back_populates="conversation_groups")
    conversations = relationship("Conversation", back_populates="group")
