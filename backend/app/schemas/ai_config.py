"""
AI接口配置相关的Pydantic模型
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class AIConfigCreate(BaseModel):
    """创建或更新AI配置"""
    api_endpoint: str = Field(..., description="API访问端点", min_length=1, max_length=500)
    model_name: str = Field("deepseek-chat", description="AI模型名称", min_length=1, max_length=100)
    api_key: Optional[str] = Field(None, description="API密钥（明文），更新时留空表示不修改")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    prompt_template: str = Field(..., description="用户提示词模板", min_length=1)
    call_delay: float = Field(1.0, description="调用延迟（秒）", ge=0.1, le=10.0)
    daily_limit: int = Field(10000, description="每日调用限额", ge=1, le=100000)
    batch_size: int = Field(100, description="批次大小", ge=1, le=1000)

    @field_validator('api_endpoint')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """验证URL格式"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_pattern.match(v):
            raise ValueError('API端点必须是有效的URL格式')
        return v


class AIConfigUpdate(BaseModel):
    """更新AI配置"""
    api_endpoint: Optional[str] = Field(None, description="API访问端点", min_length=1, max_length=500)
    api_key: Optional[str] = Field(None, description="API密钥（明文）", min_length=1)
    prompt_template: Optional[str] = Field(None, description="提示词模板", min_length=1)
    call_delay: Optional[float] = Field(None, description="调用延迟（秒）", ge=0.1, le=10.0)
    daily_limit: Optional[int] = Field(None, description="每日调用限额", ge=1, le=100000)
    batch_size: Optional[int] = Field(None, description="批次大小", ge=1, le=1000)

    @field_validator('api_endpoint')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """验证URL格式"""
        if v is None:
            return v
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_pattern.match(v):
            raise ValueError('API端点必须是有效的URL格式')
        return v


class AIConfigResponse(BaseModel):
    """AI配置响应（密钥掩码）"""
    id: int
    hospital_id: int
    api_endpoint: str
    model_name: str = Field(..., description="AI模型名称")
    api_key_masked: str = Field(..., description="掩码后的API密钥")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    prompt_template: str
    call_delay: float
    daily_limit: int
    batch_size: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIConfigTest(BaseModel):
    """测试AI配置请求"""
    test_item_name: str = Field(..., description="测试项目名称", min_length=1, max_length=200)
    test_dimensions: Optional[list[dict]] = Field(
        None,
        description="测试维度列表，格式：[{id: int, name: str, path: str}]"
    )


class AIConfigTestResponse(BaseModel):
    """测试AI配置响应"""
    success: bool = Field(..., description="测试是否成功")
    dimension_id: Optional[int] = Field(None, description="AI建议的维度ID")
    confidence: Optional[float] = Field(None, description="确信度（0-1）")
    error_message: Optional[str] = Field(None, description="错误信息")
    response_time: Optional[float] = Field(None, description="响应时间（秒）")


class APIUsageStatsResponse(BaseModel):
    """API使用统计响应"""
    total_calls: int = Field(..., description="总调用次数")
    successful_calls: int = Field(..., description="成功调用次数")
    failed_calls: int = Field(..., description="失败调用次数")
    today_calls: int = Field(..., description="今日调用次数")
    daily_limit: int = Field(..., description="每日限额")
    avg_duration: float = Field(..., description="平均响应时间（秒）")
    estimated_cost: float = Field(..., description="预估成本（元）")
    period_days: int = Field(..., description="统计天数")
