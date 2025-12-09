"""
成本基准相关的Schema
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class CostBenchmarkBase(BaseModel):
    """成本基准基础Schema"""
    department_code: str = Field(..., min_length=1, max_length=50, description="科室代码")
    department_name: str = Field(..., min_length=1, max_length=100, description="科室名称")
    version_id: int = Field(..., gt=0, description="模型版本ID")
    version_name: str = Field(..., min_length=1, max_length=100, description="模型版本名称")
    dimension_code: str = Field(..., min_length=1, max_length=100, description="维度代码")
    dimension_name: str = Field(..., min_length=1, max_length=200, description="维度名称")
    benchmark_value: Decimal = Field(..., gt=0, description="基准值（必须大于0）")

    @field_validator('benchmark_value')
    @classmethod
    def validate_benchmark_value(cls, v: Decimal) -> Decimal:
        """验证基准值必须大于0，并格式化为2位小数"""
        if v is None:
            raise ValueError('基准值不能为空')
        if v <= 0:
            raise ValueError('基准值必须大于0')
        # 四舍五入到2位小数
        return Decimal(str(round(float(v), 2)))

    @field_validator('department_code', 'department_name', 'version_name', 'dimension_code', 'dimension_name')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """验证字符串不能为空"""
        if not v or not v.strip():
            raise ValueError('字段不能为空')
        return v.strip()


class CostBenchmarkCreate(CostBenchmarkBase):
    """创建成本基准Schema"""
    pass


class CostBenchmarkUpdate(BaseModel):
    """更新成本基准Schema"""
    department_code: Optional[str] = Field(None, min_length=1, max_length=50, description="科室代码")
    department_name: Optional[str] = Field(None, min_length=1, max_length=100, description="科室名称")
    version_id: Optional[int] = Field(None, gt=0, description="模型版本ID")
    version_name: Optional[str] = Field(None, min_length=1, max_length=100, description="模型版本名称")
    dimension_code: Optional[str] = Field(None, min_length=1, max_length=100, description="维度代码")
    dimension_name: Optional[str] = Field(None, min_length=1, max_length=200, description="维度名称")
    benchmark_value: Optional[Decimal] = Field(None, gt=0, description="基准值（必须大于0）")

    @field_validator('benchmark_value')
    @classmethod
    def validate_benchmark_value(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """验证基准值必须大于0，并格式化为2位小数"""
        if v is None:
            return None
        if v <= 0:
            raise ValueError('基准值必须大于0')
        # 四舍五入到2位小数
        return Decimal(str(round(float(v), 2)))

    @field_validator('department_code', 'department_name', 'version_name', 'dimension_code', 'dimension_name')
    @classmethod
    def validate_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """验证字符串不能为空"""
        if v is not None and (not v or not v.strip()):
            raise ValueError('字段不能为空')
        return v.strip() if v else None


class CostBenchmark(CostBenchmarkBase):
    """成本基准Schema（响应模型）"""
    id: int
    hospital_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CostBenchmarkList(BaseModel):
    """成本基准列表Schema"""
    total: int
    items: list[CostBenchmark]
