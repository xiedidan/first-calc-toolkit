"""
计算步骤Schema
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class CalculationStepBase(BaseModel):
    """计算步骤基础Schema"""
    name: str = Field(..., description="步骤名称", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="步骤描述")
    code_type: str = Field(..., description="代码类型(python/sql)")
    code_content: str = Field(..., description="代码内容", min_length=1)
    data_source_id: Optional[int] = Field(None, description="数据源ID（SQL步骤使用）")
    python_env: Optional[str] = Field(None, description="Python虚拟环境路径（Python步骤使用）", max_length=200)
    is_enabled: bool = Field(True, description="是否启用")


class CalculationStepCreate(CalculationStepBase):
    """创建计算步骤Schema"""
    workflow_id: int = Field(..., description="计算流程ID", gt=0)
    sort_order: Optional[Decimal] = Field(None, description="执行顺序")


class CalculationStepUpdate(BaseModel):
    """更新计算步骤Schema"""
    name: Optional[str] = Field(None, description="步骤名称", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="步骤描述")
    code_type: Optional[str] = Field(None, description="代码类型(python/sql)")
    code_content: Optional[str] = Field(None, description="代码内容", min_length=1)
    data_source_id: Optional[int] = Field(None, description="数据源ID（SQL步骤使用）")
    python_env: Optional[str] = Field(None, description="Python虚拟环境路径（Python步骤使用）", max_length=200)
    is_enabled: Optional[bool] = Field(None, description="是否启用")


class CalculationStepResponse(CalculationStepBase):
    """计算步骤响应Schema"""
    id: int
    workflow_id: int
    workflow_name: Optional[str] = None
    data_source_name: Optional[str] = None
    sort_order: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CalculationStepListResponse(BaseModel):
    """计算步骤列表响应Schema"""
    total: int
    items: list[CalculationStepResponse]


class CalculationStepMoveResponse(BaseModel):
    """移动计算步骤响应Schema"""
    success: bool
    message: str


class TestCodeRequest(BaseModel):
    """测试代码请求Schema"""
    code_type: Optional[str] = Field(None, description="代码类型(python/sql)")
    code_content: Optional[str] = Field(None, description="代码内容")
    data_source_id: Optional[int] = Field(None, description="数据源ID（SQL代码使用）")
    test_params: Optional[dict] = Field(None, description="测试参数")


class TestCodeResponse(BaseModel):
    """测试代码响应Schema"""
    success: bool
    duration_ms: Optional[int] = None
    result: Optional[dict] = None
    error: Optional[str] = None
