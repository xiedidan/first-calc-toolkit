"""
AI接口配置相关的Pydantic模型 - 智能问数系统
支持多AI接口管理，按模块分配不同的AI服务
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


class AIInterfaceCreate(BaseModel):
    """创建AI接口配置"""
    name: str = Field(..., description="接口名称", min_length=1, max_length=100)
    api_endpoint: str = Field(..., description="API端点", min_length=1, max_length=500)
    model_name: str = Field(..., description="模型名称", min_length=1, max_length=100)
    api_key: str = Field(..., description="API密钥（明文）", min_length=1)
    call_delay: float = Field(1.0, description="调用延迟（秒）", ge=0.1, le=10.0)
    daily_limit: int = Field(10000, description="每日调用限额", ge=1, le=100000)
    is_active: bool = Field(True, description="是否启用")

    @field_validator('api_endpoint')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """验证URL格式"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_pattern.match(v):
            raise ValueError('API端点必须是有效的URL格式')
        return v


class AIInterfaceUpdate(BaseModel):
    """更新AI接口配置"""
    name: Optional[str] = Field(None, description="接口名称", min_length=1, max_length=100)
    api_endpoint: Optional[str] = Field(None, description="API端点", min_length=1, max_length=500)
    model_name: Optional[str] = Field(None, description="模型名称", min_length=1, max_length=100)
    api_key: Optional[str] = Field(None, description="API密钥（明文），留空表示不修改")
    call_delay: Optional[float] = Field(None, description="调用延迟（秒）", ge=0.1, le=10.0)
    daily_limit: Optional[int] = Field(None, description="每日调用限额", ge=1, le=100000)
    is_active: Optional[bool] = Field(None, description="是否启用")

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



class AIInterfaceResponse(BaseModel):
    """AI接口配置响应（密钥掩码）"""
    id: int = Field(..., description="接口ID")
    hospital_id: int = Field(..., description="医疗机构ID")
    name: str = Field(..., description="接口名称")
    api_endpoint: str = Field(..., description="API端点")
    model_name: str = Field(..., description="模型名称")
    api_key_masked: str = Field(..., description="掩码后的API密钥")
    call_delay: float = Field(..., description="调用延迟（秒）")
    daily_limit: int = Field(..., description="每日调用限额")
    is_active: bool = Field(..., description="是否启用")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    # 关联信息
    referenced_modules: List[str] = Field(default_factory=list, description="引用此接口的模块列表")

    model_config = {"from_attributes": True}


class AIInterfaceListResponse(BaseModel):
    """AI接口列表响应"""
    items: List[AIInterfaceResponse] = Field(..., description="接口列表")
    total: int = Field(..., description="总数")


class AIInterfaceTestRequest(BaseModel):
    """测试AI接口请求"""
    test_message: str = Field(
        default="你好，请简单介绍一下你自己。",
        description="测试消息",
        min_length=1,
        max_length=500
    )


class AIInterfaceTestConfigRequest(BaseModel):
    """使用自定义配置测试AI接口请求（用于保存前测试）"""
    api_endpoint: str = Field(..., description="API端点", min_length=1, max_length=500)
    model_name: str = Field(..., description="模型名称", min_length=1, max_length=100)
    api_key: Optional[str] = Field(None, description="API密钥（明文），留空时需提供interface_id从数据库获取")
    interface_id: Optional[int] = Field(None, description="现有接口ID，用于获取已保存的密钥")
    test_message: str = Field(
        default="你好，请简单介绍一下你自己。",
        description="测试消息",
        min_length=1,
        max_length=500
    )


class AIInterfaceTestResponse(BaseModel):
    """测试AI接口响应"""
    success: bool = Field(..., description="测试是否成功")
    response_content: Optional[str] = Field(None, description="AI响应内容")
    response_time: Optional[float] = Field(None, description="响应时间（秒）")
    error_message: Optional[str] = Field(None, description="错误信息")
