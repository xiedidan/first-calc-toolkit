"""
模型版本Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ModelVersionBase(BaseModel):
    """模型版本基础Schema"""
    version: str = Field(..., description="版本号")
    name: str = Field(..., description="版本名称")
    description: Optional[str] = Field(None, description="版本描述")


class ModelVersionCreate(ModelVersionBase):
    """创建模型版本Schema"""
    base_version_id: Optional[int] = Field(None, description="基础版本ID（用于复制）")


class ModelVersionUpdate(BaseModel):
    """更新模型版本Schema"""
    name: Optional[str] = Field(None, description="版本名称")
    description: Optional[str] = Field(None, description="版本描述")


class ModelVersionResponse(ModelVersionBase):
    """模型版本响应Schema"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelVersionListResponse(BaseModel):
    """模型版本列表响应Schema"""
    total: int
    items: list[ModelVersionResponse]
