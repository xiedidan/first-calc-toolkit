"""
指标主题相关的Pydantic模型 - 智能问数系统
项目下的一级分类，用于归类指标
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MetricTopicCreate(BaseModel):
    """创建指标主题"""
    project_id: int = Field(..., description="所属项目ID")
    name: str = Field(..., description="主题名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="主题描述", max_length=500)
    sort_order: int = Field(0, description="排序顺序", ge=0)


class MetricTopicUpdate(BaseModel):
    """更新指标主题"""
    project_id: Optional[int] = Field(None, description="所属项目ID")
    name: Optional[str] = Field(None, description="主题名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="主题描述", max_length=500)
    sort_order: Optional[int] = Field(None, description="排序顺序", ge=0)


class MetricTopicResponse(BaseModel):
    """指标主题响应"""
    id: int = Field(..., description="主题ID")
    project_id: int = Field(..., description="所属项目ID")
    project_name: Optional[str] = Field(None, description="所属项目名称")
    name: str = Field(..., description="主题名称")
    description: Optional[str] = Field(None, description="主题描述")
    sort_order: int = Field(..., description="排序顺序")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    # 统计信息
    metric_count: int = Field(0, description="指标数量")

    model_config = {"from_attributes": True}


class MetricTopicListResponse(BaseModel):
    """指标主题列表响应"""
    items: List[MetricTopicResponse] = Field(..., description="主题列表")
    total: int = Field(..., description="总数")


class MetricTopicReorderRequest(BaseModel):
    """重新排序主题请求"""
    topic_ids: List[int] = Field(..., description="按新顺序排列的主题ID列表", min_length=1)
