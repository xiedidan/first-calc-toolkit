"""内含式收费Schema"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class DimInclusiveFeeBase(BaseModel):
    """内含式收费基础Schema"""
    item_code: str = Field(..., max_length=255, description="收费项目代码")
    item_name: Optional[str] = Field(None, max_length=255, description="收费项目名称")
    cost: Decimal = Field(..., ge=0, description="单位成本")


class DimInclusiveFeeCreate(DimInclusiveFeeBase):
    """创建内含式收费"""
    pass


class DimInclusiveFeeUpdate(BaseModel):
    """更新内含式收费"""
    item_code: Optional[str] = Field(None, max_length=255, description="收费项目代码")
    item_name: Optional[str] = Field(None, max_length=255, description="收费项目名称")
    cost: Optional[Decimal] = Field(None, ge=0, description="单位成本")


class DimInclusiveFeeResponse(DimInclusiveFeeBase):
    """内含式收费响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DimInclusiveFeeListResponse(BaseModel):
    """内含式收费列表响应"""
    items: List[DimInclusiveFeeResponse]
    total: int
    page: int
    size: int
