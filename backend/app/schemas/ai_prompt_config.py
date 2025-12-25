"""
AI提示词配置相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AIPromptConfigBase(BaseModel):
    """AI提示词配置基础模型"""
    category: str = Field(..., description="提示词分类")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    user_prompt: str = Field(..., description="用户提示词模板", min_length=1)


class AIPromptConfigCreate(AIPromptConfigBase):
    """创建AI提示词配置"""
    pass


class AIPromptConfigUpdate(BaseModel):
    """更新AI提示词配置"""
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    user_prompt: Optional[str] = Field(None, description="用户提示词模板", min_length=1)


class AIPromptConfigResponse(AIPromptConfigBase):
    """AI提示词配置响应"""
    id: int
    hospital_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIPromptConfigListResponse(BaseModel):
    """AI提示词配置列表响应"""
    items: List[AIPromptConfigResponse]


class AIPromptCategoryInfo(BaseModel):
    """提示词分类信息"""
    category: str = Field(..., description="分类标识")
    name: str = Field(..., description="分类名称")
    description: str = Field(..., description="分类描述")
    placeholders: List[str] = Field(..., description="支持的占位符列表")


class AIPromptCategoriesResponse(BaseModel):
    """提示词分类列表响应"""
    categories: List[AIPromptCategoryInfo]


class ReportAIGenerateRequest(BaseModel):
    """报告AI生成请求"""
    report_id: int = Field(..., description="报告ID")
    category: str = Field(..., description="生成类型：report_issues 或 report_plans")


class ReportAIPreviewGenerateRequest(BaseModel):
    """报告AI预览生成请求（创建报告时使用）"""
    department_id: int = Field(..., description="科室ID")
    period: str = Field(..., description="统计周期，格式：YYYY-MM")
    task_id: str = Field(..., description="计算任务ID")
    category: str = Field(..., description="生成类型：report_issues 或 report_plans")


class ReportAIGenerateResponse(BaseModel):
    """报告AI生成响应"""
    success: bool = Field(..., description="是否成功")
    content: Optional[str] = Field(None, description="生成的内容（Markdown格式）")
    error: Optional[str] = Field(None, description="错误信息")
    duration: Optional[float] = Field(None, description="响应时间（秒）")
