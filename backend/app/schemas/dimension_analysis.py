"""
维度分析 Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DimensionAnalysisBase(BaseModel):
    """维度分析基础 Schema"""
    content: str = Field(..., description="分析内容", min_length=1)


class DimensionAnalysisCreate(DimensionAnalysisBase):
    """创建维度分析"""
    department_id: int = Field(..., description="科室ID")
    node_id: int = Field(..., description="维度节点ID")
    period: Optional[str] = Field(None, description="统计月份(YYYY-MM)，NULL表示长期分析")


class DimensionAnalysisUpdate(BaseModel):
    """更新维度分析"""
    content: str = Field(..., description="分析内容", min_length=1)


class DimensionAnalysisResponse(DimensionAnalysisBase):
    """维度分析响应"""
    id: int
    hospital_id: int
    department_id: int
    node_id: int
    period: Optional[str] = None
    
    # 关联信息
    department_name: Optional[str] = None
    node_name: Optional[str] = None
    
    # 审计信息
    created_by: Optional[int] = None
    created_by_name: Optional[str] = None
    updated_by: Optional[int] = None
    updated_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DimensionAnalysisQuery(BaseModel):
    """查询维度分析"""
    department_id: int = Field(..., description="科室ID")
    node_id: int = Field(..., description="维度节点ID")
    period: Optional[str] = Field(None, description="统计月份(YYYY-MM)，NULL表示长期分析")


class DimensionAnalysisBatchQuery(BaseModel):
    """批量查询维度分析"""
    department_id: int = Field(..., description="科室ID")
    node_ids: list[int] = Field(..., description="维度节点ID列表")
    period: Optional[str] = Field(None, description="统计月份(YYYY-MM)")


class DimensionAnalysisBatchResponse(BaseModel):
    """批量查询响应"""
    # key: "{node_id}_{period}" 或 "{node_id}_long_term"
    current_analyses: dict[str, DimensionAnalysisResponse] = Field(default_factory=dict, description="当期分析")
    long_term_analyses: dict[str, DimensionAnalysisResponse] = Field(default_factory=dict, description="长期分析")
