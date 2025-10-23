"""
模型节点Schema
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class ModelNodeBase(BaseModel):
    """模型节点基础Schema"""
    name: str = Field(..., description="节点名称")
    code: str = Field(..., description="节点编码")
    node_type: str = Field(..., description="节点类型(sequence/dimension)")
    sort_order: Optional[Decimal] = Field(0, description="排序序号")
    is_leaf: bool = Field(False, description="是否为末级维度")
    calc_type: Optional[str] = Field(None, description="算法类型(statistical=指标/calculational=目录)")
    weight: Optional[Decimal] = Field(None, description="权重/单价")
    unit: Optional[str] = Field('%', description="单位")
    business_guide: Optional[str] = Field(None, description="业务导向")
    script: Optional[str] = Field(None, description="SQL/Python脚本")


class ModelNodeCreate(ModelNodeBase):
    """创建模型节点Schema"""
    version_id: int = Field(..., description="模型版本ID")
    parent_id: Optional[int] = Field(None, description="父节点ID")


class ModelNodeUpdate(BaseModel):
    """更新模型节点Schema"""
    name: Optional[str] = Field(None, description="节点名称")
    code: Optional[str] = Field(None, description="节点编码")
    node_type: Optional[str] = Field(None, description="节点类型")
    sort_order: Optional[Decimal] = Field(None, description="排序序号")
    is_leaf: Optional[bool] = Field(None, description="是否为末级维度")
    calc_type: Optional[str] = Field(None, description="算法类型")
    weight: Optional[Decimal] = Field(None, description="权重/单价")
    unit: Optional[str] = Field(None, description="单位")
    business_guide: Optional[str] = Field(None, description="业务导向")
    script: Optional[str] = Field(None, description="SQL/Python脚本")


class ModelNodeResponse(ModelNodeBase):
    """模型节点响应Schema"""
    id: int
    version_id: int
    parent_id: Optional[int]
    sort_order: Decimal
    is_leaf: bool
    created_at: datetime
    updated_at: datetime
    children: list["ModelNodeResponse"] = []
    has_children: bool = False  # 是否有子节点

    class Config:
        from_attributes = True


class ModelNodeListResponse(BaseModel):
    """模型节点列表响应Schema"""
    total: int
    items: list[ModelNodeResponse]


class TestCodeRequest(BaseModel):
    """测试代码请求Schema"""
    script: str = Field(..., description="SQL/Python脚本")
    test_params: Optional[dict] = Field(None, description="测试参数")


class TestCodeResponse(BaseModel):
    """测试代码响应Schema"""
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


# 解决循环引用
ModelNodeResponse.model_rebuild()
