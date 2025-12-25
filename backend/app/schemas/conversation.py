"""
对话相关的Pydantic模型 - 智能问数系统
用户与AI之间的一次完整交互会话
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


# 对话类型常量
CONVERSATION_TYPES = ["caliber", "data", "sql"]

# 对话类型显示名称映射
CONVERSATION_TYPE_DISPLAY = {
    "caliber": "指标口径查询",
    "data": "数据智能查询",
    "sql": "SQL代码编写"
}


class ConversationCreate(BaseModel):
    """创建对话"""
    title: str = Field(..., description="对话标题", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="对话描述", max_length=500)
    conversation_type: str = Field("caliber", description="对话类型：caliber(指标口径查询)、data(数据智能查询)、sql(SQL代码编写)")
    group_id: Optional[int] = Field(None, description="分组ID")

    @field_validator('conversation_type')
    @classmethod
    def validate_conversation_type(cls, v: str) -> str:
        """验证对话类型"""
        if v not in CONVERSATION_TYPES:
            raise ValueError(f'对话类型必须是以下之一: {", ".join(CONVERSATION_TYPES)}')
        return v


class ConversationUpdate(BaseModel):
    """更新对话"""
    title: Optional[str] = Field(None, description="对话标题", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="对话描述", max_length=500)
    conversation_type: Optional[str] = Field(None, description="对话类型")
    group_id: Optional[int] = Field(None, description="分组ID，设为null表示移至未分组")

    @field_validator('conversation_type')
    @classmethod
    def validate_conversation_type(cls, v: Optional[str]) -> Optional[str]:
        """验证对话类型"""
        if v is not None and v not in CONVERSATION_TYPES:
            raise ValueError(f'对话类型必须是以下之一: {", ".join(CONVERSATION_TYPES)}')
        return v


class ConversationResponse(BaseModel):
    """对话响应"""
    id: int = Field(..., description="对话ID")
    hospital_id: int = Field(..., description="医疗机构ID")
    group_id: Optional[int] = Field(None, description="分组ID")
    group_name: Optional[str] = Field(None, description="分组名称")
    title: str = Field(..., description="对话标题")
    description: Optional[str] = Field(None, description="对话描述")
    conversation_type: str = Field(..., description="对话类型")
    conversation_type_display: str = Field(..., description="对话类型显示名称")
    message_count: int = Field(0, description="消息数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    """对话列表响应"""
    items: List[ConversationResponse] = Field(..., description="对话列表")
    total: int = Field(..., description="总数")


class ConversationSearchRequest(BaseModel):
    """对话搜索请求"""
    keyword: Optional[str] = Field(None, description="搜索关键词（匹配标题或描述）")
    group_id: Optional[int] = Field(None, description="分组ID筛选，-1表示未分组")
    conversation_type: Optional[str] = Field(None, description="对话类型筛选")
    page: int = Field(1, description="页码", ge=1)
    size: int = Field(20, description="每页数量", ge=1, le=100)

    @field_validator('conversation_type')
    @classmethod
    def validate_conversation_type(cls, v: Optional[str]) -> Optional[str]:
        """验证对话类型"""
        if v is not None and v not in CONVERSATION_TYPES:
            raise ValueError(f'对话类型必须是以下之一: {", ".join(CONVERSATION_TYPES)}')
        return v


class ConversationMoveRequest(BaseModel):
    """移动对话到分组请求"""
    conversation_ids: List[int] = Field(..., description="对话ID列表", min_length=1)
    group_id: Optional[int] = Field(None, description="目标分组ID，null表示移至未分组")

