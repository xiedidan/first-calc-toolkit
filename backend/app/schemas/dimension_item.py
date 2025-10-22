"""
维度目录相关的Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ChargeItemBase(BaseModel):
    """收费项目基础Schema"""
    item_code: str = Field(..., description="收费项目编码")
    item_name: str = Field(..., description="收费项目名称")
    item_category: Optional[str] = Field(None, description="收费项目分类")
    unit_price: Optional[str] = Field(None, description="单价")


class ChargeItemCreate(ChargeItemBase):
    """创建收费项目Schema"""
    pass


class ChargeItemUpdate(BaseModel):
    """更新收费项目Schema"""
    item_name: Optional[str] = Field(None, description="收费项目名称")
    item_category: Optional[str] = Field(None, description="收费项目分类")
    unit_price: Optional[str] = Field(None, description="单价")


class ChargeItem(ChargeItemBase):
    """收费项目Schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChargeItemList(BaseModel):
    """收费项目列表Schema"""
    total: int
    items: list[ChargeItem]


class DimensionItemMappingBase(BaseModel):
    """维度-收费项目映射基础Schema"""
    dimension_id: int = Field(..., description="维度节点ID")
    item_code: str = Field(..., description="收费项目编码")


class DimensionItemMappingCreate(BaseModel):
    """创建维度-收费项目映射Schema"""
    dimension_id: int = Field(..., description="维度节点ID")
    item_codes: list[str] = Field(..., description="收费项目编码列表")


class DimensionItemMapping(DimensionItemMappingBase):
    """维度-收费项目映射Schema"""
    id: int
    item_name: Optional[str] = None
    item_category: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DimensionItemList(BaseModel):
    """维度目录列表Schema"""
    total: int
    items: list[DimensionItemMapping]
