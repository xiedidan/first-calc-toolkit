"""
科室相关的Schema
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class DepartmentBase(BaseModel):
    """科室基础Schema"""
    his_code: str = Field(..., description="HIS科室代码")
    his_name: str = Field(..., description="HIS科室名称")
    sort_order: Optional[Decimal] = Field(None, description="排序序号")
    cost_center_code: Optional[str] = Field(None, description="成本中心代码")
    cost_center_name: Optional[str] = Field(None, description="成本中心名称")
    accounting_unit_code: Optional[str] = Field(None, description="核算单元代码")
    accounting_unit_name: Optional[str] = Field(None, description="核算单元名称")
    is_active: bool = Field(True, description="是否参与评估")


class DepartmentCreate(DepartmentBase):
    """创建科室Schema"""
    pass


class DepartmentUpdate(BaseModel):
    """更新科室Schema"""
    his_name: Optional[str] = Field(None, description="HIS科室名称")
    sort_order: Optional[Decimal] = Field(None, description="排序序号")
    cost_center_code: Optional[str] = Field(None, description="成本中心代码")
    cost_center_name: Optional[str] = Field(None, description="成本中心名称")
    accounting_unit_code: Optional[str] = Field(None, description="核算单元代码")
    accounting_unit_name: Optional[str] = Field(None, description="核算单元名称")


class Department(DepartmentBase):
    """科室Schema"""
    id: int
    sort_order: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DepartmentList(BaseModel):
    """科室列表Schema"""
    total: int
    items: list[Department]
