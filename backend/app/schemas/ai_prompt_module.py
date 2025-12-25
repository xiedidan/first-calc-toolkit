"""
AI提示词模块配置相关的Pydantic模型 - 智能问数系统
支持按功能模块配置独立的提示词，优化不同场景的AI响应质量
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime


class AIPromptModuleUpdate(BaseModel):
    """更新提示词模块配置"""
    ai_interface_id: Optional[int] = Field(None, description="AI接口ID，设为null表示取消关联")
    temperature: Optional[float] = Field(None, description="模型温度", ge=0.0, le=2.0)
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    user_prompt: Optional[str] = Field(None, description="用户提示词", min_length=1)

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: Optional[float]) -> Optional[float]:
        """验证温度范围"""
        if v is not None and (v < 0.0 or v > 2.0):
            raise ValueError('温度必须在0.0到2.0之间')
        return v


class AIInterfaceInfo(BaseModel):
    """AI接口简要信息（用于模块响应中嵌套）"""
    id: int = Field(..., description="接口ID")
    name: str = Field(..., description="接口名称")
    model_name: str = Field(..., description="模型名称")
    is_active: bool = Field(..., description="是否启用")

    model_config = {"from_attributes": True}


class AIPromptModuleResponse(BaseModel):
    """提示词模块配置响应"""
    id: int = Field(..., description="模块ID")
    hospital_id: int = Field(..., description="医疗机构ID")
    module_code: str = Field(..., description="模块代码")
    module_name: str = Field(..., description="模块名称")
    description: Optional[str] = Field(None, description="模块描述")
    ai_interface_id: Optional[int] = Field(None, description="AI接口ID")
    ai_interface: Optional[AIInterfaceInfo] = Field(None, description="AI接口信息")
    temperature: float = Field(..., description="模型温度")
    placeholders: List[Any] = Field(default_factory=list, description="支持的占位符")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    user_prompt: str = Field(..., description="用户提示词")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    # 状态信息
    is_configured: bool = Field(False, description="是否已配置AI接口")

    model_config = {"from_attributes": True}


class AIPromptModuleListResponse(BaseModel):
    """提示词模块列表响应"""
    items: List[AIPromptModuleResponse] = Field(..., description="模块列表")
    total: int = Field(..., description="总数")
