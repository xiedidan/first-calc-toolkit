"""
对话消息相关的Pydantic模型 - 智能问数系统
存储对话中的每条消息，包括用户消息和AI回复
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Dict
from datetime import datetime


# 消息角色常量
MESSAGE_ROLES = ["user", "assistant"]

# 内容类型常量
CONTENT_TYPES = ["text", "table", "code", "chart", "error"]

# 内容类型显示名称映射
CONTENT_TYPE_DISPLAY = {
    "text": "文本",
    "table": "表格",
    "code": "代码",
    "chart": "图表",
    "error": "错误"
}


class ConversationMessageCreate(BaseModel):
    """创建对话消息（用户发送消息）"""
    content: str = Field(..., description="消息内容", min_length=1)
    content_type: str = Field("text", description="内容类型：text(文本)、table(表格)、code(代码)、chart(图表)、error(错误)")

    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        """验证内容类型"""
        if v not in CONTENT_TYPES:
            raise ValueError(f'内容类型必须是以下之一: {", ".join(CONTENT_TYPES)}')
        return v


class ConversationMessageResponse(BaseModel):
    """对话消息响应"""
    id: int = Field(..., description="消息ID")
    conversation_id: int = Field(..., description="对话ID")
    role: str = Field(..., description="角色：user(用户)、assistant(AI)")
    content: str = Field(..., description="消息内容")
    content_type: str = Field(..., description="内容类型")
    content_type_display: str = Field(..., description="内容类型显示名称")
    message_metadata: Optional[Dict[str, Any]] = Field(None, description="元数据（图表配置、表格数据等）")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}


class ConversationMessageListResponse(BaseModel):
    """对话消息列表响应"""
    items: List[ConversationMessageResponse] = Field(..., description="消息列表")
    total: int = Field(..., description="总数")


class ConversationDetailResponse(BaseModel):
    """对话详情响应（包含消息历史）"""
    id: int = Field(..., description="对话ID")
    hospital_id: int = Field(..., description="医疗机构ID")
    group_id: Optional[int] = Field(None, description="分组ID")
    group_name: Optional[str] = Field(None, description="分组名称")
    title: str = Field(..., description="对话标题")
    description: Optional[str] = Field(None, description="对话描述")
    conversation_type: str = Field(..., description="对话类型")
    conversation_type_display: str = Field(..., description="对话类型显示名称")
    messages: List[ConversationMessageResponse] = Field(default_factory=list, description="消息列表")
    message_count: int = Field(0, description="消息数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    content: str = Field(..., description="消息内容", min_length=1)


class SendMessageResponse(BaseModel):
    """发送消息响应（包含用户消息和AI回复）"""
    user_message: ConversationMessageResponse = Field(..., description="用户消息")
    assistant_message: ConversationMessageResponse = Field(..., description="AI回复")


class MessageExportRequest(BaseModel):
    """消息导出请求"""
    format: str = Field(..., description="导出格式：markdown、pdf、excel、csv")
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        """验证导出格式"""
        valid_formats = ["markdown", "pdf", "excel", "csv"]
        if v not in valid_formats:
            raise ValueError(f'导出格式必须是以下之一: {", ".join(valid_formats)}')
        return v


class ChartConfig(BaseModel):
    """图表配置（用于message_metadata）"""
    chart_type: str = Field(..., description="图表类型：line(折线图)、bar(柱状图)、pie(饼图)")
    title: Optional[str] = Field(None, description="图表标题")
    x_axis: Optional[str] = Field(None, description="X轴字段")
    y_axis: Optional[str] = Field(None, description="Y轴字段")
    series: Optional[List[str]] = Field(None, description="系列字段列表")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="图表数据")


class TableData(BaseModel):
    """表格数据（用于message_metadata）"""
    columns: List[str] = Field(..., description="列名列表")
    rows: List[List[Any]] = Field(..., description="行数据列表")
    total_rows: Optional[int] = Field(None, description="总行数（用于分页）")


class CodeBlock(BaseModel):
    """代码块（用于message_metadata）"""
    language: str = Field("sql", description="代码语言")
    code: str = Field(..., description="代码内容")

