"""
计算流程Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CalculationWorkflowBase(BaseModel):
    """计算流程基础Schema"""
    name: str = Field(..., description="流程名称", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="流程描述")
    is_active: bool = Field(True, description="是否启用")


class CalculationWorkflowCreate(CalculationWorkflowBase):
    """创建计算流程Schema"""
    version_id: int = Field(..., description="模型版本ID", gt=0)


class CalculationWorkflowUpdate(BaseModel):
    """更新计算流程Schema"""
    name: Optional[str] = Field(None, description="流程名称", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="流程描述")
    is_active: Optional[bool] = Field(None, description="是否启用")


class CalculationWorkflowResponse(CalculationWorkflowBase):
    """计算流程响应Schema"""
    id: int
    version_id: int
    version_name: Optional[str] = None
    step_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CalculationWorkflowListResponse(BaseModel):
    """计算流程列表响应Schema"""
    total: int
    items: list[CalculationWorkflowResponse]


class CalculationWorkflowCopyRequest(BaseModel):
    """复制计算流程请求Schema"""
    name: str = Field(..., description="新流程名称", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="新流程描述")


class CalculationWorkflowCopyResponse(BaseModel):
    """复制计算流程响应Schema"""
    id: int
    name: str
    step_count: int
