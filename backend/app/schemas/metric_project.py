"""
指标项目相关的Pydantic模型 - 智能问数系统
指标树的根节点，用于组织指标
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MetricProjectCreate(BaseModel):
    """创建指标项目"""
    name: str = Field(..., description="项目名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="项目描述", max_length=500)
    sort_order: int = Field(0, description="排序顺序", ge=0)


class MetricProjectUpdate(BaseModel):
    """更新指标项目"""
    name: Optional[str] = Field(None, description="项目名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="项目描述", max_length=500)
    sort_order: Optional[int] = Field(None, description="排序顺序", ge=0)


class MetricProjectResponse(BaseModel):
    """指标项目响应"""
    id: int = Field(..., description="项目ID")
    hospital_id: int = Field(..., description="医疗机构ID")
    name: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    sort_order: int = Field(..., description="排序顺序")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    # 统计信息
    topic_count: int = Field(0, description="主题数量")
    metric_count: int = Field(0, description="指标数量")

    model_config = {"from_attributes": True}


class MetricProjectListResponse(BaseModel):
    """指标项目列表响应"""
    items: List[MetricProjectResponse] = Field(..., description="项目列表")
    total: int = Field(..., description="总数")


class MetricProjectReorderRequest(BaseModel):
    """重新排序项目请求"""
    project_ids: List[int] = Field(..., description="按新顺序排列的项目ID列表", min_length=1)
