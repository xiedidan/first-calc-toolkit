"""
导向基准相关的Schema
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator
from app.models.orientation_benchmark import BenchmarkType


class OrientationBenchmarkBase(BaseModel):
    """导向基准基础Schema"""
    rule_id: int = Field(..., description="导向规则ID")
    department_code: str = Field(..., min_length=1, max_length=50, description="科室代码")
    department_name: str = Field(..., min_length=1, max_length=100, description="科室名称")
    benchmark_type: BenchmarkType = Field(..., description="基准类别")
    control_intensity: Decimal = Field(..., description="管控力度")
    stat_start_date: datetime = Field(..., description="统计开始时间")
    stat_end_date: datetime = Field(..., description="统计结束时间")
    benchmark_value: Decimal = Field(..., description="基准值")

    @field_validator('control_intensity', 'benchmark_value')
    @classmethod
    def validate_decimal_precision(cls, v: Decimal) -> Decimal:
        """验证并格式化数值为4位小数"""
        if v is None:
            raise ValueError('数值不能为空')
        # 四舍五入到4位小数
        return Decimal(str(round(float(v), 4)))

    @field_validator('department_code', 'department_name')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """验证字符串不能为空"""
        if not v or not v.strip():
            raise ValueError('字段不能为空')
        return v.strip()

    @model_validator(mode='after')
    def validate_date_range(self):
        """验证统计开始时间必须早于统计结束时间"""
        if self.stat_start_date >= self.stat_end_date:
            raise ValueError('统计开始时间必须早于统计结束时间')
        return self


class OrientationBenchmarkCreate(OrientationBenchmarkBase):
    """创建导向基准Schema"""
    pass


class OrientationBenchmarkUpdate(BaseModel):
    """更新导向基准Schema"""
    rule_id: Optional[int] = Field(None, description="导向规则ID")
    department_code: Optional[str] = Field(None, min_length=1, max_length=50, description="科室代码")
    department_name: Optional[str] = Field(None, min_length=1, max_length=100, description="科室名称")
    benchmark_type: Optional[BenchmarkType] = Field(None, description="基准类别")
    control_intensity: Optional[Decimal] = Field(None, description="管控力度")
    stat_start_date: Optional[datetime] = Field(None, description="统计开始时间")
    stat_end_date: Optional[datetime] = Field(None, description="统计结束时间")
    benchmark_value: Optional[Decimal] = Field(None, description="基准值")

    @field_validator('control_intensity', 'benchmark_value')
    @classmethod
    def validate_decimal_precision(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """验证并格式化数值为4位小数"""
        if v is None:
            return None
        # 四舍五入到4位小数
        return Decimal(str(round(float(v), 4)))

    @field_validator('department_code', 'department_name')
    @classmethod
    def validate_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """验证字符串不能为空"""
        if v is not None and (not v or not v.strip()):
            raise ValueError('字段不能为空')
        return v.strip() if v else None

    @model_validator(mode='after')
    def validate_date_range(self):
        """验证统计开始时间必须早于统计结束时间"""
        if self.stat_start_date is not None and self.stat_end_date is not None:
            if self.stat_start_date >= self.stat_end_date:
                raise ValueError('统计开始时间必须早于统计结束时间')
        return self


class OrientationBenchmark(OrientationBenchmarkBase):
    """导向基准Schema"""
    id: int
    hospital_id: int
    created_at: datetime
    updated_at: datetime
    # 预加载字段
    rule_name: Optional[str] = Field(None, description="导向规则名称")

    class Config:
        from_attributes = True


class OrientationBenchmarkList(BaseModel):
    """导向基准列表Schema"""
    total: int
    items: list[OrientationBenchmark]
