"""
指标关联相关的Pydantic模型 - 智能问数系统
定义指标之间的关联关系，支持复合指标的计算和追溯
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime


# 关联类型常量
RELATION_TYPES = ["component", "derived", "related"]


class MetricRelationCreate(BaseModel):
    """创建指标关联"""
    target_metric_id: int = Field(..., description="目标指标ID")
    relation_type: str = Field("component", description="关联类型：component(组成)、derived(派生)、related(相关)")

    @field_validator('relation_type')
    @classmethod
    def validate_relation_type(cls, v: str) -> str:
        """验证关联类型"""
        if v not in RELATION_TYPES:
            raise ValueError(f'关联类型必须是以下之一: {", ".join(RELATION_TYPES)}')
        return v


class MetricRelationResponse(BaseModel):
    """指标关联响应"""
    id: int = Field(..., description="关联ID")
    source_metric_id: int = Field(..., description="源指标ID")
    source_metric_name: Optional[str] = Field(None, description="源指标名称")
    target_metric_id: int = Field(..., description="目标指标ID")
    target_metric_name: Optional[str] = Field(None, description="目标指标名称")
    relation_type: str = Field(..., description="关联类型")
    relation_type_display: str = Field(..., description="关联类型显示名称")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}


class MetricRelationListResponse(BaseModel):
    """指标关联列表响应"""
    items: List[MetricRelationResponse] = Field(..., description="关联列表")
    total: int = Field(..., description="总数")


class AffectedMetricResponse(BaseModel):
    """受影响的指标响应（用于删除前检查）"""
    id: int = Field(..., description="指标ID")
    name_cn: str = Field(..., description="指标中文名称")
    topic_name: Optional[str] = Field(None, description="所属主题名称")
    project_name: Optional[str] = Field(None, description="所属项目名称")
    relation_type: str = Field(..., description="关联类型")

    model_config = {"from_attributes": True}


class AffectedMetricsResponse(BaseModel):
    """受影响的指标列表响应"""
    items: List[AffectedMetricResponse] = Field(..., description="受影响的指标列表")
    total: int = Field(..., description="总数")
    can_delete: bool = Field(..., description="是否可以删除（无关联时为True）")
