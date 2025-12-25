"""
学科规则Schema
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class DisciplineRuleBase(BaseModel):
    """学科规则基础Schema"""
    department_code: str = Field(..., description="科室代码", max_length=50)
    department_name: str = Field(..., description="科室名称", max_length=100)
    version_id: int = Field(..., description="模型版本ID", gt=0)
    dimension_code: str = Field(..., description="维度代码", max_length=100)
    dimension_name: str = Field(..., description="维度名称", max_length=200)
    rule_description: Optional[str] = Field(None, description="规则描述", max_length=500)
    rule_coefficient: Decimal = Field(..., description="规则系数", ge=0, le=100)


class DisciplineRuleCreate(DisciplineRuleBase):
    """创建学科规则Schema"""
    pass


class DisciplineRuleUpdate(BaseModel):
    """更新学科规则Schema"""
    department_code: Optional[str] = Field(None, description="科室代码", max_length=50)
    department_name: Optional[str] = Field(None, description="科室名称", max_length=100)
    dimension_code: Optional[str] = Field(None, description="维度代码", max_length=100)
    dimension_name: Optional[str] = Field(None, description="维度名称", max_length=200)
    rule_description: Optional[str] = Field(None, description="规则描述", max_length=500)
    rule_coefficient: Optional[Decimal] = Field(None, description="规则系数", ge=0, le=100)


class DisciplineRuleResponse(DisciplineRuleBase):
    """学科规则响应Schema"""
    id: int
    version_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DisciplineRuleListResponse(BaseModel):
    """学科规则列表响应Schema"""
    items: List[DisciplineRuleResponse]
    total: int
