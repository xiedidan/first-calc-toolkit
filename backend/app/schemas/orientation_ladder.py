"""
导向阶梯相关的Schema
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator


class OrientationLadderBase(BaseModel):
    """导向阶梯基础Schema"""
    rule_id: int = Field(..., description="导向规则ID")
    ladder_order: int = Field(..., ge=1, description="阶梯次序")
    upper_limit: Optional[Decimal] = Field(None, description="阶梯上限（NULL表示正无穷）")
    lower_limit: Optional[Decimal] = Field(None, description="阶梯下限（NULL表示负无穷）")
    adjustment_intensity: Decimal = Field(..., description="调整力度")

    @field_validator('upper_limit', 'lower_limit', 'adjustment_intensity')
    @classmethod
    def validate_decimal_precision(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """验证并格式化数值为4位小数"""
        if v is None:
            return None
        # 四舍五入到4位小数
        return Decimal(str(round(float(v), 4)))

    @field_validator('ladder_order')
    @classmethod
    def validate_ladder_order(cls, v: int) -> int:
        """验证阶梯次序必须为正整数"""
        if v < 1:
            raise ValueError('阶梯次序必须为正整数')
        return v

    @model_validator(mode='after')
    def validate_limit_range(self):
        """验证阶梯下限必须小于阶梯上限（除非使用无穷值）"""
        if self.lower_limit is not None and self.upper_limit is not None:
            if self.lower_limit >= self.upper_limit:
                raise ValueError('阶梯下限必须小于阶梯上限')
        return self


class OrientationLadderCreate(OrientationLadderBase):
    """创建导向阶梯Schema"""
    pass


class OrientationLadderUpdate(BaseModel):
    """更新导向阶梯Schema"""
    rule_id: Optional[int] = Field(None, description="导向规则ID")
    ladder_order: Optional[int] = Field(None, ge=1, description="阶梯次序")
    upper_limit: Optional[Decimal] = Field(None, description="阶梯上限（NULL表示正无穷）")
    lower_limit: Optional[Decimal] = Field(None, description="阶梯下限（NULL表示负无穷）")
    adjustment_intensity: Optional[Decimal] = Field(None, description="调整力度")

    @field_validator('upper_limit', 'lower_limit', 'adjustment_intensity')
    @classmethod
    def validate_decimal_precision(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """验证并格式化数值为4位小数"""
        if v is None:
            return None
        # 四舍五入到4位小数
        return Decimal(str(round(float(v), 4)))

    @field_validator('ladder_order')
    @classmethod
    def validate_ladder_order(cls, v: Optional[int]) -> Optional[int]:
        """验证阶梯次序必须为正整数"""
        if v is not None and v < 1:
            raise ValueError('阶梯次序必须为正整数')
        return v

    @model_validator(mode='after')
    def validate_limit_range(self):
        """验证阶梯下限必须小于阶梯上限（除非使用无穷值）"""
        if self.lower_limit is not None and self.upper_limit is not None:
            if self.lower_limit >= self.upper_limit:
                raise ValueError('阶梯下限必须小于阶梯上限')
        return self


class OrientationLadder(OrientationLadderBase):
    """导向阶梯Schema"""
    id: int
    hospital_id: int
    created_at: datetime
    updated_at: datetime
    # 预加载字段
    rule_name: Optional[str] = Field(None, description="导向规则名称")

    class Config:
        from_attributes = True


class OrientationLadderList(BaseModel):
    """导向阶梯列表Schema"""
    total: int
    items: list[OrientationLadder]
