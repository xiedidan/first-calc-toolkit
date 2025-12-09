"""
科室运营分析报告相关的Schema
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class AnalysisReportBase(BaseModel):
    """分析报告基础Schema"""
    department_id: int = Field(..., description="科室ID")
    period: str = Field(..., description="年月 (YYYY-MM格式)")
    current_issues: Optional[str] = Field(None, max_length=2000, description="当前存在问题 (Markdown格式，最大2000字符)")
    future_plans: Optional[str] = Field(None, max_length=2000, description="未来发展计划 (Markdown格式，最大2000字符)")

    @field_validator('period')
    @classmethod
    def validate_period(cls, v: str) -> str:
        """验证年月格式"""
        import re
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('年月格式必须为 YYYY-MM')
        return v

    @field_validator('current_issues', 'future_plans')
    @classmethod
    def validate_content_length(cls, v: Optional[str]) -> Optional[str]:
        """验证内容长度不超过2000字符"""
        if v is not None and len(v) > 2000:
            raise ValueError('内容长度不能超过2000字符')
        return v


class AnalysisReportCreate(AnalysisReportBase):
    """创建分析报告Schema"""
    pass


class AnalysisReportUpdate(BaseModel):
    """更新分析报告Schema"""
    current_issues: Optional[str] = Field(None, max_length=2000, description="当前存在问题 (Markdown格式，最大2000字符)")
    future_plans: Optional[str] = Field(None, max_length=2000, description="未来发展计划 (Markdown格式，最大2000字符)")

    @field_validator('current_issues', 'future_plans')
    @classmethod
    def validate_content_length(cls, v: Optional[str]) -> Optional[str]:
        """验证内容长度不超过2000字符"""
        if v is not None and len(v) > 2000:
            raise ValueError('内容长度不能超过2000字符')
        return v


class AnalysisReport(AnalysisReportBase):
    """分析报告Schema"""
    id: int
    hospital_id: int
    department_code: str = Field(..., description="科室代码")
    department_name: str = Field(..., description="科室名称")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class AnalysisReportList(BaseModel):
    """分析报告列表Schema"""
    total: int
    items: List[AnalysisReport]


class ValueDistributionItem(BaseModel):
    """科室主业价值分布项"""
    rank: int = Field(..., description="排名")
    node_id: int = Field(..., description="节点ID")
    dimension_name: str = Field(..., description="维度名称")
    value: Decimal = Field(..., description="业务价值")
    workload: Decimal = Field(..., description="工作量金额（收入）")


class BusinessContentItem(BaseModel):
    """科室业务内涵项（单个项目）"""
    item_code: str = Field(..., description="项目编码")
    item_name: str = Field(..., description="项目名称")
    item_category: Optional[str] = Field(None, description="项目类别")
    unit_price: Optional[str] = Field(None, description="单价")
    amount: Decimal = Field(..., description="金额（收入）")
    quantity: Decimal = Field(..., description="数量")


class DimensionBusinessContent(BaseModel):
    """按维度分组的业务内涵"""
    dimension_name: str = Field(..., description="维度名称（完整路径）")
    items: List[BusinessContentItem] = Field(..., description="该维度下的收入Top5项目")


class ValueDistributionResponse(BaseModel):
    """科室主业价值分布响应"""
    items: List[ValueDistributionItem]
    total_value: Decimal = Field(..., description="总业务价值")
    message: Optional[str] = Field(None, description="提示信息")


class BusinessContentResponse(BaseModel):
    """科室业务内涵响应（按维度分组）"""
    dimensions: List[DimensionBusinessContent] = Field(..., description="按维度分组的业务内涵列表")
    message: Optional[str] = Field(None, description="提示信息")


class DimensionDrillDownItem(BaseModel):
    """维度下钻明细项"""
    period: str = Field(..., description="年月")
    department_code: str = Field(..., description="科室代码")
    department_name: str = Field(..., description="科室名称")
    item_code: str = Field(..., description="项目编码")
    item_name: str = Field(..., description="项目名称")
    item_category: Optional[str] = Field(None, description="项目类别")
    unit_price: Optional[str] = Field(None, description="单价")
    amount: Decimal = Field(..., description="金额")
    quantity: Decimal = Field(..., description="数量")


class DimensionDrillDownResponse(BaseModel):
    """维度下钻响应"""
    dimension_name: str = Field(..., description="维度名称")
    items: List[DimensionDrillDownItem]
    total_amount: Decimal = Field(..., description="总金额")
    total_quantity: Decimal = Field(..., description="总数量")
    message: Optional[str] = Field(None, description="提示信息")
