"""
指标相关的Pydantic模型 - 智能问数系统
具有业务含义的数据度量单位
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime


# 指标类型常量
METRIC_TYPES = ["atomic", "composite"]


class MetricCreate(BaseModel):
    """创建指标"""
    topic_id: int = Field(..., description="所属主题ID")
    name_cn: str = Field(..., description="中文名称", min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, description="英文名称", max_length=200)
    metric_type: str = Field("atomic", description="指标类型：atomic(原子指标)、composite(复合指标)")
    metric_level: Optional[str] = Field(None, description="指标层级", max_length=100)
    business_caliber: Optional[str] = Field(None, description="业务口径")
    technical_caliber: Optional[str] = Field(None, description="技术口径")
    source_tables: Optional[List[str]] = Field(None, description="源表列表")
    dimension_tables: Optional[List[str]] = Field(None, description="关联维表")
    dimensions: Optional[List[str]] = Field(None, description="指标维度")
    data_source_id: Optional[int] = Field(None, description="数据源ID")
    sort_order: int = Field(0, description="排序顺序", ge=0)

    @field_validator('metric_type')
    @classmethod
    def validate_metric_type(cls, v: str) -> str:
        """验证指标类型"""
        if v not in METRIC_TYPES:
            raise ValueError(f'指标类型必须是以下之一: {", ".join(METRIC_TYPES)}')
        return v


class MetricUpdate(BaseModel):
    """更新指标"""
    topic_id: Optional[int] = Field(None, description="所属主题ID")
    name_cn: Optional[str] = Field(None, description="中文名称", min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, description="英文名称", max_length=200)
    metric_type: Optional[str] = Field(None, description="指标类型")
    metric_level: Optional[str] = Field(None, description="指标层级", max_length=100)
    business_caliber: Optional[str] = Field(None, description="业务口径")
    technical_caliber: Optional[str] = Field(None, description="技术口径")
    source_tables: Optional[List[str]] = Field(None, description="源表列表")
    dimension_tables: Optional[List[str]] = Field(None, description="关联维表")
    dimensions: Optional[List[str]] = Field(None, description="指标维度")
    data_source_id: Optional[int] = Field(None, description="数据源ID")
    sort_order: Optional[int] = Field(None, description="排序顺序", ge=0)

    @field_validator('metric_type')
    @classmethod
    def validate_metric_type(cls, v: Optional[str]) -> Optional[str]:
        """验证指标类型"""
        if v is not None and v not in METRIC_TYPES:
            raise ValueError(f'指标类型必须是以下之一: {", ".join(METRIC_TYPES)}')
        return v



class MetricResponse(BaseModel):
    """指标响应"""
    id: int = Field(..., description="指标ID")
    topic_id: int = Field(..., description="所属主题ID")
    topic_name: Optional[str] = Field(None, description="所属主题名称")
    project_id: Optional[int] = Field(None, description="所属项目ID")
    project_name: Optional[str] = Field(None, description="所属项目名称")
    name_cn: str = Field(..., description="中文名称")
    name_en: Optional[str] = Field(None, description="英文名称")
    metric_type: str = Field(..., description="指标类型")
    metric_type_display: str = Field(..., description="指标类型显示名称")
    metric_level: Optional[str] = Field(None, description="指标层级")
    business_caliber: Optional[str] = Field(None, description="业务口径")
    technical_caliber: Optional[str] = Field(None, description="技术口径")
    source_tables: Optional[List[str]] = Field(None, description="源表列表")
    dimension_tables: Optional[List[str]] = Field(None, description="关联维表")
    dimensions: Optional[List[str]] = Field(None, description="指标维度")
    data_source_id: Optional[int] = Field(None, description="数据源ID")
    data_source_name: Optional[str] = Field(None, description="数据源名称")
    sort_order: int = Field(..., description="排序顺序")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    # 关联信息
    related_metric_count: int = Field(0, description="关联指标数量")

    model_config = {"from_attributes": True}


class MetricListResponse(BaseModel):
    """指标列表响应"""
    items: List[MetricResponse] = Field(..., description="指标列表")
    total: int = Field(..., description="总数")


class MetricTreeNodeResponse(BaseModel):
    """指标树节点响应（用于树形结构）"""
    id: int = Field(..., description="节点ID")
    name: str = Field(..., description="节点名称")
    node_type: str = Field(..., description="节点类型：project、topic、metric")
    sort_order: int = Field(..., description="排序顺序")
    # 项目特有字段
    description: Optional[str] = Field(None, description="描述")
    # 主题特有字段
    project_id: Optional[int] = Field(None, description="所属项目ID")
    # 指标特有字段
    topic_id: Optional[int] = Field(None, description="所属主题ID")
    metric_type: Optional[str] = Field(None, description="指标类型")
    metric_type_display: Optional[str] = Field(None, description="指标类型显示名称")
    # 子节点
    children: Optional[List["MetricTreeNodeResponse"]] = Field(None, description="子节点列表")

    model_config = {"from_attributes": True}


# 解决循环引用
MetricTreeNodeResponse.model_rebuild()


class MetricTreeResponse(BaseModel):
    """指标树响应"""
    items: List[MetricTreeNodeResponse] = Field(..., description="树形结构根节点列表")
    total_projects: int = Field(..., description="项目总数")
    total_topics: int = Field(..., description="主题总数")
    total_metrics: int = Field(..., description="指标总数")


class MetricSearchRequest(BaseModel):
    """指标搜索请求"""
    keyword: Optional[str] = Field(None, description="搜索关键词（匹配中文名称、英文名称、业务口径）")
    project_id: Optional[int] = Field(None, description="项目ID筛选")
    topic_id: Optional[int] = Field(None, description="主题ID筛选")
    metric_type: Optional[str] = Field(None, description="指标类型筛选")
    page: int = Field(1, description="页码", ge=1)
    size: int = Field(20, description="每页数量", ge=1, le=100)


class MetricReorderRequest(BaseModel):
    """重新排序指标请求"""
    topic_id: int = Field(..., description="主题ID")
    metric_ids: List[int] = Field(..., description="按新顺序排列的指标ID列表", min_length=1)
