"""
导向规则相关的Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.models.orientation_rule import OrientationCategory


class OrientationRuleBase(BaseModel):
    """导向规则基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="导向名称")
    category: OrientationCategory = Field(..., description="导向类别")
    description: Optional[str] = Field(None, max_length=1024, description="导向规则描述")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证导向名称不能为空字符串"""
        if not v or not v.strip():
            raise ValueError('导向名称不能为空')
        return v.strip()


class OrientationRuleCreate(OrientationRuleBase):
    """创建导向规则Schema"""
    pass


class OrientationRuleUpdate(BaseModel):
    """更新导向规则Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="导向名称")
    category: Optional[OrientationCategory] = Field(None, description="导向类别")
    description: Optional[str] = Field(None, max_length=1024, description="导向规则描述")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """验证导向名称不能为空字符串"""
        if v is not None and (not v or not v.strip()):
            raise ValueError('导向名称不能为空')
        return v.strip() if v else None


class OrientationRule(OrientationRuleBase):
    """导向规则Schema"""
    id: int
    hospital_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrientationRuleList(BaseModel):
    """导向规则列表Schema"""
    total: int
    items: list[OrientationRule]
