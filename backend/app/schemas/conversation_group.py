"""
对话分组相关的Pydantic模型 - 智能问数系统
用于组织和管理多个相关对话的容器
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ConversationGroupCreate(BaseModel):
    """创建对话分组"""
    name: str = Field(..., description="分组名称", min_length=1, max_length=100)
    sort_order: int = Field(0, description="排序顺序", ge=0)
    is_collapsed: bool = Field(False, description="是否收起")


class ConversationGroupUpdate(BaseModel):
    """更新对话分组"""
    name: Optional[str] = Field(None, description="分组名称", min_length=1, max_length=100)
    sort_order: Optional[int] = Field(None, description="排序顺序", ge=0)
    is_collapsed: Optional[bool] = Field(None, description="是否收起")


class ConversationGroupResponse(BaseModel):
    """对话分组响应"""
    id: int = Field(..., description="分组ID")
    hospital_id: int = Field(..., description="医疗机构ID")
    name: str = Field(..., description="分组名称")
    sort_order: int = Field(..., description="排序顺序")
    is_collapsed: bool = Field(..., description="是否收起")
    conversation_count: int = Field(0, description="对话数量")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}


class ConversationGroupListResponse(BaseModel):
    """对话分组列表响应"""
    items: List[ConversationGroupResponse] = Field(..., description="分组列表")
    total: int = Field(..., description="总数")


class ConversationGroupReorderRequest(BaseModel):
    """分组重排序请求"""
    group_ids: List[int] = Field(..., description="按新顺序排列的分组ID列表", min_length=1)


class ConversationGroupWithConversationsResponse(BaseModel):
    """带对话列表的分组响应（用于侧边栏展示）"""
    id: int = Field(..., description="分组ID")
    name: str = Field(..., description="分组名称")
    sort_order: int = Field(..., description="排序顺序")
    is_collapsed: bool = Field(..., description="是否收起")
    conversation_count: int = Field(0, description="对话数量")
    conversations: List["ConversationBriefResponse"] = Field(default_factory=list, description="对话列表")

    model_config = {"from_attributes": True}


class ConversationBriefResponse(BaseModel):
    """对话简要信息（用于侧边栏列表）"""
    id: int = Field(..., description="对话ID")
    title: str = Field(..., description="对话标题")
    conversation_type: str = Field(..., description="对话类型")
    conversation_type_display: str = Field(..., description="对话类型显示名称")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}


class SidebarResponse(BaseModel):
    """侧边栏响应（包含分组和未分组对话）"""
    groups: List[ConversationGroupWithConversationsResponse] = Field(..., description="分组列表（含对话）")
    ungrouped_conversations: List[ConversationBriefResponse] = Field(..., description="未分组的对话列表")
    total_conversations: int = Field(..., description="对话总数")

