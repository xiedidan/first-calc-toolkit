"""
成本报表相关的Schema
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class CostReportBase(BaseModel):
    """成本报表基础Schema"""
    period: str = Field(..., description="年月，格式：YYYY-MM")
    department_code: str = Field(..., description="科室代码")
    department_name: str = Field(..., description="科室名称")
    personnel_cost: Decimal = Field(default=Decimal("0"), description="人员经费")
    material_cost: Decimal = Field(default=Decimal("0"), description="不收费卫生材料费")
    medicine_cost: Decimal = Field(default=Decimal("0"), description="不收费药品费")
    depreciation_cost: Decimal = Field(default=Decimal("0"), description="折旧风险费")
    other_cost: Decimal = Field(default=Decimal("0"), description="其他费用")


class CostReportCreate(CostReportBase):
    """创建成本报表Schema"""
    pass


class CostReportUpdate(BaseModel):
    """更新成本报表Schema"""
    period: Optional[str] = Field(None, description="年月")
    department_code: Optional[str] = Field(None, description="科室代码")
    department_name: Optional[str] = Field(None, description="科室名称")
    personnel_cost: Optional[Decimal] = Field(None, description="人员经费")
    material_cost: Optional[Decimal] = Field(None, description="不收费卫生材料费")
    medicine_cost: Optional[Decimal] = Field(None, description="不收费药品费")
    depreciation_cost: Optional[Decimal] = Field(None, description="折旧风险费")
    other_cost: Optional[Decimal] = Field(None, description="其他费用")


class CostReport(CostReportBase):
    """成本报表Schema"""
    id: int
    hospital_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CostReportList(BaseModel):
    """成本报表列表Schema"""
    total: int
    items: List[CostReport]


# 智能导入相关Schema

class CostReportImportParseResponse(BaseModel):
    """成本报表导入解析响应Schema"""
    session_id: str = Field(..., description="会话ID")
    sheet_names: List[str] = Field(..., description="所有Sheet名称列表")
    current_sheet: str = Field(..., description="当前选中的Sheet")
    headers: List[str] = Field(..., description="Excel表头列表")
    preview_data: List[List[str]] = Field(..., description="预览数据")
    total_rows: int = Field(..., description="总行数")
    skip_rows: int = Field(..., description="跳过的行数")
    header_row: int = Field(..., description="标题行位置")
    suggested_mapping: dict = Field(..., description="建议的字段映射")


class CostReportImportFieldMapping(BaseModel):
    """成本报表导入字段映射Schema"""
    session_id: str = Field(..., description="会话ID")
    field_mapping: dict = Field(..., description="字段映射")
    match_by: str = Field("code", description="匹配方式：code(按科室代码精确匹配) 或 name(按科室名称模糊匹配)")


class DepartmentMatch(BaseModel):
    """科室匹配Schema"""
    id: int
    code: str
    name: str
    score: float = Field(1.0, description="匹配得分")


class UniqueValueForMatch(BaseModel):
    """待匹配的唯一值Schema"""
    value: str = Field(..., description="Excel中的科室名称")
    count: int = Field(..., description="出现次数")
    suggested_departments: List[DepartmentMatch] = Field(..., description="建议匹配的科室")


class CostReportImportExtractResponse(BaseModel):
    """成本报表导入提取唯一值响应Schema"""
    unique_values: List[UniqueValueForMatch]
    system_departments: List[DepartmentMatch]


class DepartmentValueMapping(BaseModel):
    """科室值映射Schema"""
    value: str = Field(..., description="Excel中的科室名称")
    department_code: Optional[str] = Field(None, description="匹配的科室代码")


class CostReportImportPreviewRequest(BaseModel):
    """成本报表导入预览请求Schema"""
    session_id: str = Field(..., description="会话ID")
    value_mapping: List[DepartmentValueMapping] = Field(..., description="科室值映射")


class CostReportPreviewItem(BaseModel):
    """成本报表预览项Schema"""
    period: str
    department_code: str
    department_name: str
    excel_department_name: str = Field("", description="Excel中的科室名称")
    personnel_cost: Decimal = Field(default=Decimal("0"))
    material_cost: Decimal = Field(default=Decimal("0"))
    medicine_cost: Decimal = Field(default=Decimal("0"))
    depreciation_cost: Decimal = Field(default=Decimal("0"))
    other_cost: Decimal = Field(default=Decimal("0"))
    status: str = Field(..., description="状态：new(新增), update(覆盖), skip(跳过), error(错误)")
    message: str = Field("", description="提示信息")


class CostReportPreviewStatistics(BaseModel):
    """成本报表预览统计Schema"""
    total: int
    new_count: int = Field(..., description="新增数量")
    update_count: int = Field(..., description="覆盖数量")
    skip_count: int = Field(0, description="跳过数量")
    error_count: int = Field(..., description="错误数量")


class CostReportImportPreviewResponse(BaseModel):
    """成本报表导入预览响应Schema"""
    preview_items: List[CostReportPreviewItem]
    statistics: CostReportPreviewStatistics


class CostReportImportExecuteRequest(BaseModel):
    """成本报表导入执行请求Schema"""
    session_id: str = Field(..., description="会话ID")
    confirmed_items: Optional[List[CostReportPreviewItem]] = Field(None, description="用户确认的导入项")


class CostReportImportError(BaseModel):
    """成本报表导入错误Schema"""
    period: str
    department_code: str
    reason: str


class CostReportImportReport(BaseModel):
    """成本报表导入报告Schema"""
    success_count: int
    update_count: int
    skip_count: int = Field(0, description="跳过数量")
    error_count: int
    errors: List[CostReportImportError]


class CostReportImportExecuteResponse(BaseModel):
    """成本报表导入执行响应Schema"""
    success: bool
    report: CostReportImportReport
